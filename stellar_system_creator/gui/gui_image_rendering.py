import tempfile
from functools import partial
from typing import Union
import os
import glob

import cairo
import pkg_resources
from PIL import ImageQt, Image
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QThread, QModelIndex, QRectF, QPoint, QPointF
from PyQt5.QtGui import QIcon, QResizeEvent, QPixmap
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QMenu, QAction, QFileDialog, QSizePolicy, \
    QComboBox, QCheckBox, QDialog, QDialogButtonBox, QMessageBox, QGraphicsView, QGraphicsScene, QGestureEvent, QLabel, \
    QLineEdit, QScrollArea

from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items import \
    TreeViewItemFromStellarSystemElement
from stellar_system_creator.gui.stellar_system_element_context_menus.stellar_bodies_context_menu.detail_dialog_widgets import \
    GroupBox, ComboBox
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem, MultiStellarSystemSType
from stellar_system_creator.visualization.system_plot import get_ndarray_from_cairo_image_surface, \
    save_image_ndarray

# https://stackoverflow.com/questions/57432570/generate-a-svg-file-with-pyqt5


class SystemRenderingWidget(QLabel):

    def __init__(self, graphics_view):
        super().__init__()
        self.hide()
        self.latest_surface = None
        self.graphics_view: GraphicsView = graphics_view
        self.setMouseTracking(True)
        self.old_pos = None
        self.temp_file_name = '~.tempfile0.png'
        self.temp_file = None
        self.setScaledContents(True)
        while len(glob.glob(self.temp_file_name)):
            self.temp_file_name = self.temp_file_name[:-1] + str(int(self.temp_file_name[-1]) + 1)

    def delete_temp_file(self):
        os.remove(self.temp_file_name)
        self.temp_file = None

    def render_image(self, ssc_object: Union[MultiStellarSystemSType, StellarSystem, PlanetarySystem, None]):
        if ssc_object is not None:
            if ssc_object.parent is not None and self.temp_file_name is not None:
                self.change_draw_line_options(ssc_object)
                self.hide()
                save_format = 'png'
                fd = self.temp_file_name
                if isinstance(ssc_object, MultiStellarSystemSType):
                    ssc_object.draw_multi_stellar_system(save=True, save_temp_file=fd, save_format=save_format)
                elif isinstance(ssc_object, StellarSystem):
                    ssc_object.draw_stellar_system(save=True, save_temp_file=fd, save_format=save_format)
                elif isinstance(ssc_object, PlanetarySystem):
                    ssc_object.draw_planetary_system(save=True, save_temp_file=fd, save_format=save_format)
                pixmap = QPixmap.fromImage(ImageQt.ImageQt(Image.open(fd)))
                self.setPixmap(pixmap)
                # self.update()
                self.setBaseSize(pixmap.size())
                self.resize(self.baseSize())
                self.graphics_view.scene().setSceneRect(0, 0, pixmap.width(), pixmap.height())
                self.graphics_view.fitInView(self.graphics_view.sceneRect(), Qt.KeepAspectRatio)
                self.update()
            else:
                self.hide()
        else:
            self.hide()

    def change_draw_line_options(self, ssc_object):
        # noinspection PyTypeChecker
        rsd: RenderingSettingsDialog = self.graphics_view.parent().rendering_settings_dialog

        if isinstance(ssc_object, MultiStellarSystemSType):
            system_plots = ssc_object.system_plot.system_plots
        elif isinstance(ssc_object, (PlanetarySystem, StellarSystem)):
            system_plots = [ssc_object.system_plot]
        else:
            return

        for sp in system_plots:
            sp.scale = float(rsd.image_scale_line_edit.line_edit.text())

            # drawing options - lines // areas
            sp.want_orbit_limits = rsd.draw_orbit_limits_line_check_box.isChecked()
            sp.want_habitable_zones_extended = rsd.draw_extended_habitable_zone_check_box.isChecked()
            sp.want_habitable_zones_conservative = rsd.draw_conservative_habitable_zone_check_box.isChecked()
            sp.want_water_frost_line = rsd.draw_water_frost_line_check_box.isChecked()
            sp.want_rock_line = rsd.draw_rock_line_check_box.isChecked()
            sp.want_tidal_locking_radius = rsd.draw_tidal_locking_radius_check_box.isChecked()
            sp.want_orbit_lines = rsd.draw_orbit_line_check_box.isChecked()
            sp.orbit_line_width = float(rsd.orbit_line_width_line_edit.line_edit.text())

            # drawing options - labels
            sp.want_orbit_limits_labels = rsd.draw_orbit_limits_labels_check_box.isChecked()
            sp.want_other_line_labels = rsd.draw_other_line_labels_check_box.isChecked()
            sp.want_children_orbit_labels = rsd.draw_children_orbit_labels_check_box.isChecked()
            sp.want_children_name_labels = rsd.draw_children_name_labels_check_box.isChecked()
            sp.want_parent_name_labels = rsd.draw_parents_name_labels_check_box.isChecked()

            sp.orbit_distance_font_size = float(rsd.line_distance_font_size_line_edit.line_edit.text())
            sp.object_name_font_size = float(rsd.object_name_font_size_line_edit.line_edit.text())

            # drawing options - objects
            sp.satellite_plot_y_step = float(rsd.satellite_display_distance_line_edit.line_edit.text())
            sp.want_satellites = rsd.draw_children_satellites_check_box.isChecked()
            sp.want_trojans = rsd.draw_children_trojans_check_box.isChecked()
            sp.want_asteroid_belts = rsd.draw_asteroid_belt_check_box.isChecked()
            sp.want_children_objects = rsd.draw_children_check_box.isChecked()
            sp.want_parents = rsd.draw_parents_check_box.isChecked()

    # https://learndataanalysis.org/drag-and-move-an-object-with-your-mouse-pyqt5-tutorial/
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.old_pos = self.graphics_view.mapToScene(event.globalPos())
        self.count_mouse_event_steps = 1

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.old_pos is not None:
            self.count_mouse_event_steps += 1
            if self.count_mouse_event_steps % 5 == 0:
                newPos = self.graphics_view.mapToScene(event.globalPos())
                delta = newPos - self.old_pos
                self.graphics_view.translate(delta.x(), delta.y())
                self.old_pos = newPos

    def mouseReleaseEvent(self, event):
        self.old_pos = None


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
        self.setLayout(layout)

    # def changed_scene_process(self):
    #     self.graphics_view.fitInView(self.graphics_scene.sceneRect())

    def _set_graphics(self):
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_scene.setSceneRect(self.graphics_scene.itemsBoundingRect())
        self.graphics_view = GraphicsView(self.graphics_scene, self)

        # self.graphics_scene.setBackgroundBrush(self.graphics_view.backgroundBrush())
        self.system_rendering_widget = SystemRenderingWidget(self.graphics_view)
        self.graphics_scene.addWidget(self.system_rendering_widget)

    def _set_options_widget(self):
        self.options_widget = QWidget(self)
        layout = QHBoxLayout()

        self.render_button = QPushButton(parent=self)
        self.render_button.setShortcut('Ctrl+R')
        render_dir = pkg_resources.resource_filename('stellar_system_creator', 'gui/logo.ico')
        self.render_button.setIcon(QIcon(render_dir))
        self.render_button.setStyleSheet("padding: 1px;")
        self.render_button.adjustSize()
        shortcut_string = self.render_button.shortcut().toString()
        self.render_button.setToolTip(f'({shortcut_string}): Press to render image.')
        self.render_button.pressed.connect(self.render_process)
        self.render_thread = None

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
        # ssc_object = self.target_treeview.ssc_object
        # self.system_rendering_widget.set_temp_file()
        self.render_thread = ImageRenderingProcess(self.target_treeview, self.system_rendering_widget,
                                                   self.render_button)
        self.render_thread.finished.connect(self.thread_finished_process)
        self.render_thread.start()

    def thread_finished_process(self):
        ssc_object = self.target_treeview.ssc_object
        self.system_rendering_widget.show()
        self.system_rendering_widget.latest_surface = ssc_object.system_plot.plot_base_surface
        ssc_object.clear_system_plot()
        self.system_rendering_widget.delete_temp_file()

    def rendering_settings_process(self):
        self.rendering_settings_dialog.show()

    def save_image_process(self):
        surface: cairo.ImageSurface = self.system_rendering_widget.latest_surface
        if surface is None:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("'Save Image' has failed...")
            message_box.setText(f"There is no rendered image to be saved.")
            message_box.exec()
            return

        filename = QFileDialog.getSaveFileName(self, 'Save Image', '', "All Files (*);;"
                                                                       "PNG (*.png)")[0]
        if filename != '':
            array = get_ndarray_from_cairo_image_surface(surface)
            save_image_ndarray(array, filename)


class GraphicsScene(QGraphicsScene):

    def __init__(self, parent):
        super(GraphicsScene, self).__init__(parent)
        # self.setMinimumRenderSize(0)


class RenderingSettingsDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowTitle('Rendering Settings')

        self._set_options_widget()
        # self._set_button_box()

        layout = QVBoxLayout()
        layout.addWidget(self.scrollable_area)
        # layout.addWidget(self.button_box)
        self.setLayout(layout)
        # self.adjustSize()

    def _set_options_widget(self):
        self._set_available_systems_drop_down()
        self._set_line_area_options_groupbox()
        self._set_label_options_groupbox()
        self._set_object_options_groupbox()
        self.options_widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.available_systems_drop_down)
        self.image_scale_line_edit = RenderingSettingsLineEdit(6, 'Image resolution scale: ')
        layout.addWidget(self.image_scale_line_edit)
        layout.addWidget(self.line_area_groupbox)
        layout.addWidget(self.label_groupbox)
        layout.addWidget(self.object_groupbox)
        layout.addStretch()
        self.options_widget.setLayout(layout)

        self.scrollable_area = QScrollArea()
        self.scrollable_area.setWidget(self.options_widget)
        self.scrollable_area.setWidgetResizable(True)
        self.scrollable_area.adjustSize()
        self.scrollable_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollable_area.horizontalScrollBar().setEnabled(False)
        self.scrollable_area.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def _set_line_area_options_groupbox(self):
        self.line_area_groupbox = GroupBox('Line/Area Options')
        layout = QVBoxLayout()

        self.draw_orbit_limits_line_check_box = QCheckBox()
        self.draw_orbit_limits_line_check_box.setText('Show inner/outer orbit limits lines')
        self.draw_orbit_limits_line_check_box.setChecked(True)

        self.draw_tidal_locking_radius_check_box = QCheckBox()
        self.draw_tidal_locking_radius_check_box.setText('Show tidal locking radius')
        self.draw_tidal_locking_radius_check_box.setChecked(True)

        self.draw_water_frost_line_check_box = QCheckBox()
        self.draw_water_frost_line_check_box.setText('Show water frost-line')
        self.draw_water_frost_line_check_box.setChecked(True)

        self.draw_rock_line_check_box = QCheckBox()
        self.draw_rock_line_check_box.setText('Show rock-line')
        self.draw_rock_line_check_box.setChecked(True)

        self.draw_conservative_habitable_zone_check_box = QCheckBox()
        self.draw_conservative_habitable_zone_check_box.setText('Show conservative Habitable Zone')
        self.draw_conservative_habitable_zone_check_box.setChecked(True)

        self.draw_extended_habitable_zone_check_box = QCheckBox()
        self.draw_extended_habitable_zone_check_box.setText('Show extended Habitable Zone')
        self.draw_extended_habitable_zone_check_box.setChecked(True)

        self.draw_orbit_line_check_box = QCheckBox()
        self.draw_orbit_line_check_box.setText('Show orbit lines')
        self.draw_orbit_line_check_box.setChecked(True)

        self.orbit_line_width_line_edit = RenderingSettingsLineEdit(3, 'Orbit line width: ')

        layout.addWidget(self.draw_orbit_limits_line_check_box)
        layout.addWidget(self.draw_tidal_locking_radius_check_box)
        layout.addWidget(self.draw_water_frost_line_check_box)
        layout.addWidget(self.draw_rock_line_check_box)
        layout.addWidget(self.draw_conservative_habitable_zone_check_box)
        layout.addWidget(self.draw_extended_habitable_zone_check_box)
        layout.addWidget(self.draw_orbit_line_check_box)
        layout.addWidget(self.orbit_line_width_line_edit)
        layout.addStretch()
        self.line_area_groupbox.setLayout(layout)

    def _set_label_options_groupbox(self):
        self.label_groupbox = GroupBox('Label Options')
        layout = QVBoxLayout()

        self.draw_orbit_limits_labels_check_box = QCheckBox()
        self.draw_orbit_limits_labels_check_box.setText('Show inner/outer orbit limits labels')
        self.draw_orbit_limits_labels_check_box.setChecked(True)

        self.draw_other_line_labels_check_box = QCheckBox()
        self.draw_other_line_labels_check_box.setText('Show other lines distances')
        self.draw_other_line_labels_check_box.setChecked(True)

        self.draw_children_orbit_labels_check_box = QCheckBox()
        self.draw_children_orbit_labels_check_box.setText('Show children distances')
        self.draw_children_orbit_labels_check_box.setChecked(True)

        self.draw_children_name_labels_check_box = QCheckBox()
        self.draw_children_name_labels_check_box.setText('Show children names')
        self.draw_children_name_labels_check_box.setChecked(True)

        self.draw_parents_name_labels_check_box = QCheckBox()
        self.draw_parents_name_labels_check_box.setText('Show parent names')
        self.draw_parents_name_labels_check_box.setChecked(True)

        self.object_name_font_size_line_edit = RenderingSettingsLineEdit(10, 'Object name font size: ')
        self.line_distance_font_size_line_edit = RenderingSettingsLineEdit(10, 'Orbit label font size: ')

        layout.addWidget(self.draw_orbit_limits_labels_check_box)
        layout.addWidget(self.draw_other_line_labels_check_box)
        layout.addWidget(self.draw_children_orbit_labels_check_box)
        layout.addWidget(self.draw_children_name_labels_check_box)
        layout.addWidget(self.draw_parents_name_labels_check_box)
        layout.addWidget(self.object_name_font_size_line_edit)
        layout.addWidget(self.line_distance_font_size_line_edit)
        layout.addStretch()
        self.label_groupbox.setLayout(layout)

    def _set_object_options_groupbox(self):
        self.object_groupbox = GroupBox('Celestial Object Options')
        layout = QVBoxLayout()

        self.draw_parents_check_box = QCheckBox()
        self.draw_parents_check_box.setText('Show parents')
        self.draw_parents_check_box.setChecked(True)

        self.draw_children_check_box = QCheckBox()
        self.draw_children_check_box.setText('Show children')
        self.draw_children_check_box.setChecked(True)

        self.draw_asteroid_belt_check_box = QCheckBox()
        self.draw_asteroid_belt_check_box.setText('Show asteroid belts')
        self.draw_asteroid_belt_check_box.setChecked(True)

        self.draw_children_trojans_check_box = QCheckBox()
        self.draw_children_trojans_check_box.setText('Show children trojans')
        self.draw_children_trojans_check_box.setChecked(True)

        self.draw_children_satellites_check_box = QCheckBox()
        self.draw_children_satellites_check_box.setText('Show children satellites')
        self.draw_children_satellites_check_box.setChecked(True)

        self.satellite_display_distance_line_edit = RenderingSettingsLineEdit(
            0.1, 'Satellite display vertical distance: ')

        layout.addWidget(self.draw_parents_check_box)
        layout.addWidget(self.draw_children_check_box)
        layout.addWidget(self.draw_asteroid_belt_check_box)
        layout.addWidget(self.draw_children_trojans_check_box)
        layout.addWidget(self.draw_children_satellites_check_box)
        layout.addWidget(self.satellite_display_distance_line_edit)
        layout.addStretch()
        self.object_groupbox.setLayout(layout)

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
        self.available_systems_drop_down.model().sort(0)

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
        if not isinstance(ssc_obj, (PlanetarySystem, StellarSystem, MultiStellarSystemSType)):
            return
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
        if old_text_index >= 0:
            self.available_systems_drop_down.setItemText(old_text_index, text)
            for index in range(self.available_systems_drop_down.count()):
                if self.available_systems_drop_down.itemText(index).startswith(old_text):
                    new_index_text = self.available_systems_drop_down.itemText(index).replace(old_text, text)
                    self.available_systems_drop_down.setItemText(index, new_index_text)
        else:
            self.available_systems_drop_down.addItem(text)
        self.available_systems_drop_down.model().sort(0)

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
        # try:
        self.rendering_widget.render_image(self.ssc_object)
        # except Exception as e:
        #     message_box = QMessageBox()
        #     message_box.setIcon(QMessageBox.Information)
        #     message_box.setWindowTitle("'Rendering' has failed...")
        #     message_box.setText(f"Error message: {e}")
        #     message_box.exec()

        self.render_button.setEnabled(True)
        self.render_button.setIcon(button_icon)


class GraphicsView(QGraphicsView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_zoom_factor = 1
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event: QResizeEvent):
        # self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        # self.scene().setBackgroundBrush(self.backgroundBrush())
        # self.scene().update()
        # self.scene().setBackgroundBrush(Qt.blue)
        # self.setBackgroundBrush(self.scene().backgroundBrush())
        super().resizeEvent(event)

    def wheelEvent(self, event):
        """
        Zoom in or out of the view.
        """
        zoomInFactor = 1.1
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        # if 1000 > self.total_zoom_factor * zoomFactor > 0.5:
        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())
        self.total_zoom_factor *= zoomFactor


class RenderingSettingsLineEdit(QWidget):

    def __init__(self, default_value, label_string):
        self.default_value = default_value
        super().__init__()

        def line_edit_process(line_edit: QLineEdit):
            try:
                float(line_edit.text())
            except ValueError:
                line_edit.setText(str(default_value))

        self.line_edit = QLineEdit()
        self.line_edit.setText(str(default_value))
        self.line_edit.editingFinished.connect(partial(line_edit_process, self.line_edit))
        self.line_edit.setFixedWidth(50)

        self.label = QLabel(label_string)
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)

