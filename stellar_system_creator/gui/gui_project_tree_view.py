
from typing import Dict, List, Union

import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeView
from PyQt5.Qt import QStandardItemModel

from stellar_system_creator.filing import load
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem
from stellar_system_creator.stellar_system_elements.stellar_body import StellarBody
from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem


def set_stellar_system_tree_model_from_ssc_object(tree_model, ssc_object: StellarSystem):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
    tree_model: Union[TreeViewItemFromString, QStandardItemModel]

    treeview_dict = {
        'Stellar Parent': {'TreeViewItem': TreeViewItemFromString('Stellar Parent', ssc_object),
                           'Children': {ssc_object.parent: tvifsse(ssc_object.parent)},
                           'Binary Children': {}},
        'Planetary Systems': {'TreeViewItem': TreeViewItemFromString('Planetary Systems', ssc_object),
                              'Children': {}},
        'Asteroid Belts': {'TreeViewItem': TreeViewItemFromString('Asteroid Belts', ssc_object),
                           'Children': {ab: tvifsse(ab) for ab in ssc_object.asteroid_belts}}}

    for ps in ssc_object.planetary_systems:
        treeview_dict['Planetary Systems']['Children'][ps] = tvifsse(ps)
        set_planetary_system_tree_model_from_ssc_object(
            treeview_dict['Planetary Systems']['Children'][ps], ps)

    if isinstance(ssc_object.parent, BinarySystem):
        treeview_dict['Stellar Parent']['Binary Children'] = {
            ssc_object.parent.primary_body: tvifsse(ssc_object.parent.primary_body),
            ssc_object.parent.secondary_body: tvifsse(ssc_object.parent.secondary_body)}

    set_tree_view_model_from_tree_view_dict(tree_model, treeview_dict)


def set_planetary_system_tree_model_from_ssc_object(tree_model, ssc_object: PlanetarySystem):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
    tree_model: Union[TreeViewItemFromString, QStandardItemModel]

    treeview_dict = {
        'Planetary Parent': {'TreeViewItem': TreeViewItemFromString('Planetary Parent', ssc_object),
                             'Children': {ssc_object.parent: tvifsse(ssc_object.parent)},
                             'Binary Children': {}},
        'Satellites': {'TreeViewItem': TreeViewItemFromString('Satellites', ssc_object),
                       'Children': {sat: tvifsse(sat) for sat in ssc_object.satellite_list}},
        'Trojans': {'TreeViewItem': TreeViewItemFromString('Trojans', ssc_object),
                    'Children': {trj: tvifsse(trj) for trj in ssc_object.trojans_list}}}

    if isinstance(ssc_object.parent, BinarySystem):
        treeview_dict['Planetary Parent']['Binary Children'] = {
            ssc_object.parent.primary_body: tvifsse(ssc_object.parent.primary_body),
            ssc_object.parent.secondary_body: tvifsse(ssc_object.parent.secondary_body)}

    set_tree_view_model_from_tree_view_dict(tree_model, treeview_dict)


def set_tree_view_model_from_tree_view_dict(tree_model: QStandardItemModel, treeview_dict: Dict):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString

    for key in treeview_dict:
        temp_tree_item: TreeViewItemFromString = treeview_dict[key]['TreeViewItem']
        tree_model.appendRow(temp_tree_item)
        for child_key in treeview_dict[key]['Children']:
            temp_child_item: tvifsse = treeview_dict[key]['Children'][child_key]
            temp_tree_item.appendRow(temp_child_item)
            if 'Binary Children' in treeview_dict[key].keys():
                temp_child_item.appendRows([tvi for tvi in treeview_dict[key]['Binary Children'].values()])


class ProjectTreeView(QTreeView):

    def __init__(self, ssc_object):
        super().__init__()
        self.ssc_object = ssc_object
        self._get_system_tree()

        self.setHeaderHidden(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

    def open_context_menu(self, position):

        from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
            import TreeViewItemFromStellarSystemElement, TreeViewItemFromString

        index = self.selectedIndexes()[0]
        project_tree_view_item: Union[TreeViewItemFromStellarSystemElement,
                                      TreeViewItemFromString] = index.model().itemFromIndex(index)

        project_tree_view_item.context_menu.exec_(self.viewport().mapToGlobal(position))

    def _get_system_tree(self):
        tree_model = QStandardItemModel(self)

        if self.ssc_object.__class__ == StellarSystem:
            set_stellar_system_tree_model_from_ssc_object(tree_model, self.ssc_object)
        elif self.ssc_object.__class__ == PlanetarySystem:
            set_planetary_system_tree_model_from_ssc_object(tree_model, self.ssc_object)

        self.setModel(tree_model)
        self.expandAll()

    def collapse_recursively(self, item):
        for row_index in range(item.rowCount()):
            child_item = item.child(row_index)
            self.collapse_recursively(child_item)
            self.collapse(child_item.index())
        self.collapse(item.index())
