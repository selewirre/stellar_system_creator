from typing import Union

import numpy as np
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.Qt import QStandardItem

from .misc import CategoryBasedTreeViewItemContextMenu
from .stellar_bodies_context_menu.planet_context_menu import \
    PlanetTreeViewItemContextMenu, SatelliteTreeViewItemContextMenu, AsteroidBeltTreeViewItemContextMenu, \
    TrojanTreeViewItemContextMenu, TrojanSatelliteTreeViewItemContextMenu
from .stellar_bodies_context_menu.star_context_menu import \
    StarTreeViewItemContextMenu
from .system_context_menu import BinarySystemTreeViewItemContextMenu, \
    PlanetarySystemTreeViewItemContextMenu, StellarSystemTreeViewItemContextMenu
from stellar_system_creator.stellar_system_elements.stellar_body import StellarBody, Star, Planet, Satellite, \
    AsteroidBelt, Trojan, TrojanSatellite
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem


class TreeViewItemFromString(QStandardItem):
    def __init__(self, category: str):
        super().__init__()
        self.setEditable(False)

        self.category = category
        self.setText(self.category)

        self._get_context_menu_class()
        self._set_context_menu()

    def _get_context_menu_class(self):
        self.context_menu_class = CategoryBasedTreeViewItemContextMenu

    def _set_context_menu(self):
        self.context_menu = self.context_menu_class(self)


class TreeViewItemFromStellarSystemElement(QStandardItem):
    def __init__(self, stellar_system_element: Union[StellarBody, Star, Planet,
                                                   BinarySystem, PlanetarySystem, StellarSystem]):
        super().__init__()
        self.setEditable(False)
        self.stellar_system_element = stellar_system_element
        self.update_text()

        self._get_context_menu_class()
        self._set_context_menu()

        self.set_stellar_system_element_icon()

    def _get_context_menu_class(self):
        if isinstance(self.stellar_system_element, BinarySystem):
            self.context_menu_class = BinarySystemTreeViewItemContextMenu
        elif isinstance(self.stellar_system_element, StellarSystem):
            self.context_menu_class = StellarSystemTreeViewItemContextMenu
        elif isinstance(self.stellar_system_element, PlanetarySystem):
            self.context_menu_class = PlanetarySystemTreeViewItemContextMenu
        elif isinstance(self.stellar_system_element, Star):
            self.context_menu_class = StarTreeViewItemContextMenu
        elif isinstance(self.stellar_system_element, TrojanSatellite):
            self.context_menu_class = TrojanSatelliteTreeViewItemContextMenu
        elif isinstance(self.stellar_system_element, Satellite):
            self.context_menu_class = SatelliteTreeViewItemContextMenu
        elif isinstance(self.stellar_system_element, Trojan):
            self.context_menu_class = TrojanTreeViewItemContextMenu
        elif isinstance(self.stellar_system_element, AsteroidBelt):
            self.context_menu_class = AsteroidBeltTreeViewItemContextMenu
        elif isinstance(self.stellar_system_element, Planet):
            self.context_menu_class = PlanetTreeViewItemContextMenu

    def _set_context_menu(self):
        self.context_menu = self.context_menu_class(self)

    def set_stellar_system_element_icon(self):
        try:
            image_array = self.stellar_system_element.image_array
            if image_array.shape[0] > image_array.shape[1]:
                padding = (image_array.shape[0] - image_array.shape[1]) // 2
                image_array = np.pad(image_array, ((0, 0), (padding, padding), (0, 0)))
            else:
                padding = (image_array.shape[1] - image_array.shape[0]) // 2
                image_array = np.pad(image_array, ((padding, padding), (0, 0), (0, 0)))

            # noinspection PyTypeChecker
            image = QtGui.QImage(image_array, image_array.shape[1], image_array.shape[0],
                                 image_array.shape[1] * 4, QtGui.QImage.Format_RGBA8888)

            pix = QtGui.QPixmap(image)
            self.setIcon(QIcon(pix))
        except Exception:
            pass

    def update_text(self):
        self.setText(f"{self.stellar_system_element.name}")
