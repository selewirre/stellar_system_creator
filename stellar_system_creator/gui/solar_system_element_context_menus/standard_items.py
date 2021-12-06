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
    PlanetarySystemTreeViewItemContextMenu, SolarSystemTreeViewItemContextMenu
from stellar_system_creator.solar_system_elements.stellar_body import StellarBody, Star, Planet, Satellite, \
    AsteroidBelt, Trojans, TrojanSatellite
from stellar_system_creator.solar_system_elements.solar_system import SolarSystem
from stellar_system_creator.solar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.solar_system_elements.binary_system import BinarySystem


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


class TreeViewItemFromSolarSystemElement(QStandardItem):
    def __init__(self, solar_system_element: Union[StellarBody, Star, Planet,
                                                   BinarySystem, PlanetarySystem, SolarSystem]):
        super().__init__()
        self.setEditable(False)
        self.solar_system_element = solar_system_element
        self.update_text()

        self._get_context_menu_class()
        self._set_context_menu()

        self.set_solar_system_element_icon()

    def _get_context_menu_class(self):
        if isinstance(self.solar_system_element, BinarySystem):
            self.context_menu_class = BinarySystemTreeViewItemContextMenu
        elif isinstance(self.solar_system_element, SolarSystem):
            self.context_menu_class = SolarSystemTreeViewItemContextMenu
        elif isinstance(self.solar_system_element, PlanetarySystem):
            self.context_menu_class = PlanetarySystemTreeViewItemContextMenu
        elif isinstance(self.solar_system_element, Star):
            self.context_menu_class = StarTreeViewItemContextMenu
        elif isinstance(self.solar_system_element, TrojanSatellite):
            self.context_menu_class = TrojanSatelliteTreeViewItemContextMenu
        elif isinstance(self.solar_system_element, Satellite):
            self.context_menu_class = SatelliteTreeViewItemContextMenu
        elif isinstance(self.solar_system_element, Trojans):
            self.context_menu_class = TrojanTreeViewItemContextMenu
        elif isinstance(self.solar_system_element, AsteroidBelt):
            self.context_menu_class = AsteroidBeltTreeViewItemContextMenu
        elif isinstance(self.solar_system_element, Planet):
            self.context_menu_class = PlanetTreeViewItemContextMenu

    def _set_context_menu(self):
        self.context_menu = self.context_menu_class(self)

    def set_solar_system_element_icon(self):
        try:
            image_array = self.solar_system_element.image_array
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
        self.setText(f"{self.solar_system_element.name}")
