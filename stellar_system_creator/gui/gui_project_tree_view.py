
from typing import Dict, List, Union

import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeView
from PyQt5.Qt import QStandardItemModel

from stellar_system_creator.filing import load
from stellar_system_creator.solar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.solar_system_elements.solar_system import SolarSystem
from stellar_system_creator.solar_system_elements.stellar_body import StellarBody
from stellar_system_creator.solar_system_elements.binary_system import BinarySystem


def get_accumulated_dict(list_of_dicts: List[Dict], target_keys):
    for dictionary in list_of_dicts:
        for target_key in target_keys:
            if target_key not in dictionary.keys():
                dictionary[target_key] = None

    returning_dict = {key: [d[key] for d in list_of_dicts] for key in target_keys}

    if len(returning_dict['Object']):
        if 'semi_major_axis' in returning_dict['Object'][0].__dict__:
            sorted_index_by_semi_major_axis = np.argsort([
                obj.semi_major_axis.to('au').m for obj in returning_dict['Object']])
            return {key: np.array(returning_dict[key])[sorted_index_by_semi_major_axis] for key in returning_dict}

    sorted_index_by_name = np.argsort(returning_dict['Name'])
    return {key: np.array(returning_dict[key])[sorted_index_by_name] for key in returning_dict}


def get_stellar_body_dict(stellar_body: StellarBody) -> Dict:
    from stellar_system_creator.gui.solar_system_element_context_menus.standard_items import TreeViewItemFromSolarSystemElement
    stellar_body_item = TreeViewItemFromSolarSystemElement(stellar_body)
    stellar_body_dict = {'Name': stellar_body.name, 'Object': stellar_body, 'TreeViewItem': stellar_body_item}
    return stellar_body_dict


def get_binary_system_dict(binary_system: BinarySystem) -> Dict:

    primary_dict = {}
    if isinstance(binary_system.primary_body, StellarBody):
        primary_dict = get_stellar_body_dict(binary_system.primary_body)
    elif isinstance(binary_system.primary_body, BinarySystem):
        primary_dict = get_binary_system_dict(binary_system.primary_body)

    secondary_dict = {}
    if isinstance(binary_system.secondary_body, StellarBody):
        secondary_dict = get_stellar_body_dict(binary_system.secondary_body)
    elif isinstance(binary_system.secondary_body, BinarySystem):
        secondary_dict = get_binary_system_dict(binary_system.secondary_body)

    target_keys = ['Name', 'Object', 'TreeViewItem', 'BinaryChildren']
    children_dicts = get_accumulated_dict([primary_dict, secondary_dict], target_keys)

    from stellar_system_creator.gui.solar_system_element_context_menus.standard_items import TreeViewItemFromSolarSystemElement
    binary_system_item = TreeViewItemFromSolarSystemElement(binary_system)
    binary_system_dict = {'Name': binary_system.name, 'Object': binary_system,
                          'TreeViewItem': binary_system_item, 'BinaryChildren': children_dicts}

    return binary_system_dict


def get_planetary_system_dict(planetary_system: PlanetarySystem) -> Dict:

    keys = ['Name',  'Object', 'TreeViewItem']
    satellite_dicts = get_accumulated_dict([get_stellar_body_dict(satellite)
                                            for satellite in planetary_system.satellite_list], keys)

    trojan_dicts = get_accumulated_dict([get_stellar_body_dict(trojan)
                                         for trojan in planetary_system.trojans_list], keys)

    parent_dict = {}
    if isinstance(planetary_system.parent, StellarBody):
        parent_dict = get_stellar_body_dict(planetary_system.parent)
    elif isinstance(planetary_system.parent, BinarySystem):
        parent_dict = get_binary_system_dict(planetary_system.parent)

    from stellar_system_creator.gui.solar_system_element_context_menus.standard_items import TreeViewItemFromSolarSystemElement
    planetary_system_item = TreeViewItemFromSolarSystemElement(planetary_system)
    planetary_system_dict = {'Name': planetary_system.name, 'Object': planetary_system,
                             'TreeViewItem': planetary_system_item, 'Parent': parent_dict,
                             'Satellites': satellite_dicts, 'Trojans': trojan_dicts}

    return planetary_system_dict


def get_solar_system_dict(solar_system: SolarSystem) -> Dict:

    keys = ['Name', 'Object', 'TreeViewItem', 'Parent', 'Satellites', 'Trojans']
    planetary_dicts = get_accumulated_dict([get_planetary_system_dict(planetary_system)
                                            for planetary_system in solar_system.planetary_systems], keys)

    keys = ['Name', 'Object', 'TreeViewItem']
    asteroid_belt_dicts = get_accumulated_dict([get_stellar_body_dict(asteroid_belt)
                                                for asteroid_belt in solar_system.asteroid_belts], keys)

    parent_dict = {}
    if isinstance(solar_system.parent, StellarBody):
        parent_dict = get_stellar_body_dict(solar_system.parent)
    elif isinstance(solar_system.parent, BinarySystem):
        parent_dict = get_binary_system_dict(solar_system.parent)

    from stellar_system_creator.gui.solar_system_element_context_menus.standard_items import TreeViewItemFromSolarSystemElement
    solar_system_item = TreeViewItemFromSolarSystemElement(solar_system)
    solar_system_dict = {'Name': solar_system.name, 'Object': solar_system,
                         'TreeViewItem': solar_system_item, 'Parent': parent_dict,
                         'Planets': planetary_dicts, 'Asteroid Belts': asteroid_belt_dicts}

    return solar_system_dict


def set_system_parent_tree_model_from_dict(parent_dict, tree_model):
    from stellar_system_creator.gui.solar_system_element_context_menus.standard_items import TreeViewItemFromSolarSystemElement
    if parent_dict != {}:
        parent_tree_item: TreeViewItemFromSolarSystemElement = parent_dict['TreeViewItem']
        tree_model.appendRow(parent_tree_item)

        # set parent's children branches if parent is binary
        if 'BinaryChildren' in parent_dict.keys():
            primary_child_tree_item: TreeViewItemFromSolarSystemElement = \
                parent_dict['BinaryChildren']['TreeViewItem'][0]
            parent_tree_item.appendRow(primary_child_tree_item)

            secondary_child_tree_item: TreeViewItemFromSolarSystemElement = \
                parent_dict['BinaryChildren']['TreeViewItem'][1]
            parent_tree_item.appendRow(secondary_child_tree_item)


def set_system_element_tree_model_from_dict(element_string: str, system_dict, tree_model, subsystem_function=None):
    element_dict = system_dict[element_string]
    from stellar_system_creator.gui.solar_system_element_context_menus.standard_items import TreeViewItemFromString

    element_tree_item = TreeViewItemFromString(element_string)
    tree_model.appendRow(element_tree_item)
    if len(element_dict['TreeViewItem']):
        element_tree_item.appendRows(element_dict['TreeViewItem'])
        if subsystem_function is not None:
            for i in range(len(element_dict['TreeViewItem'])):
                subsystem_function(element_dict['TreeViewItem'][i], element_dict['Object'][i])


def set_planetary_system_tree_model_from_ssc_object(tree_model, file):
    planetary_system_dict = get_planetary_system_dict(file)

    # set parent root
    parent_dict: Dict = planetary_system_dict['Parent']
    set_system_parent_tree_model_from_dict(parent_dict, tree_model)

    # set satellite root and branches if there are satellites
    set_system_element_tree_model_from_dict('Satellites', planetary_system_dict, tree_model)

    # set trojan root and branches if there are trojans
    set_system_element_tree_model_from_dict('Trojans', planetary_system_dict, tree_model)

    return planetary_system_dict


def set_solar_system_tree_model_from_ssc_object(tree_model, file):
    solar_system_dict = get_solar_system_dict(file)

    # set parent root
    parent_dict: Dict = solar_system_dict['Parent']
    set_system_parent_tree_model_from_dict(parent_dict, tree_model)

    # set planet root and branches if there are planets
    set_system_element_tree_model_from_dict('Planets', solar_system_dict, tree_model,
                                            set_planetary_system_tree_model_from_ssc_object)

    # set asteroid belt root and branches if there are asteroid belts
    set_system_element_tree_model_from_dict('Asteroid Belts', solar_system_dict, tree_model)

    return solar_system_dict


class ProjectTreeView(QTreeView):

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

        self._get_scc_object_from_file()
        self._get_system_tree()

        self.setHeaderHidden(True)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

        # self.setIconSize(QSize(50, 50))

    def open_context_menu(self, position):

        from stellar_system_creator.gui.solar_system_element_context_menus.standard_items import TreeViewItemFromSolarSystemElement, \
            TreeViewItemFromString

        index = self.selectedIndexes()[0]
        project_tree_view_item: Union[TreeViewItemFromSolarSystemElement,
                                      TreeViewItemFromString] = index.model().itemFromIndex(index)

        project_tree_view_item.context_menu.exec_(self.viewport().mapToGlobal(position))

    def update_scc_object_from_file(self, filename):
        self.filename = filename
        self._get_file()

    def _get_scc_object_from_file(self):
        self.scc_object = load(self.filename)

    def _get_system_tree(self):
        tree_model = QStandardItemModel(self)

        if self.scc_object.__class__ == SolarSystem:
            self.system_dict = set_solar_system_tree_model_from_ssc_object(tree_model, self.scc_object)
        elif self.scc_object.__class__ == PlanetarySystem:
            self.system_dict = set_planetary_system_tree_model_from_ssc_object(tree_model, self.scc_object)

        self.setModel(tree_model)
        self.expandAll()

    def collapse_recursively(self, item):
        for row_index in range(item.rowCount()):
            child_item = item.child(row_index)
            self.collapse_recursively(child_item)
            self.collapse(child_item.index())
        self.collapse(item.index())
