import gc
import inspect
import json
import os
import pickle
import shutil
import uuid
import zipfile
from typing import Union, Dict, List
from zipfile import ZipFile

import blosc
import _pickle as cPickle
# https://stackoverflow.com/questions/57983431/whats-the-most-space-efficient-way-to-compress-serialized-python-data
import numpy as np
import pkg_resources
from PIL import Image

from stellar_system_creator.astrothings.units import Q_
from stellar_system_creator.stellar_system_elements import *


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
    obj = cPickle.loads(depressed_pickle)  # turn bytes object back into data

    return obj


def save_as_ssc_light(obj: Union[StellarBody, BinarySystem, PlanetarySystem, StellarSystem, MultiStellarSystemSType],
                      filename: str):
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
        save_object_to_json(obj, temp_folder)
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


def save_system_to_json(obj: Union[PlanetarySystem, StellarSystem, MultiStellarSystemSType], target_folder: str):
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


def get_children_uuid_list(children: List[Union[StellarBody, BinarySystem, PlanetarySystem, StellarSystem]]):
    return [child._uuid for child in children]


def save_object_to_json(obj: Union[StellarBody, BinarySystem], target_folder: str):
    if isinstance(obj, StellarBody):
        save_stellar_body_to_json(obj, target_folder)
    elif isinstance(obj, BinarySystem):
        save_binary_to_json(obj, target_folder)
    elif isinstance(obj, (PlanetarySystem, StellarSystem, MultiStellarSystemSType)):
        save_system_to_json(obj, target_folder)
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
                        ring_color_list.append(gradient_color.get_color())
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


def load_ssc_light(filename: str) -> Union[StellarBody, BinarySystem,
                                           PlanetarySystem, StellarSystem, MultiStellarSystemSType]:

    allmother_filename = os.path.join(filename, '.allmother.json')
    print(allmother_filename)
    kwargs = get_dict_from_json(allmother_filename)

    return get_object_from_kwargs_uuid(kwargs['allmother_uuid'], allmother_filename)


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
