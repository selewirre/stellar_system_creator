import tempfile
from functools import partial
from typing import Union

import pkg_resources
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QMenu, QAction, QFileDialog, QSizePolicy

from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem

# https://stackoverflow.com/questions/57432570/generate-a-svg-file-with-pyqt5


class SystemRenderingWidget(QSvgWidget):

    def __init__(self):
        super().__init__()
        self.hide()

    def render_image(self, ssc_object: Union[StellarSystem, PlanetarySystem, None]):

        if ssc_object is not None:
            if ssc_object.parent is not None:
                self.hide()
                save_format = 'svg'
                with tempfile.NamedTemporaryFile("r+b", delete=True) as fd:
                    if isinstance(ssc_object, StellarSystem):
                        ssc_object.draw_stellar_system(save_fig=True, save_temp_file=fd, save_format=save_format)
                    elif isinstance(ssc_object, PlanetarySystem):
                        ssc_object.draw_planetary_system(save_fig=True, save_temp_file=fd, save_format=save_format)
                    fd.seek(0)
                    self.renderer().load(fd.name)
                ssc_object.fig = None
                ssc_object.ax = None
                self.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
                self.show()
            else:
                self.hide()
        else:
            self.hide()


class SystemImageWidget(QWidget):

    def __init__(self, tree_view: ProjectTreeView):
        super().__init__()
        self.tree_view = tree_view

        self.system_rendering_widget = SystemRenderingWidget()
        self._set_options_widget()

        layout = QVBoxLayout()

        layout.addWidget(self.options_widget)
        layout.addWidget(self.system_rendering_widget)
        layout.setAlignment(self.options_widget, Qt.AlignTop)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setStretchFactor(self.options_widget, 0)
        layout.setStretchFactor(self.system_rendering_widget, 1)
        # layout.sets
        self.setLayout(layout)

    def _set_options_widget(self):
        self.options_widget = QWidget(self)
        layout = QHBoxLayout()

        self.render_button = QPushButton(parent=self)
        render_dir = pkg_resources.resource_filename('stellar_system_creator', 'gui/logo.ico')
        self.render_button.setIcon(QIcon(render_dir))
        self.render_button.setStyleSheet("padding: 1px;")
        self.render_button.adjustSize()
        self.render_button.pressed.connect(self.render_process)
        self.render_thread = None

        layout.addWidget(self.render_button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.options_widget.setLayout(layout)
        self.options_widget.setFixedSize(self.options_widget.sizeHint())

    def render_process(self):
        self.render_thread = ImageRenderingProcess(self.tree_view, self.system_rendering_widget, self.render_button)
        self.render_thread.start()


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
