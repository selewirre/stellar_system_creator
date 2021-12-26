from typing import Union

import numpy as np
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.Qt import QStandardItem
from PyQt5.QtCore import pyqtSignal

from .category_context_menu import CategoryBasedTreeViewItemContextMenu
from .stellar_bodies_context_menu.binary_system_context_menu import StellarBinaryTreeViewItemContextMenu
from .stellar_bodies_context_menu.planet_context_menu import \
    PlanetTreeViewItemContextMenu, SatelliteTreeViewItemContextMenu, AsteroidBeltTreeViewItemContextMenu, \
    TrojanTreeViewItemContextMenu, TrojanSatelliteTreeViewItemContextMenu
from .stellar_bodies_context_menu.star_context_menu import \
    StarTreeViewItemContextMenu
from .system_context_menu import PlanetarySystemTreeViewItemContextMenu, StellarSystemTreeViewItemContextMenu, \
    MultiStellarSystemTreeViewItemContextMenu
from stellar_system_creator.stellar_system_elements.stellar_body import StellarBody, Star, Planet, Satellite, \
    AsteroidBelt, Trojan, TrojanSatellite
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem, MultiStellarSystemSType
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.binary_system import BinarySystem, StellarBinary


class TreeViewItemFromString(QStandardItem):
    def __init__(self, category: str, ssc_parent):
        super().__init__()
        self.setEditable(False)
        self.ssc_parent: Union[PlanetarySystem, StellarSystem, MultiStellarSystemSType] = ssc_parent
        self.category = category
        self.setText(self.category)

        self._get_context_menu_class()
        self._set_context_menu()

    def _get_context_menu_class(self):
        self.context_menu_class = CategoryBasedTreeViewItemContextMenu

    def _set_context_menu(self):
        self.context_menu = self.context_menu_class(self)


class TreeViewItemFromStellarSystemElement(QStandardItem):
    def __init__(self, ssc_object: Union[StellarBody, Star, Planet, StellarBinary,
                                         BinarySystem, PlanetarySystem, StellarSystem]):
        super().__init__()
        self.setEditable(False)
        self.ssc_object = ssc_object
        self.update_text()

        self._get_context_menu_class()
        self._set_context_menu()

        self.set_stellar_system_element_icon()

    def _get_context_menu_class(self):
        if isinstance(self.ssc_object, StellarBinary):
            self.context_menu_class = StellarBinaryTreeViewItemContextMenu
        elif isinstance(self.ssc_object, MultiStellarSystemSType):
            self.context_menu_class = MultiStellarSystemTreeViewItemContextMenu
        elif isinstance(self.ssc_object, StellarSystem):
            self.context_menu_class = StellarSystemTreeViewItemContextMenu
        elif isinstance(self.ssc_object, PlanetarySystem):
            self.context_menu_class = PlanetarySystemTreeViewItemContextMenu
        elif isinstance(self.ssc_object, Star):
            self.context_menu_class = StarTreeViewItemContextMenu
        elif isinstance(self.ssc_object, TrojanSatellite):
            self.context_menu_class = TrojanSatelliteTreeViewItemContextMenu
        elif isinstance(self.ssc_object, Satellite):
            self.context_menu_class = SatelliteTreeViewItemContextMenu
        elif isinstance(self.ssc_object, Trojan):
            self.context_menu_class = TrojanTreeViewItemContextMenu
        elif isinstance(self.ssc_object, AsteroidBelt):
            self.context_menu_class = AsteroidBeltTreeViewItemContextMenu
        elif isinstance(self.ssc_object, Planet):
            self.context_menu_class = PlanetTreeViewItemContextMenu

    def _set_context_menu(self):
        self.context_menu = self.context_menu_class(self)

    def set_stellar_system_element_icon(self):
        try:
            image_array = self.ssc_object.image_array
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
        from ..gui_image_rendering import SystemImageWidget, RenderingSettingsDialog
        if self.model() is not None:
            rendering_dialog: RenderingSettingsDialog = self.model().parent().parent().parent().\
                findChild(SystemImageWidget).rendering_settings_dialog
            rendering_dialog.update_available_systems_drop_down(self, self.text())
        self.setText(f"{self.ssc_object.name}")
