import os.path
from functools import partial
from typing import Union

import pkg_resources
from PyQt5 import QtGui, QtCore
from PyQt5.Qt import QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter, QMessageBox, QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QApplication, \
    QTabBar

from stellar_system_creator.filing import load as load_ssc, load_ssc_light, load_system_rendering_preferences
from stellar_system_creator.gui.gui_image_rendering import SystemImageWidget
from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
from stellar_system_creator.gui.gui_theme import get_icon_with_theme_colors
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem


class CentralWidget(QTabWidget):

    def __init__(self):
        super().__init__()

        self.setTabPosition(QTabWidget.West)
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.tabBarDoubleClicked.connect(self.toggle_hide_tab_contents)
        self.tabCloseRequested.connect(self.close_tab)
        self.tabBar()

    def add_new_tab(self, filename: str):
        tab_content = QSplitter(Qt.Horizontal)
        if filename.endswith('.ssc'):
            ssc_object = load_ssc(filename)
            system_rendering_preferences = None
        else:
            ssc_object = load_ssc_light(filename)
            system_rendering_preferences = load_system_rendering_preferences(filename)
        tree_view = ProjectTreeView(ssc_object, filename)
        tab_header = self.make_tab_header(tree_view.ssc_object.name, tree_view, tab_content)

        left_side_widget = QWidget()
        left_side_layout = QVBoxLayout()
        left_side_layout.addWidget(tab_header)
        left_side_layout.addWidget(tree_view)
        left_side_layout.setContentsMargins(0, 0, 0, 0)
        left_side_layout.setSpacing(0)
        left_side_widget.setLayout(left_side_layout)

        right_side_widget = SystemImageWidget(tree_view, system_rendering_preferences)

        tab_content.addWidget(left_side_widget)
        tab_content.addWidget(right_side_widget)
        tab_content.setStretchFactor(0, 0)
        tab_content.setStretchFactor(1, 1)
        tab_content.setSizes([1.5*left_side_widget.sizeHint().width(),
                              1.5*right_side_widget.sizeHint().width()])

        # if platform.system() == 'Windows':
        #     seperator = '\\'
        # else:
        #     seperator = '/'
        # tab_label = filename.split(seperator)[-1].split('.')[0]
        tab_label = os.path.basename(filename).split('.')[0]
        tab_index = self.addTab(tab_content, tab_label)
        self.setCurrentIndex(tab_index)
        self.set_tab_button(tab_index)
        # tab_content.widget(0).hide()

    def set_tab_button(self, tab_index):
        new_button = CloseTabButton()
        new_button.pressed.connect(lambda: self.tabCloseRequested.emit(tab_index))
        self.tabBar().setTabButton(tab_index, self.tabBar().RightSide, new_button)

    def make_tab_header(self, label_text, tree_view, tab_content):
        tab_header = QWidget(self)
        layout = QHBoxLayout()

        class Label(QLabel):
            def __init__(self, *args, **kwargs):
                super(Label, self).__init__(*args, **kwargs)
                self.tab_dialolog = TabHeaderDialog(tree_view, self, tab_content)

            def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
                if a0.button() == QtCore.Qt.RightButton:
                    self.tab_dialolog.show()
                super().mousePressEvent(a0)

        label = Label(label_text)
        label.adjustSize()
        layout.addWidget(label)

        # hide_button_icon = self.style().standardIcon(getattr(QStyle, 'SP_TitleBarMinButton'))
        # hide_button = QPushButton(hide_button_icon, '', self)
        hide_button = TabMinimizeButton(parent=tab_header)
        # hide_button.setSize(hide_button.size().height(), 0.8*hide_button.size().width())

        hide_button.pressed.connect(self.toggle_hide_tab_contents)
        # hide_button.triggered.connect(self.toggle_hide_tab_contents)

        layout.addWidget(hide_button)
        layout.setStretch(0, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        tab_header.setLayout(layout)
        # tab_header.adjustSize()
        # tab_header.setFixedHeight(2*label.height())

        return tab_header

    def toggle_hide_tab_contents(self):
        tree_widget_of_current_tab: QWidget = self.widget(self.currentIndex()).widget(0)
        if not tree_widget_of_current_tab.isHidden():
            tree_widget_of_current_tab.hide()
        else:
            tree_widget_of_current_tab.show()

    def close_tab(self, i):
        ssc_object_name = self.get_ssc_object_of_current_tab().name
        if self.tabText(self.currentIndex()).startswith('*'):
            close_tab_reply = QMessageBox.question(self, 'Exit Project',
                                                   f"Are you sure you want to close {ssc_object_name}? "
                                                   f"Any changes made after last saving action,"
                                                   f" will be lost. Do you still want to close the project tab?",
                                                   QMessageBox.Yes | QMessageBox.Save | QMessageBox.No,
                                                   QMessageBox.No)
        else:
            close_tab_reply = QMessageBox.question(self, 'Exit Project',
                                                   f"Are you sure you want to close {ssc_object_name}?",
                                                   QMessageBox.Yes | QMessageBox.No,
                                                   QMessageBox.No)

        if close_tab_reply == QMessageBox.Save:
            from gui_menubar import save_project
            save_project(self.parent().menuBar().children()[0])

        if close_tab_reply == QMessageBox.No:
            return

        self.removeTab(i)

    def get_project_tree_view_of_current_tab(self) -> ProjectTreeView:
        tree_widget_of_current_tab: QWidget = self.widget(self.currentIndex()).widget(0)
        project_tree_view: ProjectTreeView = tree_widget_of_current_tab.findChild(ProjectTreeView)
        return project_tree_view

    def get_ssc_object_of_current_tab(self) -> Union[StellarSystem, PlanetarySystem]:
        project_tree_view = self.get_project_tree_view_of_current_tab()
        return project_tree_view.ssc_object


class TabMinimizeButton(QPushButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimize_icon()

    def set_minimize_icon(self):
        minimize_dir = pkg_resources.resource_filename('stellar_system_creator', 'gui/gui_icons/window-minimize.svg')
        self.setIcon(get_icon_with_theme_colors(minimize_dir))
        self.setStyleSheet("padding: 1px;")
        self.adjustSize()


class TabHeaderDialog(QDialog):

    def __init__(self, parent_item, header_label: QLabel, parent):
        from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
        self.parent_item: ProjectTreeView = parent_item
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle(f'{self.parent_item.ssc_object.name} details')
        self.header_label = header_label

        self._set_button_box()
        self._set_dialog_widget()

        layout = QVBoxLayout()
        layout.addWidget(self.dialog_widget)
        layout.addWidget(self.button_box)
        layout.addStretch()
        self.setLayout(layout)

    def _set_dialog_widget(self):
        self.dialog_widget = QWidget()

        self.name_line_edit = QLineEdit(self.parent_item.ssc_object.name)

        layout = QFormLayout()
        layout.addRow('Name', self.name_line_edit)
        self.dialog_widget.setLayout(layout)

    def _set_button_box(self):
        self.button_box = QDialogButtonBox((QDialogButtonBox.Cancel | QDialogButtonBox.Ok), self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Enter or a0.key() == Qt.Key_Return or a0.key() == Qt.Key_Escape:
            return
        super().keyPressEvent(a0)

    def accept(self) -> None:
        siw: SystemImageWidget = self.parent().findChild(SystemImageWidget)
        for i in range(siw.rendering_settings_dialog.available_systems_drop_down.count()):
            old_text = siw.rendering_settings_dialog.available_systems_drop_down.itemText(i)
            new_text = old_text.replace(self.header_label.text(), self.name_line_edit.text(), 1)
            siw.rendering_settings_dialog.available_systems_drop_down.setItemText(i, new_text)

        self.parent_item.ssc_object.name = self.name_line_edit.text()
        self.header_label.setText(self.name_line_edit.text())
        self.parent_item.model().parent().update_tab_title()
        super().accept()

    def reject(self) -> None:
        super().reject()


class CloseTabButton(QPushButton):

    def __init__(self, parent=None):
        super().__init__(parent)

        icon_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                   'gui/gui_icons/close.svg')
        current_palette = QApplication.instance().palette()
        self.setIcon(get_icon_with_theme_colors(icon_dir, current_palette))
        # self.setContentsMargins(0, 0, 0, 0)
        self.setCheckable(True)
        self.setStyleSheet("QPushButton:!hover{border: none;}")
        self.adjustSize()

