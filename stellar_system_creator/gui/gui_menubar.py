import pkg_resources
import sys
from functools import partial

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QMenuBar, QMessageBox

from stellar_system_creator.filing import save as save_ssc_object, add_extension_if_necessary
from stellar_system_creator.gui.gui_central_widget import CentralWidget
from stellar_system_creator.solar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.solar_system_elements.solar_system import SolarSystem


class MenuBar(QMenuBar):

    def __init__(self):
        super().__init__()
        self._create_file_menu()

    def _create_file_menu(self):
        FileMenu(self)
        EditMenu(self)
        InsertMenu(self)
        HelpMenu(self)


class FileMenu(QMenu):

    def __init__(self, menubar):
        super().__init__("&File", menubar)
        menubar.addMenu(self)

        self._create_menu_actions(menubar)
        self._connect_actions()
        self._create_menu()

    def _create_menu(self):

        self.addMenu(self.new_project_submenu)
        self.new_project_submenu.addAction(self.new_project_solar_system_action)
        self.new_project_submenu.addAction(self.new_project_planetary_system_action)

        self.addAction(self.open_project_action)
        self.addAction(self.save_project_action)
        self.addSeparator()
        self.addAction(self.settings_action)
        self.addSeparator()
        self.addAction(self.exit_action)

    def _connect_actions(self):
        self.new_project_solar_system_action.triggered.connect(partial(new_project, self, 'Solar System'))
        self.new_project_planetary_system_action.triggered.connect(partial(new_project, self, 'Planetary System'))
        self.open_project_action.triggered.connect(partial(open_project, self))
        self.save_project_action.triggered.connect(partial(save_project, self))
        self.exit_action.triggered.connect(partial(exit_application, self))

    def _create_menu_actions(self, menubar):
        self.new_project_submenu = QMenu("&New Project", menubar)
        self.new_project_solar_system_action = QAction("&Solar System...", menubar)
        self.new_project_planetary_system_action = QAction("&Planetary System...", menubar)

        self.open_project_action = QAction(QIcon.fromTheme("document-open"), "&Open Project...", menubar)
        self.open_project_action.setShortcut('Ctrl+O')

        self.save_project_action = QAction(QIcon.fromTheme("document-save"), "&Save Project...", menubar)
        self.save_project_action.setShortcut('Ctrl+S')

        self.settings_action = QAction("&Settings...", menubar)

        self.exit_action = QAction(QIcon.fromTheme("application-exit"), "&Exit", menubar)
        # self.exit_action.setShortcut('Alt+F4')


class EditMenu(QMenu):

    def __init__(self, menubar):
        super().__init__("&Edit", menubar)
        menubar.addMenu(self)

        self._create_menu_actions(menubar)
        self._create_menu()

    def _create_menu(self):

        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addSeparator()

        self.addAction(self.cut_action)
        self.addAction(self.copy_action)
        self.addAction(self.paste_action)
        self.addAction(self.delete_action)
        self.addSeparator()

        self.addAction(self.find_action)
        self.addAction(self.replace_action)
        self.addAction(self.find_all_action)
        self.addAction(self.replace_all_action)
        self.addSeparator()

        self.addAction(self.select_all_action)

    def _create_menu_actions(self, menubar):
        self.undo_action = QAction(QIcon.fromTheme("edit-undo"), "&Undo", menubar)
        self.undo_action.setShortcut('Ctrl+Z')

        self.redo_action = QAction(QIcon.fromTheme("edit-redo"), "&Redo", menubar)
        self.redo_action.setShortcut('Ctrl+Y')

        self.cut_action = QAction(QIcon.fromTheme("edit-cut"), "&Cut", menubar)
        self.cut_action.setShortcut('Ctrl+X')

        self.copy_action = QAction(QIcon.fromTheme("edit-copy"), "&Copy", menubar)
        self.copy_action.setShortcut('Ctrl+C')

        self.paste_action = QAction(QIcon.fromTheme("edit-paste"), "&Paste", menubar)
        self.paste_action.setShortcut('Ctrl+V')

        self.delete_action = QAction(QIcon.fromTheme("edit-delete"), "&Delete", menubar)
        self.delete_action.setShortcut('Delete')

        self.find_action = QAction(QIcon.fromTheme("edit-find"), "&Find...", menubar)
        self.find_action.setShortcut('Ctrl+F')

        self.replace_action = QAction(QIcon.fromTheme("edit-find-replace"), "&Replace...", menubar)
        self.replace_action.setShortcut('Ctrl+R')

        self.find_all_action = QAction("&Find in all projects...", menubar)
        self.find_all_action.setShortcut('Ctrl+Shift+F')

        self.replace_all_action = QAction("&Replace in all projects...", menubar)
        self.replace_all_action.setShortcut('Ctrl+Shift+R')

        self.select_all_action = QAction(QIcon.fromTheme("edit-select-all"), "&Select All", menubar)
        self.select_all_action.setShortcut('Ctrl+A')


class InsertMenu(QMenu):

    def __init__(self, menubar):
        super().__init__("&Insert", menubar)
        menubar.addMenu(self)

        self._create_menu_actions(menubar)
        self._create_menu()

    def _create_menu(self):

        self.addAction(self.star_action)
        self.addSeparator()
        self.addAction(self.planet_action)
        self.addAction(self.asteroid_belt_action)
        self.addSeparator()
        self.addAction(self.satellite_action)
        self.addAction(self.trojan_action)

    def _create_menu_actions(self, menubar):
        self.star_action = QAction("&Star...", menubar)
        self.planet_action = QAction("&Planet...", menubar)
        self.asteroid_belt_action = QAction("&Asteroid Belt...", menubar)
        self.satellite_action = QAction("&Satellite...", menubar)
        self.trojan_action = QAction("&Trojan...", menubar)


class HelpMenu(QMenu):

    def __init__(self, menubar):
        super().__init__("&Help", menubar)
        menubar.addMenu(self)

        self._create_menu_actions(menubar)
        self._connect_actions()
        self._create_menu()

    def _create_menu(self):
        self.addAction(self.documentation_action)

    def _connect_actions(self):
        self.documentation_action.triggered.connect(open_documentation)

    def _create_menu_actions(self, menubar):
        self.documentation_action = QAction("&Documentation", menubar)


def new_project(parent, system_type):
    filename: str = QFileDialog.getSaveFileName(parent, 'Save Project')[0]
    system_name = filename.split('/')[-1].split('.')[0]
    if filename != '':
        filename = add_extension_if_necessary(filename, 'ssc')
        if system_type == 'Solar System':
            ssc_object = SolarSystem(system_name)
        elif system_type == 'Planetary System':
            ssc_object = PlanetarySystem(system_name)

        save_ssc_object(ssc_object, filename)
        central_widget: CentralWidget = parent.parent().parent().central_widget
        central_widget.add_new_tab(filename)
    else:
        return


def open_project(parent):
    central_widget: CentralWidget = parent.parent().parent().central_widget
    filename = QFileDialog.getOpenFileName(parent, 'Open Project(s)', '', "All Files (*);;Python Files (*.ssc)")[0]
    try:
        central_widget.add_new_tab(filename)
    except Exception:
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle("'Open Project' has failed...")
        message_box.setText(f"File '{filename}' is not compatible.")
        message_box.exec()


def save_project(parent):
    central_widget: CentralWidget = parent.parent().parent().central_widget
    ssc_object = central_widget.get_ssc_object_of_current_tab()
    filename: str = QFileDialog.getSaveFileName(parent, 'Save Project')[0]
    if filename != '':
        save_ssc_object(ssc_object, filename)
    else:
        return


def exit_application(parent):
    central_widget: CentralWidget = parent.parent().parent().central_widget
    for i in range(central_widget.count()):
        central_widget.setCurrentIndex(i)
        central_widget.tabCloseRequested.emit(i)

    if central_widget.count() < 1:
        sys.exit()


def open_documentation():
    filename = pkg_resources.resource_filename('stellar_system_creator',
                                               'documentation/stellar_system_creator_documentation.pdf')
    import subprocess, os, platform
    if platform.system() == 'Darwin':  # macOS
        subprocess.call(('open', filename))
    elif platform.system() == 'Windows':  # Windows
        os.startfile(filename)
        # subprocess.call(('start', filename), shell=True)
    else:  # linux variants
        subprocess.call(('xdg-open', filename))
