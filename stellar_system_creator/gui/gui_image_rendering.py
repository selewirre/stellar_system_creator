import tempfile
from functools import partial
from typing import Union

import matplotlib.pyplot as plt
import pkg_resources
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QThread, QModelIndex
from PyQt5.QtGui import QIcon
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QMenu, QAction, QFileDialog, QSizePolicy, \
    QComboBox, QCheckBox, QDialog, QDialogButtonBox, QMessageBox, QGraphicsView, QGraphicsScene

from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items import \
    TreeViewItemFromStellarSystemElement
from stellar_system_creator.gui.stellar_system_element_context_menus.stellar_bodies_context_menu.detail_dialog_widgets import \
    GroupBox, ComboBox
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem, MultiStellarSystemSType


# https://stackoverflow.com/questions/57432570/generate-a-svg-file-with-pyqt5


class SystemRenderingWidget(QSvgWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.hide()
        self.latest_fig = None

    def render_image(self, ssc_object: Union[MultiStellarSystemSType, StellarSystem, PlanetarySystem, None]):

        if ssc_object is not None:
            if ssc_object.parent is not None:
                self.change_draw_line_options(ssc_object)
                self.hide()
                save_format = 'svg'
                with tempfile.NamedTemporaryFile("r+b", delete=True) as fd:
                    if isinstance(ssc_object, MultiStellarSystemSType):
                        ssc_object.draw_multi_stellar_system(save_fig=True, save_temp_file=fd, save_format=save_format)
                    elif isinstance(ssc_object, StellarSystem):
                        ssc_object.draw_stellar_system(save_fig=True, save_temp_file=fd, save_format=save_format)
                    elif isinstance(ssc_object, PlanetarySystem):
                        ssc_object.draw_planetary_system(save_fig=True, save_temp_file=fd, save_format=save_format)
                    fd.seek(0)
                    self.renderer().load(fd.name)
                self.latest_fig = ssc_object.fig
                ssc_object.fig = None
                ssc_object.ax = None
                self.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
                self.show()
                self.adjustSize()
            else:
                self.hide()
        else:
            self.hide()

    def change_draw_line_options(self, ssc_object):
        # noinspection PyTypeChecker
        rsd: RenderingSettingsDialog = self.parent().parent().rendering_settings_dialog
        if isinstance(ssc_object, MultiStellarSystemSType):
            for child in ssc_object.children:
                child.want_draw_stellar_system_limits = rsd.draw_stellar_system_limits_check_box.isChecked()
                child.want_draw_orbit_lines = rsd.draw_planet_orbit_line_check_box.isChecked()
                child.want_orbit_label = rsd.draw_planet_orbit_distance_check_box.isChecked()
                child.want_draw_extended_habitable_zone = rsd.draw_extended_habitable_zone_check_box.isChecked()
                child.want_draw_conservative_habitable_zone = rsd.draw_conservative_habitable_zone_check_box.isChecked()
                child.want_draw_frost_line = rsd.draw_frost_line_check_box.isChecked()
        elif isinstance(ssc_object, StellarSystem):
            ssc_object.want_draw_stellar_system_limits = rsd.draw_stellar_system_limits_check_box.isChecked()
            ssc_object.want_draw_orbit_lines = rsd.draw_planet_orbit_line_check_box.isChecked()
            ssc_object.want_orbit_label = rsd.draw_planet_orbit_distance_check_box.isChecked()
            ssc_object.want_draw_extended_habitable_zone = rsd.draw_extended_habitable_zone_check_box.isChecked()
            ssc_object.want_draw_conservative_habitable_zone = rsd.draw_conservative_habitable_zone_check_box.isChecked()
            ssc_object.want_draw_frost_line = rsd.draw_frost_line_check_box.isChecked()
        elif isinstance(ssc_object, PlanetarySystem):
            ssc_object.want_draw_planetary_system_limits = rsd.draw_planetary_system_limits_check_box.isChecked()
            ssc_object.want_draw_satellite_orbits = rsd.draw_satellite_orbit_line_check_box.isChecked()
            ssc_object.want_orbit_label = rsd.draw_satellite_orbit_distance_check_box.isChecked()


class SystemImageWidget(QWidget):

    def __init__(self, tree_view: ProjectTreeView):
        super().__init__()
        self.tree_view = tree_view

        self._set_graphics()
        self._set_options_widget()

        layout = QVBoxLayout()

        layout.addWidget(self.options_widget)
        layout.addWidget(self.graphics_view)
        layout.setAlignment(self.options_widget, Qt.AlignTop)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setStretchFactor(self.options_widget, 0)
        layout.setStretchFactor(self.system_rendering_widget, 1)
        # layout.sets
        self.setLayout(layout)

    def _set_graphics(self):
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.system_rendering_widget = SystemRenderingWidget(self.graphics_view)
        self.graphics_scene.addWidget(self.system_rendering_widget)

    def _set_options_widget(self):
        self.options_widget = QWidget(self)
        layout = QHBoxLayout()

        self.render_button = QPushButton(parent=self)
        render_dir = pkg_resources.resource_filename('stellar_system_creator', 'gui/logo.ico')
        self.render_button.setIcon(QIcon(render_dir))
        self.render_button.setStyleSheet("padding: 1px;")
        self.render_button.adjustSize()
        self.render_button.setToolTip('Press to render image.')
        self.render_button.pressed.connect(self.render_process)
        self.render_thread = None

        # TODO: Add dropdown menu with all systems that can be rendered
        # TODO: Connect dropdown menu to treeview edit triggered process (still don't know exaclty how)
        # print(self.tree_view.ssc_object.name)
        # # if
        # self.system_drop_menu = QComboBox()
        # self.system_drop_menu.addItem(self.tree_view.ssc_object.name)
        self.target_treeview = self.tree_view

        self.rendering_settings_dialog = RenderingSettingsDialog(self)
        self.rendering_settings_button = QPushButton('Rendering Settings', self)
        self.rendering_settings_button.setStyleSheet("padding: 1px;")
        self.rendering_settings_button.adjustSize()
        self.rendering_settings_button.setToolTip('Press to change rendering settings.')
        self.rendering_settings_button.pressed.connect(self.rendering_settings_process)

        self.save_image_button = QPushButton('Save Image', self)
        self.save_image_button.setStyleSheet("padding: 1px;")
        self.save_image_button.adjustSize()
        self.save_image_button.setToolTip('Press to save most recently rendered image.')
        self.save_image_button.pressed.connect(self.save_image_process)

        layout.addWidget(self.render_button)
        layout.addWidget(self.rendering_settings_button)
        layout.addWidget(self.save_image_button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.options_widget.setLayout(layout)
        self.options_widget.setFixedSize(self.options_widget.sizeHint())

    def render_process(self):
        self.render_thread = ImageRenderingProcess(self.target_treeview, self.system_rendering_widget, self.render_button)
        self.render_thread.start()

    def rendering_settings_process(self):
        self.rendering_settings_dialog.show()

    def save_image_process(self):
        fig: plt.Figure = self.system_rendering_widget.latest_fig
        if fig is None:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("'Save Image' has failed...")
            message_box.setText(f"There is no rendered image to be saved.")
            message_box.exec()
            return

        filename = QFileDialog.getSaveFileName(self, 'Save Image', '', "All Files (*);;"
                                                                       "PDF (*.pdf);;"
                                                                       "SVG (*.svg);;"
                                                                       "PNG (*.png)")[0]
        if filename != '':
            fig.savefig(filename, dpi=1200)


class RenderingSettingsDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowTitle('Rendering Settings')

        self._set_options_widget()
        # self._set_button_box()

        layout = QVBoxLayout()
        layout.addWidget(self.options_widget)
        # layout.addWidget(self.button_box)
        self.setLayout(layout)

    def _set_options_widget(self):
        self._set_available_systems_drop_down()
        # self._set_multi_stellar_system_groupbox()
        self._set_stellar_system_groupbox()
        self._set_planetary_system_groupbox()
        self.options_widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.available_systems_drop_down)
        # layout.addWidget(self.multi_stellar_system_groupbox)
        layout.addWidget(self.stellar_system_groupbox)
        layout.addWidget(self.planetary_system_groupbox)
        layout.addStretch()
        self.options_widget.setLayout(layout)

    def _set_multi_stellar_system_groupbox(self):
        self.multi_stellar_system_groupbox = GroupBox('Multi-Stellar System Options')
        layout = QVBoxLayout()

        self.multi_stellar_system_groupbox.setLayout(layout)

    def _set_stellar_system_groupbox(self):
        self.stellar_system_groupbox = GroupBox('Stellar System Options')
        layout = QVBoxLayout()

        self.draw_stellar_system_limits_check_box = QCheckBox()
        self.draw_stellar_system_limits_check_box.setText('Show inner/outer limits')
        self.draw_stellar_system_limits_check_box.setChecked(True)

        self.draw_planet_orbit_line_check_box = QCheckBox()
        self.draw_planet_orbit_line_check_box.setText('Show planet orbit lines')
        self.draw_planet_orbit_line_check_box.setChecked(True)

        self.draw_planet_orbit_distance_check_box = QCheckBox()
        self.draw_planet_orbit_distance_check_box.setText('Show planet orbit distance')
        self.draw_planet_orbit_distance_check_box.setChecked(True)

        self.draw_extended_habitable_zone_check_box = QCheckBox()
        self.draw_extended_habitable_zone_check_box.setText('Show relaxed HZ')
        self.draw_extended_habitable_zone_check_box.setChecked(True)

        self.draw_conservative_habitable_zone_check_box = QCheckBox()
        self.draw_conservative_habitable_zone_check_box.setText('Show conservative HZ')
        self.draw_conservative_habitable_zone_check_box.setChecked(True)

        self.draw_frost_line_check_box = QCheckBox()
        self.draw_frost_line_check_box.setText('Show water frost-line')
        self.draw_frost_line_check_box.setChecked(True)

        layout.addWidget(self.draw_stellar_system_limits_check_box)
        layout.addWidget(self.draw_planet_orbit_line_check_box)
        layout.addWidget(self.draw_planet_orbit_distance_check_box)
        layout.addWidget(self.draw_extended_habitable_zone_check_box)
        layout.addWidget(self.draw_conservative_habitable_zone_check_box)
        layout.addWidget(self.draw_frost_line_check_box)
        layout.addStretch()
        self.stellar_system_groupbox.setLayout(layout)

    def _set_planetary_system_groupbox(self):
        self.planetary_system_groupbox = GroupBox('Planetary System Options')
        layout = QVBoxLayout()

        self.draw_planetary_system_limits_check_box = QCheckBox()
        self.draw_planetary_system_limits_check_box.setText('Show inner/outer limits')
        self.draw_planetary_system_limits_check_box.setChecked(True)

        self.draw_satellite_orbit_line_check_box = QCheckBox()
        self.draw_satellite_orbit_line_check_box.setText('Show satellite orbit lines')
        self.draw_satellite_orbit_line_check_box.setChecked(True)

        self.draw_satellite_orbit_distance_check_box = QCheckBox()
        self.draw_satellite_orbit_distance_check_box.setText('Show planet orbit distance')
        self.draw_satellite_orbit_distance_check_box.setChecked(True)

        layout.addWidget(self.draw_planetary_system_limits_check_box)
        layout.addWidget(self.draw_satellite_orbit_line_check_box)
        layout.addWidget(self.draw_satellite_orbit_distance_check_box)
        layout.addStretch()
        self.planetary_system_groupbox.setLayout(layout)

    def _set_available_systems_drop_down(self):
        self.available_systems_drop_down = QComboBox()
        # noinspection PyTypeChecker
        parent: SystemImageWidget = self.parent()
        self.available_systems_drop_down.addItem(parent.tree_view.ssc_object.name)
        all_items = parent.tree_view.getAllRoots()
        for child_item in all_items:
            if isinstance(child_item, TreeViewItemFromStellarSystemElement):
                if isinstance(child_item.ssc_object, (PlanetarySystem, StellarSystem, MultiStellarSystemSType)):
                    ssc_obj = child_item.ssc_object
                    text = ssc_obj.name
                    while ssc_obj.parent is not None:
                        if not isinstance(ssc_obj, (PlanetarySystem, StellarSystem, MultiStellarSystemSType)):
                            if ssc_obj.parent.name == parent.tree_view.ssc_object.parent.name:
                                text = f'{parent.tree_view.ssc_object.name}/{text}'
                            else:
                                text = f'{ssc_obj.parent.name}/{text}'
                        ssc_obj = ssc_obj.parent
                    self.available_systems_drop_down.addItem(text)

        self.available_systems_drop_down.currentTextChanged.connect(self.available_system_selection_change_process)

    def available_system_selection_change_process(self):
        obj_name = self.available_systems_drop_down.currentText()
        # noinspection PyTypeChecker
        parent: SystemImageWidget = self.parent()
        if obj_name == parent.tree_view.ssc_object.name:
            parent.target_treeview = parent.tree_view
            return
        all_items = parent.tree_view.getAllRoots()
        for child_item in all_items:
            if isinstance(child_item, TreeViewItemFromStellarSystemElement):
                if isinstance(child_item.ssc_object, (PlanetarySystem, StellarSystem, MultiStellarSystemSType)):
                    ssc_obj = child_item.ssc_object
                    text = ssc_obj.name
                    while ssc_obj.parent is not None:
                        if not isinstance(ssc_obj, (PlanetarySystem, StellarSystem, MultiStellarSystemSType)):
                            if ssc_obj.parent.name == parent.tree_view.ssc_object.parent.name:
                                text = f'{parent.tree_view.ssc_object.name}/{text}'
                            else:
                                text = f'{ssc_obj.parent.name}/{text}'
                        ssc_obj = ssc_obj.parent

                    if text == obj_name:
                        parent.target_treeview = child_item
                        return

    def update_available_systems_drop_down(self, child_item: TreeViewItemFromStellarSystemElement, old_child_name):
        tree_view: ProjectTreeView = child_item.model().parent()
        ssc_obj = child_item.ssc_object
        text = ssc_obj.name
        old_text = old_child_name
        while ssc_obj.parent is not None:
            if not isinstance(ssc_obj, (PlanetarySystem, StellarSystem, MultiStellarSystemSType)):
                if ssc_obj.parent.name == tree_view.ssc_object.parent.name:
                    text = f'{tree_view.ssc_object.name}/{text}'
                    old_text = f'{tree_view.ssc_object.name}/{old_text}'
                else:
                    text = f'{ssc_obj.parent.name}/{text}'
                    old_text = f'{ssc_obj.parent.name}/{old_text}'
            ssc_obj = ssc_obj.parent
        old_text_index = self.available_systems_drop_down.findText(old_text)
        if old_text_index > 0:
            self.available_systems_drop_down.setItemText(old_text_index, text)
        else:
            self.available_systems_drop_down.addItem(text)

    def _set_button_box(self):
        self.button_box = QDialogButtonBox((QDialogButtonBox.Cancel | QDialogButtonBox.Ok), self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Enter or a0.key() == Qt.Key_Return or a0.key() == Qt.Key_Escape:
            return
        super().keyPressEvent(a0)

    def accept(self) -> None:
        super().accept()

    def reject(self) -> None:
        super().reject()


class ImageRenderingProcess(QThread):

    def __init__(self, tree_view: ProjectTreeView,
                 rendering_widget: SystemRenderingWidget, render_button: QPushButton):
        super().__init__()
        self.ssc_object: Union[StellarSystem, PlanetarySystem, None] = tree_view.ssc_object
        self.rendering_widget = rendering_widget
        self.render_button = render_button

    def run(self):
        button_icon = self.render_button.icon()
        loading_dir = pkg_resources.resource_filename('stellar_system_creator', 'gui/gui_icons/loading.svg')
        self.render_button.setIcon(QIcon(loading_dir))
        self.render_button.setDisabled(True)
        self.rendering_widget.render_image(self.ssc_object)
        self.render_button.setEnabled(True)
        self.render_button.setIcon(button_icon)


# class ImageContextMenu(QMenu):
#
#     def __init__(self):
#         super().__init__()
#
#         self._create_menu_actions()
#         self._connect_actions()
#         self._create_menu()
#
#     def _create_menu(self):
#         self.addAction(self.save_image_action)
#
#     def _connect_actions(self):
#         self.save_image_action.triggered.connect(self.save_image_process)
#
#     def _create_menu_actions(self):
#         self.save_image_action = QAction(f"&Save Image...", self)
#
#     def save_image_process(self):
#         filename: str = QFileDialog.getSaveFileName(self.parent(), 'Save Project')[0]
#         if filename != '':
#             self.parent().
#         else:
#             return
