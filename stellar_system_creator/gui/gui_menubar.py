import codecs

import pkg_resources
import sys
from functools import partial

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QMenuBar, QMessageBox, QDialog, QVBoxLayout, QToolBar, \
    QPushButton, QSizePolicy, QHBoxLayout

from stellar_system_creator.astrothings.units import ureg
from stellar_system_creator.filing import save as save_ssc_object, add_extension_if_necessary
from stellar_system_creator.gui.gui_central_widget import CentralWidget
from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_body import MainSequenceStar, Planet
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem, MultiStellarSystemSType


class MenuBar(QMenuBar):

    def __init__(self):
        super().__init__()
        self._create_file_menu()

    def _create_file_menu(self):
        FileMenu(self)
        # EditMenu(self)
        # InsertMenu(self)
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
        self.new_project_submenu.addAction(self.new_project_multi_stellar_system_action)
        self.new_project_submenu.addAction(self.new_project_stellar_system_action)
        self.new_project_submenu.addAction(self.new_project_planetary_system_action)

        self.addAction(self.open_project_action)
        self.addAction(self.save_project_action)
        self.addAction(self.save_as_project_action)
        self.addSeparator()
        # self.addAction(self.settings_action)
        # self.addSeparator()
        self.addAction(self.exit_action)

    def _connect_actions(self):
        self.new_project_multi_stellar_system_action.triggered.connect(partial(new_project, self, 'Multi-Stellar System'))
        self.new_project_stellar_system_action.triggered.connect(partial(new_project, self, 'Stellar System'))
        self.new_project_planetary_system_action.triggered.connect(partial(new_project, self, 'Planetary System'))
        self.open_project_action.triggered.connect(partial(open_project, self))
        self.save_project_action.triggered.connect(partial(save_project, self))
        self.save_as_project_action.triggered.connect(partial(save_as_project, self))
        self.exit_action.triggered.connect(partial(exit_application, self))

    def _create_menu_actions(self, menubar):
        self.new_project_submenu = QMenu("&New Project", menubar)
        self.new_project_multi_stellar_system_action = QAction("&Multi-Stellar System...", menubar)
        self.new_project_stellar_system_action = QAction("&Stellar System...", menubar)
        self.new_project_planetary_system_action = QAction("&Planetary System...", menubar)

        self.open_project_action = QAction(QIcon.fromTheme("document-open"), "&Open Project...", menubar)
        self.open_project_action.setShortcut('Ctrl+O')

        self.save_project_action = QAction(QIcon.fromTheme("document-save"), "&Save Project", menubar)
        self.save_project_action.setShortcut('Ctrl+S')

        self.save_as_project_action = QAction(QIcon.fromTheme("document-save"), "&Save Project As...", menubar)
        self.save_as_project_action.setShortcut('Ctrl+Alt+S')

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
        self.help_dialog = HelpDialog(self)

    def _create_menu(self):
        self.addAction(self.documentation_action)

    def _connect_actions(self):
        # self.documentation_action.triggered.connect(open_documentation)
        self.documentation_action.triggered.connect(self.open_documentation_process)

    def _create_menu_actions(self, menubar):
        self.documentation_action = QAction("&Documentation", menubar)

    def open_documentation_process(self, page_directory=None):
        if page_directory is not None:
            if page_directory:
                self.help_dialog.loadPage(page_directory)
        self.help_dialog.show()


class HelpDialog(QDialog):
    """Source: https://zetcode.com/pyqt/qwebengineview/"""
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Documentation')
        self.setModal(False)
        self.setFixedSize(600, 450)

        self._set_web_engine_view()
        self._set_toolbar()
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.web_engine_view)
        layout.addStretch()
        self.setLayout(layout)

    def _set_toolbar(self):
        self.toolbar = QToolBar(self)

        # setting back button
        self.back_button = QPushButton()
        self.back_button.setEnabled(False)
        left_arrow_dir = pkg_resources.resource_filename('stellar_system_creator', 'gui/gui_icons/left-arrow.svg')
        self.back_button.setIcon(QIcon(left_arrow_dir))
        self.back_button.clicked.connect(self.back_process)
        self.toolbar.addWidget(self.back_button)

        # setting forward button
        self.forward_button = QPushButton()
        self.forward_button.setEnabled(False)
        right_arrow_dir = pkg_resources.resource_filename('stellar_system_creator', 'gui/gui_icons/right-arrow.svg')
        self.forward_button.setIcon(QIcon(right_arrow_dir))
        self.forward_button.clicked.connect(self.forward_process)
        self.toolbar.addWidget(self.forward_button)

        # setting home button
        self.home_button = QPushButton()
        home_dir = pkg_resources.resource_filename('stellar_system_creator', 'gui/gui_icons/home.svg')
        self.home_button.setIcon(QIcon(home_dir))
        self.home_button.clicked.connect(self.homing_process)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.home_button)

        self.toolbar.layout().setContentsMargins(0, 0, 0, 0)
        self.toolbar.layout().setSpacing(0)

    def _set_web_engine_view(self):
        self.web_engine_view = QWebEngineView()
        self.loadPage()
        self.web_engine_view.page().urlChanged.connect(self.loading_finished_process)
        # self.web_engine_view.page().titleChanged.connect(self.setWindowTitle)
        # self.windowTitleChanged.connect(self.setWindowTitle)

    def loadPage(self, page_directory='index.html'):
        filename = pkg_resources.resource_filename('stellar_system_creator',
                                                   f'documentation/build/html/{page_directory}')
        file = QUrl.fromLocalFile(filename)
        self.web_engine_view.load(file)

    def loading_finished_process(self):
        if self.web_engine_view.history().canGoBack():
            self.back_button.setEnabled(True)
        else:
            self.back_button.setEnabled(False)

        if self.web_engine_view.history().canGoForward():
            self.forward_button.setEnabled(True)
        else:
            self.forward_button.setEnabled(False)

    def back_process(self):
        self.web_engine_view.page().triggerAction(QWebEnginePage.Back)

    def forward_process(self):
        self.web_engine_view.page().triggerAction(QWebEnginePage.Forward)

    def homing_process(self):
        self.loadPage()


def new_project(parent, system_type):
    filename: str = QFileDialog.getSaveFileName(parent, 'Save Project')[0]
    system_name = filename.split('/')[-1].split('.')[0]
    if filename != '':
        filename = add_extension_if_necessary(filename, 'ssc')
        if system_type == 'Multi-Stellar System':
            parent_star1 = MainSequenceStar(system_name + '1', 1 * ureg.M_s)
            parent_star2 = MainSequenceStar(system_name + '2', 1 * ureg.M_s)
            parent_binary = StellarBinary(system_name, parent_star1, parent_star2, 500*ureg.au, 0.6)
            ss1 = StellarSystem(system_name + '1', parent_star1)
            ss2 = StellarSystem(system_name + '2', parent_star2)
            ssc_object = MultiStellarSystemSType(system_name, parent_binary, [ss1, ss2])
        if system_type == 'Stellar System':
            parent_star = MainSequenceStar(system_name, 1 * ureg.M_s)
            ssc_object = StellarSystem(system_name, parent_star)
        elif system_type == 'Planetary System':
            parent_planet = Planet(system_name, 1 * ureg.M_e)
            ssc_object = PlanetarySystem(system_name, parent_planet)

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


def save_as_project(parent):
    central_widget: CentralWidget = parent.parent().parent().central_widget
    ssc_object = central_widget.get_ssc_object_of_current_tab()
    filename: str = QFileDialog.getSaveFileName(parent, 'Save Project')[0]
    if filename != '':
        save_ssc_object(ssc_object, filename)
    else:
        return


def save_project(parent):
    central_widget: CentralWidget = parent.parent().parent().central_widget
    ssc_object = central_widget.get_ssc_object_of_current_tab()
    filename = central_widget.get_project_tree_view_of_current_tab().filename
    saved = save_ssc_object(ssc_object, filename)
    tab_text = central_widget.tabText(central_widget.currentIndex())
    if saved and tab_text.startswith('*'):
        central_widget.setTabText(central_widget.currentIndex(), tab_text[1:])


def exit_application(parent):
    central_widget: CentralWidget = parent.parent().parent().central_widget
    for i in range(central_widget.count()):
        central_widget.setCurrentIndex(i)
        central_widget.tabCloseRequested.emit(i)

    if central_widget.count() < 1:
        sys.exit()


def open_documentation():
    # filename = pkg_resources.resource_filename('stellar_system_creator',
    #                                            'documentation/build/latex/stellarsystemcreator.pdf')
    filename = pkg_resources.resource_filename('stellar_system_creator',
                                               'documentation/build/html/index.html')
    import subprocess, os, platform
    if platform.system() == 'Darwin':  # macOS
        subprocess.call(('open', filename))
    elif platform.system() == 'Windows':  # Windows
        os.startfile(filename)
        # subprocess.call(('start', filename), shell=True)
    else:  # linux variants
        subprocess.call(('xdg-open', filename))
