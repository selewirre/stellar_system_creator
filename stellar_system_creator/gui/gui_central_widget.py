from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter, QMessageBox

from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
from stellar_system_creator.gui.gui_image_rendering import SystemImageWidget
from PyQt5.Qt import QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

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

    def add_new_tab(self, filename):
        tree_view = ProjectTreeView(filename)
        tab_header = self.make_tab_header(tree_view.ssc_object.name)

        left_side_widget = QWidget()
        left_side_layout = QVBoxLayout()
        left_side_layout.addWidget(tab_header)
        left_side_layout.addWidget(tree_view)
        left_side_layout.setContentsMargins(0, 0, 0, 0)
        left_side_layout.setSpacing(0)
        left_side_widget.setLayout(left_side_layout)

        right_side_widget = SystemImageWidget(tree_view)

        tab_content = QSplitter(Qt.Horizontal)
        tab_content.addWidget(left_side_widget)
        tab_content.addWidget(right_side_widget)
        tab_content.setStretchFactor(0, 0)
        tab_content.setStretchFactor(1, 1)
        tab_content.setSizes([1.5*left_side_widget.sizeHint().width(),
                              1.5*right_side_widget.sizeHint().width()])

        tab_label = tree_view.filename.split('/')[-1].split('.')[0]
        tab_index = self.addTab(tab_content, tab_label)
        self.setCurrentIndex(tab_index)
        # tab_content.widget(0).hide()

    def make_tab_header(self, label_text):
        tab_header = QWidget(self)
        layout = QHBoxLayout()

        label = QLabel(label_text)
        label.adjustSize()
        layout.addWidget(label)
        # hide_button_icon = self.style().standardIcon(getattr(QStyle, 'SP_TitleBarMinButton'))
        # hide_button = QPushButton(hide_button_icon, '', self)
        hide_button = QPushButton('-', tab_header)
        hide_button.adjustSize()
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
        close_tab_reply = QMessageBox.question(self, 'Exit Project',
                                               f"Are you sure you want to close {ssc_object_name}? "
                                               f"If there were any changes made after last saving action,"
                                               f" they will be lost. Do you still want to close the project tab?",
                                               QMessageBox.Yes | QMessageBox.Save | QMessageBox.No,
                                               QMessageBox.No)

        if close_tab_reply == QMessageBox.No:
            return

        if close_tab_reply == QMessageBox.Save:
            from gui_menubar import save_project
            save_project(self.parent().menuBar().children()[0])

        self.removeTab(i)

    def get_project_tree_view_of_current_tab(self) -> ProjectTreeView:
        tree_widget_of_current_tab: QWidget = self.widget(self.currentIndex()).widget(0)
        project_tree_view: ProjectTreeView = tree_widget_of_current_tab.findChild(ProjectTreeView)
        return project_tree_view

    def get_ssc_object_of_current_tab(self) -> Union[StellarSystem, PlanetarySystem]:
        project_tree_view = self.get_project_tree_view_of_current_tab()
        ssc_object: Union[StellarSystem, PlanetarySystem] = project_tree_view.system_dict['Object']
        return ssc_object
