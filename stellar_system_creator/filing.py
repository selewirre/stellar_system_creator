import gc
import inspect
import json
import os
import pickle
import shutil
import uuid
import zipfile
from pprint import pprint
from typing import Union, Dict, List
from zipfile import ZipFile

import blosc
import _pickle as cPickle
# https://stackoverflow.com/questions/57983431/whats-the-most-space-efficient-way-to-compress-serialized-python-data
import numpy as np
import pkg_resources
from PIL import Image
from fpdf import FPDF

from stellar_system_creator.astrothings.insolation_models.insolation_models import InsolationThresholdModel, \
    BinaryInsolationModel
from stellar_system_creator.astrothings.units import Q_
from stellar_system_creator.stellar_system_elements import *
from stellar_system_creator.stellar_system_elements.stellar_body import Ring
from stellar_system_creator.visualization import system_plot
from stellar_system_creator.visualization.drawing_tools import Color


def add_extension_if_necessary(filename, extension):
    if extension[0] != '.':
        extension = '.' + extension
    # finding if filename has ending same as extension and if not, it adds the extension ending to the file
    filename_ending = filename.split('.')[-1]
    if filename_ending != extension[1:]:
        filename = filename + extension

    return filename


def save(obj: Union[StellarBody, BinarySystem, PlanetarySystem, StellarSystem, MultiStellarSystemSType],
         filename: str) -> bool:
    """Saving object (can be any class) via pickling under filename with extension .scc"""
    supported_classes = [StellarBody, BinarySystem, PlanetarySystem, StellarSystem, MultiStellarSystemSType]

    if any([isinstance(obj, cl) for cl in supported_classes]):
        filename = add_extension_if_necessary(filename, 'ssc')
        pickled_data = cPickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)  # returns data as a bytes object
        compressed_pickle = blosc.compress(pickled_data)
        with open(filename, 'wb') as file:
            file.write(compressed_pickle)
            # pickle.dump(obj, file)
            # cPickle.dump(obj, file)
        return True
    else:
        print(f'Object class {obj.__class__} not supported... File {filename} was not saved...')
        return False


def load(filename: str) -> Union[StellarBody, BinarySystem, PlanetarySystem, StellarSystem, MultiStellarSystemSType]:
    """Loading scc pickled files"""
    # filename = add_extension_if_necessary(filename, 'ssc')

    with open(filename, "rb") as f:
        compressed_pickle = f.read()

    depressed_pickle = blosc.decompress(compressed_pickle)
    obj: Union[StellarBody, BinarySystem, PlanetarySystem, StellarSystem,
               MultiStellarSystemSType] = cPickle.loads(depressed_pickle)  # turn bytes object back into data

    if '_uuid' not in obj.__dict__.keys():
        temp_filename = os.path.join(os.path.dirname(filename), '.~'+os.path.basename(filename))
        save_as_ssc_light(obj, temp_filename)
        obj = load_ssc_light(temp_filename, set_new_uuids=True)
        os.remove(temp_filename)

    return obj


# TODO: check for suggested values before saving, and potentially change the value to its default!!
#  (in save_stellar_body and save_binary)
def save_as_ssc_light(obj: Union[StellarBody, BinarySystem, PlanetarySystem, StellarSystem, MultiStellarSystemSType],
                      filename: str, system_rendering_preferences: Union[Dict, None] = None):
    """
    Saving object extension with .sscl.
    It is a compressed folder of json files and non-default images.
    Each json file named <UUID>.json holds the input information of a file
    The file that points to the main system is always named ".allmother.json"
     and contains the <UUID> of the main system.
    """
    supported_classes = [StellarBody, BinarySystem, PlanetarySystem, StellarSystem, MultiStellarSystemSType]

    if any([isinstance(obj, cl) for cl in supported_classes]):
        # creating temp folder (will later be zipped)
        temp_folder = os.path.join(os.path.dirname(filename), '.~'+os.path.basename(filename.replace('.sscl', '')))
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        os.mkdir(temp_folder)

        # saving system and sub-systems
        save_object_to_json(obj, temp_folder, system_rendering_preferences)
        with open(os.path.join(temp_folder, f".allmother.json"), "w") as outfile:
            outfile.write(json.dumps({'allmother_uuid': obj._uuid}, indent=4))

        # get rid of old temp zip
        temp_zip_filename = f'{temp_folder}.sscl'
        if os.path.exists(temp_zip_filename):
            os.remove(temp_zip_filename)

        # zipping tempfolder
        with ZipFile(temp_zip_filename, 'w') as temp_zip_file:
            for f in os.listdir(temp_folder):
                temp_zip_file.write(os.path.join(temp_folder, f),  # file to be compressed
                                    os.path.basename(f))  # making sure there is no folder in

        # making temp zip permanent
        filename = add_extension_if_necessary(filename, 'sscl')
        if os.path.exists(temp_zip_filename):
            if os.path.exists(filename):
                os.replace(temp_zip_filename, filename)
            else:
                os.rename(temp_zip_filename, filename)

        # deleting temp folder now that we are done
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)

        return True

    else:
        print(f'Object class {obj.__class__} not supported... File {filename} was not saved...')
        return False


def save_system_to_json(obj: Union[PlanetarySystem, StellarSystem, MultiStellarSystemSType], target_folder: str,
                        system_rendering_preferences: Union[Dict, None] = None):
    parent = obj.parent
    save_object_to_json(parent, target_folder)

    children = obj.get_children()
    for child in children:
        save_object_to_json(child, target_folder)

    cls = obj.__class__
    arg_keys = inspect.getfullargspec(cls).args[1:]  # args for all args, [1:] to ignore 'self' arg
    kwargs = {'class': cls.__name__,
              'name': obj.name,
              'parent_uuid': obj.parent._uuid}
    for key in arg_keys:
        if key not in obj.__dict__:
            pass
        elif isinstance(obj.__dict__[key], list):
            kwargs[f'{key}_uuids'] = get_children_uuid_list(obj.__dict__[key])

    if "_uuid" not in obj.__dict__:
        obj._uuid = str(uuid.uuid4())
    obj_uuid = obj._uuid

    with open(os.path.join(target_folder, f"{obj_uuid}.json"), "w") as outfile:
        outfile.write(json.dumps(kwargs, indent=4))

    save_system_rendering_preferences(obj, target_folder, system_rendering_preferences)


def save_system_rendering_preferences(obj: Union[PlanetarySystem, StellarSystem, MultiStellarSystemSType],
                                      target_folder: str, system_rendering_preferences: Union[Dict, None] = None):

    if isinstance(obj, MultiStellarSystemSType):
        obj = obj.children[0] if obj.children[0].parent.mass >= obj.children[1].parent.mass else obj.children[1]
    if system_rendering_preferences is None:
        try:
            system_rendering_preferences = obj.system_plot.system_rendering_preferences
        except Exception:
            system_rendering_preferences = system_plot.default_system_rendering_preferences

    for key in system_plot.default_system_rendering_preferences.keys():
        if key not in system_rendering_preferences.keys():
            system_rendering_preferences[key] = system_plot.default_system_rendering_preferences[key]

    with open(os.path.join(target_folder, ".system_rendering_preferences.json"), "w") as outfile:
        outfile.write(json.dumps(system_rendering_preferences, indent=4))


def get_children_uuid_list(children: List[Union[StellarBody, BinarySystem, PlanetarySystem, StellarSystem]]):
    return [child._uuid for child in children]


def save_object_to_json(obj: Union[StellarBody, BinarySystem], target_folder: str,
                        system_rendering_preferences: Union[Dict, None] = None):
    if isinstance(obj, StellarBody):
        save_stellar_body_to_json(obj, target_folder)
    elif isinstance(obj, BinarySystem):
        save_binary_to_json(obj, target_folder)
    elif isinstance(obj, (PlanetarySystem, StellarSystem, MultiStellarSystemSType)):
        save_system_to_json(obj, target_folder, system_rendering_preferences)
    else:
        raise TypeError(f'Could not save {obj} because it is neither a stellar body nor a binary system.')


def save_stellar_body_to_json(obj: StellarBody, target_folder: str):
    if isinstance(obj, StellarBody):
        cls = obj.__class__
        arg_keys = inspect.getfullargspec(cls).args[1:]  # args for all args, [1:] to ignore 'self' arg

        kwargs = {'class': cls.__name__}
        for key in arg_keys:
            if key not in obj.__dict__:
                pass
            elif key == 'parent':
                if obj.parent is not None:
                    if "_uuid" not in obj.parent.__dict__:
                        obj.parent._uuid = str(uuid.uuid4())
                    kwargs['parent_uuid'] = obj.parent._uuid
            elif key == 'image_filename':
                image_filename = obj.image_filename
                if not (image_filename is None or image_filename.lower() == 'none' or image_filename == ''):
                    provider: pkg_resources.DefaultProvider = pkg_resources.get_provider('stellar_system_creator')
                    ssc_module_path = provider.module_path
                    module_visualization_files = list_files(ssc_module_path)
                    if image_filename not in module_visualization_files:
                        new_image_basename = os.path.basename(image_filename)
                        new_image_filename = os.path.join(target_folder, new_image_basename)
                        Image.fromarray(obj.image_array).save(new_image_filename)
                        kwargs[key] = new_image_basename
            elif key == 'has_ring':
                obj: Planet
                kwargs['has_ring'] = obj.has_ring
                if obj.has_ring:
                    ring_color_list = []
                    for gradient_color in obj.ring.ring_radial_gradient_colors:
                        ring_color_list.append(gradient_color.get_color('RGBA'))
                    kwargs['ring_radial_gradient_color'] = ring_color_list
            else:
                value = obj.__dict__[key]
                if isinstance(value, Q_):
                    value = str(f'Q_: {value}')
                kwargs[key] = value

        if "_uuid" not in obj.__dict__:
            obj._uuid = str(uuid.uuid4())
        obj_uuid = obj._uuid

        with open(os.path.join(target_folder, f"{obj_uuid}.json"), "w") as outfile:
            outfile.write(json.dumps(kwargs, indent=4))

    else:
        raise TypeError(f'Could not save {obj} because it is not a stellar body.')


def save_binary_to_json(obj: BinarySystem, target_folder: str):
    if isinstance(obj, BinarySystem):
        cls = obj.__class__
        arg_keys = inspect.getfullargspec(cls).args[1:]  # args for all args, [1:] to ignore 'self' arg

        kwargs = {'class': cls.__name__}
        for key in arg_keys:
            if key not in obj.__dict__:
                pass
            elif key in ['parent', 'primary_body', 'secondary_body']:
                if obj.__dict__[key] is not None:
                    if "_uuid" not in obj.__dict__[key].__dict__:
                        obj.__dict__[key]._uuid = str(uuid.uuid4())
                    kwargs[f'{key}_uuid'] = obj.__dict__[key]._uuid
            else:
                value = obj.__dict__[key]
                if isinstance(value, Q_):
                    value = str(f'Q_: {value}')
                kwargs[key] = value

        if "_uuid" not in obj.__dict__:
            obj._uuid = str(uuid.uuid4())
        obj_uuid = obj._uuid

        with open(os.path.join(target_folder, f"{obj_uuid}.json"), "w") as outfile:
            outfile.write(json.dumps(kwargs, indent=4))

        save_object_to_json(obj.primary_body, target_folder)
        save_object_to_json(obj.secondary_body, target_folder)
    else:
        raise TypeError(f'Could not save {obj} because it not a binary system.')


def load_ssc_light(filename: str, set_new_uuids=False) -> Union[StellarBody, BinarySystem,
                                                                PlanetarySystem, StellarSystem,
                                                                MultiStellarSystemSType]:

    allmother_filename = os.path.join(filename, '.allmother.json')
    kwargs = get_dict_from_json(allmother_filename)

    obj = get_object_from_kwargs_uuid(kwargs['allmother_uuid'], allmother_filename)

    if set_new_uuids:
        obj.reset_system_uuids()

    if isinstance(obj, (PlanetarySystem, StellarSystem, MultiStellarSystemSType)):
        obj.parent.update_children()
    else:
        obj.update_children()

    return obj


def load_system_rendering_preferences(filename: str) -> Dict:

    system_rendering_preferences_filename = os.path.join(filename, '.system_rendering_preferences.json')
    system_rendering_preferences = get_dict_from_json(system_rendering_preferences_filename)

    for key in system_plot.default_system_rendering_preferences.keys():
        if key not in system_rendering_preferences.keys():
            system_rendering_preferences[key] = system_plot.default_system_rendering_preferences[key]

    return system_rendering_preferences


def load_system_from_json(filename: str) -> Union[PlanetarySystem, StellarSystem, MultiStellarSystemSType]:
    kwargs = get_dict_from_json(filename)

    # get target class
    cls = get_target_class(kwargs.pop('class'))

    if 'parent_uuid' in kwargs.keys():
        kwargs['parent'] = get_object_from_kwargs_uuid(kwargs.pop('parent_uuid'), filename)

    keys_to_remove = []
    dict_to_add = {}

    for key in kwargs.keys():
        if key.endswith('_uuids'):
            keys_to_remove.append(key)
            dict_to_add[key[:-6]] = [get_object_from_kwargs_uuid(child_uuid, filename) for child_uuid in kwargs[key]]

    for key in keys_to_remove:
        kwargs.pop(key)
    kwargs.update(dict_to_add)

    system = cls(**kwargs)
    system._uuid = os.path.basename(filename).strip('.json')

    return system


def load_object_from_json(filename: str, attempt_loading_parent=True):
    directory = os.path.dirname(filename)
    file_exists = False
    if os.path.isfile(directory):
        with ZipFile(directory) as zip_file:
            if os.path.basename(filename) in zip_file.namelist():
                file_exists = True
    else:
        file_exists = os.path.exists(filename)

    obj = None
    if file_exists:
        kwargs = get_dict_from_json(filename)
        if 'Binary' in kwargs['class']:
            obj = load_binary_from_json(filename, attempt_loading_parent)
        elif 'System' in kwargs['class']:
            obj = load_system_from_json(filename)
        else:
            obj = load_stellar_body_from_json(filename, attempt_loading_parent)

    return obj


def load_stellar_body_from_json(filename: str, attempt_loading_parent=True) \
        -> Union[StellarBody, Star, MainSequenceStar, BlackHole, Planet, AsteroidBelt, Satellite, Trojan, TrojanSatellite]:
    kwargs = get_dict_from_json(filename)

    # get target class
    cls = get_target_class(kwargs.pop('class'))

    if attempt_loading_parent:
        if 'parent_uuid' in kwargs.keys():
            kwargs['parent'] = get_object_from_kwargs_uuid(kwargs.pop('parent_uuid'), filename)
    else:
        kwargs.pop('parent_uuid')

    # getting the ring
    ring_radial_gradient_color = None
    if 'has_ring' in kwargs.keys():
        if kwargs['has_ring']:
            ring_radial_gradient_color = kwargs.pop('ring_radial_gradient_color')

    # getting proper values for all quantities
    kwargs = load_quantities_from_string_in_dict(kwargs)
    if 'image_filename' in kwargs:
        kwargs['image_filename'] = os.path.join(os.path.dirname(filename), kwargs['image_filename'])

    stellar_body = cls(**kwargs)
    stellar_body._uuid = os.path.basename(filename).strip('.json')
    if ring_radial_gradient_color is not None:
        stellar_body.ring.change_ring_radial_gradient_colors(ring_radial_gradient_color)

    return stellar_body


def load_binary_from_json(filename: str, attempt_loading_parent=True) -> Union[BinarySystem, StellarBinary]:
    kwargs = get_dict_from_json(filename)
    # get target class
    cls = get_target_class(kwargs.pop('class'))

    if 'primary_body_uuid' in kwargs.keys():
        kwargs['primary_body'] = get_object_from_kwargs_uuid(kwargs.pop('primary_body_uuid'), filename,
                                                             attempt_loading_parent=False)

    if 'secondary_body_uuid' in kwargs.keys():
        kwargs['secondary_body'] = get_object_from_kwargs_uuid(kwargs.pop('secondary_body_uuid'), filename,
                                                               attempt_loading_parent=False)

    if attempt_loading_parent:
        if 'parent_uuid' in kwargs.keys():
            kwargs['parent'] = get_object_from_kwargs_uuid(kwargs.pop('parent_uuid'), filename)
    else:
        kwargs.pop('parent_uuid')

    # getting proper values for all quantities
    kwargs = load_quantities_from_string_in_dict(kwargs)

    binary = cls(**kwargs)
    binary._uuid = os.path.basename(filename).strip('.json')

    return binary


def load_quantities_from_string_in_dict(dictionary: Dict):
    for key in dictionary.keys():
        value = dictionary[key]
        if isinstance(value, str):
            if value.startswith('Q_: '):
                value = value.strip('Q_: ')
                if value.startswith('nan'):
                    value = Q_(np.nan, value.strip('nan'))
                else:
                    value = Q_(value)
                dictionary[key] = value

    return dictionary


def get_object_from_kwargs_uuid(obj_uuid: str, requesters_filename: str, attempt_loading_parent=True):
    # try to find object in the current instance objects (this should always work if called from other function,
    # not directly)
    obj = find_obj_by_uuid_in_instance(obj_uuid, (StellarBody, BinarySystem)
                                       + tuple(StellarBody.__subclasses__()) + tuple(BinarySystem.__subclasses__())
                                       + tuple(Planet.__subclasses__()))

    # if it doesn't work, attempt to load file
    if obj is None:
        potential_parent_name = os.path.join(os.path.dirname(requesters_filename), f"{obj_uuid}.json")
        obj = load_object_from_json(potential_parent_name, attempt_loading_parent)

    return obj


def get_target_class(class_name: str):
    try:
        cls = globals()[class_name]
    except KeyError:
        raise ValueError(f'Could not find class {class_name}.')

    return cls


def get_dict_from_json(filename: str):
    directory = os.path.dirname(filename)
    if not zipfile.is_zipfile(directory):
        with open(filename, 'r') as file:
            obj: dict = json.load(file)
    else:
        with ZipFile(directory) as archive:
            basename = os.path.basename(filename)
            with archive.open(basename) as file:
                obj: dict = json.load(file)

    return obj


def find_obj_by_uuid_in_instance(uuid_value: str, target_class):
    target_obj = None
    for obj in gc.get_objects():
        if isinstance(obj, target_class):
            if obj._uuid == uuid_value:
                target_obj = obj

    return target_obj


def list_files(directory):
    r = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            r.append(os.path.join(root, name))
    return r


def export_object_to_json(obj: Union[StellarBody, BinarySystem, PlanetarySystem,
                                     StellarSystem, MultiStellarSystemSType],
                          filename, precision: int = 4):
    exportable_dict_of_dicts = get_exportable_object(obj, precision)

    filename = add_extension_if_necessary(filename, 'json')
    with open(filename, "w") as outfile:
        outfile.write(json.dumps(exportable_dict_of_dicts, indent=4))


def get_exportable_object(obj, precision: int = 4, entry_level: str = '', part_of_multi_system=False):
    if entry_level == '':
        multi_dict_key = obj.name
    elif not isinstance(obj, StellarBody) and not (isinstance(obj, BinarySystem) and part_of_multi_system):
        multi_dict_key = f'{entry_level}.0: Summary'
        entry_level = f'{entry_level}.'
    else:
        return get_exportable_dict(obj, precision)
    exportable_multi_dict = {multi_dict_key: get_exportable_dict(obj, precision)}
    if isinstance(obj, (PlanetarySystem, StellarSystem, MultiStellarSystemSType)):
        parent_level = f'{entry_level}{1}'
        exportable_item = get_exportable_object(obj.parent, precision, parent_level,
                                                isinstance(obj, MultiStellarSystemSType))
        exportable_multi_dict[f'{parent_level}: {obj.parent.name}'] = exportable_item
        for i, child in enumerate(obj.get_children()):
            child_level = f'{entry_level}{i+2}'
            exportable_item = get_exportable_object(child, precision, child_level)
            exportable_multi_dict[f'{child_level}: {child.name}'] = exportable_item
    elif isinstance(obj, BinarySystem) and not part_of_multi_system:
        exportable_item = get_exportable_object(obj.primary_body, precision, f'{entry_level}{1}')
        exportable_multi_dict[f'{entry_level}{1}: {obj.primary_body.name}'] = exportable_item
        exportable_item = get_exportable_object(obj.secondary_body, precision, f'{entry_level}{2}')
        exportable_multi_dict[f'{entry_level}{2}: {obj.secondary_body.name}'] = exportable_item

    return exportable_multi_dict


def get_exportable_dict(obj, precision: int = 4):
    obj_dict = obj.__dict__
    output_dict = {}
    for key, item in obj_dict.items():
        if key == 'image_array' or key == 'system_plot':
            continue
        else:
            output_dict[key] = get_exportable_item(item, precision)

    return output_dict


def get_exportable_item(item, precision: int = 4):
    if isinstance(item, (StellarBody, BinarySystem, PlanetarySystem, StellarSystem, MultiStellarSystemSType)):
        return item.name, item.uuid
    elif isinstance(item, (InsolationThresholdModel, BinaryInsolationModel)):
        return item.name
    elif isinstance(item, Ring):
        return get_exportable_item(item.__dict__, precision)
    elif isinstance(item, Color):
        return item.get_color('RGBA')
    elif isinstance(item, bool):
        return item
    elif isinstance(item, (int, float)):
        return f'{item:.{precision}g}'
    elif isinstance(item, Q_):
        return f'{item:.{precision}g}'
    elif isinstance(item, list):
        return [get_exportable_item(it, precision) for it in item]
    elif isinstance(item, dict):
        return {key: get_exportable_item(item[key], precision) for key in item.keys()}
    else:
        return item


class MyPDF(FPDF):
    # https://pyfpdf.github.io/fpdf2/Tutorial.html
    BASE_TEXT_SIZE = 14
    BASE_TEXT_HEIGHT = 6

    def __init__(self, dict_info: Dict):
        self.dict_info = dict_info
        self.title = list(dict_info.keys())[0]
        self.section_links = {}
        self.header_exception_pages = [1, 2]
        super().__init__(format='letter')
        self.set_document()

    def header(self):
        if self.page in self.header_exception_pages:
            return
        self.set_text_color(0, 0, 0)
        self.set_font("helvetica", "B", 15)  # Setting font: helvetica bold 15
        width = self.get_string_width(self.title) + 6  # Calculating width of title and setting cursor position:
        self.set_x((210 - width) / 2)
        self.cell(width, 9, self.title, 0, 1, "C")
        self.ln(10)

    def footer(self):
        if self.page in self.header_exception_pages:
            return
        self.set_y(-15)  # Setting position at 1.5 cm from bottom
        self.set_font("helvetica", "I", 8)  # Setting font: helvetica italic 8
        self.set_text_color(128)  # Setting text color to gray
        prev_y = self.y
        self.cell(0, 10, 'Powered by "Caelian Assistants: Stellar System Creator"', 0, 0, "L")  # Printing page number
        self.set_y(prev_y)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "R")  # Printing page number

    def set_document(self):
        self.set_title_page()
        self.add_page()
        self.set_contents_page()
        self.set_all_sections()

    def set_title_page(self):
        self.add_page()
        self.set_text_color(0, 0, 0)
        self.set_font("helvetica", "B", 30)
        self.set_x(self.w/2)
        self.set_y(self.h/4)
        self.cell(0, 9, self.title, 0, 1, "C")
        self.ln(10)
        self.set_font("helvetica", "", 13)
        self.set_y(3*self.h / 4)
        self.cell(0, self.BASE_TEXT_HEIGHT, 'Powered by', 0, 1, "C")
        self.set_font("helvetica", "i", 13)
        self.cell(0, self.BASE_TEXT_HEIGHT, 'Caelian Assistants: Stellar System Creator', 0, 1, "C")
        self.add_page()

    def set_contents_page(self):
        self.set_font("helvetica", "b", 25)
        self.cell(0, int(self.BASE_TEXT_HEIGHT * 1.5), 'Contents', 0, 1, "L")
        self.ln()
        self.set_zero_section_content_item()
        self.set_content_item(self.dict_info)
        # self.header_exception_pages.append(self.page + 1)

    def set_zero_section_content_item(self):
        self.set_font("helvetica", "", self.BASE_TEXT_SIZE)
        self.set_text_color(40, 20, 140)
        title_for_display = 'About System'
        self.section_links['About System'] = self.add_link()
        self.cell(0, int(self.BASE_TEXT_HEIGHT*1.5), title_for_display, 0, 1, "L", link=self.section_links['About System'])
        self.set_text_color(0, 0, 0)

    def set_content_item(self, dictionary, level=0):
        for key, item in dictionary.items():
            if is_numeral(key[0]):
                self.set_font("helvetica", "", self.BASE_TEXT_SIZE)
                self.set_text_color(40, 20, 140)
                title_for_display = level*'    ' + key.replace(':', '\t', 1)
                self.section_links[key] = self.add_link()
                self.cell(0, int(self.BASE_TEXT_HEIGHT*1.5), title_for_display, 0, 1, "L", link=self.section_links[key])
                self.set_content_item(item, level+1)
        self.set_text_color(0, 0, 0)

    def set_all_sections(self):
        self.set_zero_section()
        self.get_dict_contents(self.dict_info)

    def set_zero_section(self):
        zero_section_key = list(self.dict_info.keys())[0]
        zero_section_item = self.dict_info[zero_section_key]
        self.set_section_title('About System')
        self.set_section_body(zero_section_item)

    def set_section_title(self, title: str):
        title_number: str = title.split(':')[0]
        level = title_number.count('.')
        if level == 0:
            self.add_page()
        title_font = int(22 - 2 * level)
        if title_font < self.BASE_TEXT_SIZE:
            title_font = self.BASE_TEXT_SIZE
        self.set_font("helvetica", "b", title_font)
        title_for_display = title.replace(':', '\t', 1)
        if title in self.section_links:
            self.set_link(self.section_links[title], self.y - self.BASE_TEXT_HEIGHT)
        self.cell(0, self.BASE_TEXT_HEIGHT, title_for_display, 0, 1, "L")
        self.ln(8 - level)

    def set_section_body(self, dictionary: Dict):
        exception_keys = ['semi_major_axis_distribution', 'radius_distribution', 'mass_distribution', 'has_ring',
                          'image_filename', 'size', 'name']
        has_variables = False
        for key, item in dictionary.items():
            if not is_numeral(key[0]) and key not in exception_keys:
                has_variables = True

        if not has_variables:
            return

        column_width_1 = 70
        column_width_2 = 0
        self.set_font("helvetica", "b", self.BASE_TEXT_SIZE)
        self.cell(column_width_1, self.BASE_TEXT_HEIGHT, 'Quantity')
        self.cell(column_width_2, self.BASE_TEXT_HEIGHT, 'Value')
        self.ln()
        self.ln()
        for key, item in dictionary.items():
            if not is_numeral(key[0]):
                if key in exception_keys or (key == 'ring' and not dictionary['has_ring']):
                    continue
                self.set_font("helvetica", "", self.BASE_TEXT_SIZE)
                self.cell(column_width_1, self.BASE_TEXT_HEIGHT, get_pdf_file_variable_name(key))
                self.multi_cell(column_width_2, self.BASE_TEXT_HEIGHT, get_pdf_file_value_string(item),
                                max_line_height=self.BASE_TEXT_SIZE)
                self.set_y(self.y - self.BASE_TEXT_HEIGHT)
                self.ln()
        self.ln(8)

    def get_dict_contents(self, dictionary: Dict):
        for key, item in dictionary.items():
            if is_numeral(key[0]):
                self.set_section_title(key)
                self.set_section_body(item)
                self.get_dict_contents(item)


def is_numeral(string: str):
    try:
        float(string)
        return True
    except ValueError:
        return False


def get_pdf_file_variable_name(key: str):
    if key.startswith('_'):
        variable_name = key.replace('_', '', 1)
    else:
        variable_name = key
    return variable_name.replace('_', ' ')


def get_pdf_file_value_string(item, spaces=0):
    if isinstance(item, (bool, type(None))):
        return str(item)
    elif isinstance(item, str):
        return item
    elif isinstance(item, dict):
        out_string = ''
        for k, it in item.items():
            if len(out_string):
                out_string += spaces * '   ' + f'{k}:\n' + (spaces + 1) * '   ' + \
                              get_pdf_file_value_string(it, spaces + 1) + '\n\n'
            else:
                out_string += (spaces - 1) * '   ' + f'{k}:\n' + (spaces + 1) * '   ' + \
                              get_pdf_file_value_string(it, spaces + 1) + '\n\n'
        return out_string[:-2]
    elif isinstance(item, list):
        out_string = '('
        if len(item) == 2:
            if isinstance(item[1], str):
                if len(item[1]) == 36 and item[1].count('-') == 4:
                    return str(item[0])
        for it in item:
            out_string += get_pdf_file_value_string(it, spaces + 1) + ', '

        if len(out_string) > 2:
            return out_string[:-2] + ')'
        else:
            return out_string + ')'
    elif isinstance(item, str):
        return item
    elif isinstance(item, (int, float)):
        return str(item)
    else:
        return ''
