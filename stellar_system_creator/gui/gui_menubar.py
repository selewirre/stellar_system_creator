import platform
import sys
from functools import partial

import pkg_resources
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QMenuBar, QMessageBox, QDialog, QVBoxLayout, QToolBar, \
    QPushButton, QApplication, QSizePolicy

from stellar_system_creator.astrothings.units import ureg
from stellar_system_creator.filing import save as save_ssc_object, save_as_ssc_light, add_extension_if_necessary, \
    export_object_to_pdf, export_object_to_json, export_object_to_csv
from stellar_system_creator.gui.gui_central_widget import CentralWidget
from stellar_system_creator.gui.gui_image_rendering import SystemImageWidget
from stellar_system_creator.gui.gui_theme import get_icon_with_theme_colors, get_dark_theme_pallet, \
    get_light_theme_pallet
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
        self.addAction(self.export_as_project_action)
        self.addSeparator()
        self.addMenu(self.theme_submenu)
        self.theme_submenu.addAction(self.dark_theme_action)
        self.theme_submenu.addAction(self.light_theme_action)
        self.addSeparator()
        # self.addAction(self.settings_action)
        # if platform.system() == 'Windows':
        #     self.addAction(self.add_file_association_action)
        #     self.addSeparator()
        self.addAction(self.exit_action)

    def _connect_actions(self):
        self.new_project_multi_stellar_system_action.triggered.connect(
            partial(new_project, self, 'Multi-Stellar System'))
        self.new_project_stellar_system_action.triggered.connect(partial(new_project, self, 'Stellar System'))
        self.new_project_planetary_system_action.triggered.connect(partial(new_project, self, 'Planetary System'))

        self.open_project_action.triggered.connect(partial(open_project, self))
        self.save_project_action.triggered.connect(partial(save_project, self))
        self.save_as_project_action.triggered.connect(partial(save_as_project, self))
        self.export_as_project_action.triggered.connect(partial(export_as_project, self))

        self.dark_theme_action.triggered.connect(partial(change_theme, self, get_dark_theme_pallet))
        self.light_theme_action.triggered.connect(partial(change_theme, self, get_light_theme_pallet))

        self.add_file_association_action.triggered.connect(partial(add_file_association, sys.argv[0]))
        self.exit_action.triggered.connect(partial(exit_application, self))

        self.reset_menu_icons()

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

        self.export_as_project_action = QAction("Export Project As...", menubar)
        self.export_as_project_action.setShortcut('Ctrl+E')

        self.settings_action = QAction("&Settings...", menubar)

        self.theme_submenu = QMenu("&Theme", menubar)
        self.dark_theme_action = QAction("&Dark...", menubar)
        self.light_theme_action = QAction("&Light...", menubar)

        self.add_file_association_action = QAction("&Add File Association...", menubar)
        self.add_file_association_action.setToolTip('Associate *.ssc files with the Stellar System Creator.'
                                                    'Then, you can open them with this program by double-clicking'
                                                    ' on them.')

        self.exit_action = QAction(QIcon.fromTheme("application-exit"), "&Exit", menubar)
        # self.exit_action.setShortcut('Alt+F4')

    def reset_menu_icons(self):
        current_palette = QApplication.instance().palette()

        mss_icon_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                       'gui/gui_icons/Multi-Stellar-System.svg')
        self.new_project_multi_stellar_system_action.setIcon(get_icon_with_theme_colors(mss_icon_dir, current_palette))

        ss_icon_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                      'gui/gui_icons/Stellar-System.svg')
        self.new_project_stellar_system_action.setIcon(get_icon_with_theme_colors(ss_icon_dir, current_palette))

        ps_icon_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                      'gui/gui_icons/Planetary-System.png')
        self.new_project_planetary_system_action.setIcon(get_icon_with_theme_colors(ps_icon_dir, current_palette))

        new_project_icon_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                               'gui/gui_icons/new-folder.svg')
        self.new_project_submenu.setIcon(get_icon_with_theme_colors(new_project_icon_dir, current_palette))

        open_project_icon_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                                'gui/gui_icons/open-folder.svg')
        self.open_project_action.setIcon(get_icon_with_theme_colors(open_project_icon_dir, current_palette))

        save_project_icon_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                                'gui/gui_icons/save.svg')
        self.save_project_action.setIcon(get_icon_with_theme_colors(save_project_icon_dir, current_palette))

        export_project_icon_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                                  'gui/gui_icons/export-to.svg')
        self.export_as_project_action.setIcon(get_icon_with_theme_colors(export_project_icon_dir, current_palette))

        theme_icon_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                         'gui/gui_icons/color-palette.svg')
        self.theme_submenu.setIcon(get_icon_with_theme_colors(theme_icon_dir, current_palette))

        exit_icon_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                         'gui/gui_icons/shut-down.svg')
        self.exit_action.setIcon(get_icon_with_theme_colors(exit_icon_dir, current_palette))


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
        self.addAction(self.documentation_in_browser_action)
        self.addAction(self.documentation_pdf_action)

    def _connect_actions(self):
        # self.documentation_action.triggered.connect(open_documentation)
        self.documentation_action.triggered.connect(self.open_documentation_process)
        self.documentation_in_browser_action.triggered.connect(open_documentation_in_browser)
        self.documentation_pdf_action.triggered.connect(open_documentation_pdf)

    def _create_menu_actions(self, menubar):
        self.documentation_action = QAction("&Documentation", menubar)
        self.documentation_action.setShortcut('F1')

        self.documentation_in_browser_action = QAction("&Open Documentation in Browser", menubar)
        self.documentation_in_browser_action.setShortcut('Ctrl+F1')

        self.documentation_pdf_action = QAction("&Open Documentation PDF", menubar)
        self.documentation_pdf_action.setShortcut('Ctrl+Shift+F1')

        self.reset_menu_icons()

    def open_documentation_process(self, page_directory=None):
        if page_directory is not None:
            if page_directory:
                self.help_dialog.loadPage(page_directory)
        self.help_dialog.show()

    def reset_menu_icons(self):
        current_palette = QApplication.instance().palette()

        documentation_icon_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                                 'gui/gui_icons/help.svg')
        self.documentation_action.setIcon(get_icon_with_theme_colors(documentation_icon_dir, current_palette))


class HelpDialog(QDialog):
    """Source: https://zetcode.com/pyqt/qwebengineview/"""

    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle('Documentation')
        self.setModal(False)
        self.resize(600, 450)

        self._set_web_engine_view()
        self._set_toolbar()
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.web_engine_view)
        layout.addStretch()
        self.setLayout(layout)

        self.setWindowFlags(Qt.Window)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)

    def reset_toolbar(self):
        old_toolbar = self.toolbar
        old_toolbar.deleteLater()
        self._set_toolbar()
        self.layout().replaceWidget(old_toolbar, self.toolbar)

    def _set_toolbar(self):
        self.toolbar = QToolBar(self)
        current_palette = QApplication.instance().palette()

        # setting back button
        self.back_button = QPushButton()
        self.back_button.setEnabled(False)
        left_arrow_dir = pkg_resources.resource_filename('stellar_system_creator', 'gui/gui_icons/left-arrow.svg')
        self.back_button.setIcon(get_icon_with_theme_colors(left_arrow_dir, current_palette))
        self.back_button.clicked.connect(self.back_process)
        self.toolbar.addWidget(self.back_button)

        # setting forward button
        self.forward_button = QPushButton()
        self.forward_button.setEnabled(False)
        right_arrow_dir = pkg_resources.resource_filename('stellar_system_creator', 'gui/gui_icons/right-arrow.svg')
        self.forward_button.setIcon(get_icon_with_theme_colors(right_arrow_dir, self.palette()))
        self.forward_button.clicked.connect(self.forward_process)
        self.toolbar.addWidget(self.forward_button)

        # setting home button
        self.home_button = QPushButton()
        home_dir = pkg_resources.resource_filename('stellar_system_creator', 'gui/gui_icons/home.svg')
        self.home_button.setIcon(get_icon_with_theme_colors(home_dir, self.palette()))
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

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super().resizeEvent(a0)
        new_web_engine_view_height = self.height() - self.toolbar.size().height() - self.layout().spacing() \
            - self.layout().contentsMargins().bottom() - self.layout().contentsMargins().top()
        self.web_engine_view.resize(self.web_engine_view.width(), new_web_engine_view_height)


def new_project(parent, system_type):
    filename: str = QFileDialog.getSaveFileName(parent, 'Save Project', '',
                                                "Stellar System Creator Light Files (*.sscl);;"
                                                "Stellar System Creator Files (*.ssc);;"
                                                "All Files (*)")[0]
    system_name = filename.split('/')[-1].split('.')[0]
    if filename != '':
        filename = add_extension_if_necessary(filename, 'sscl')
        if system_type == 'Multi-Stellar System':
            parent_star1 = MainSequenceStar(system_name + '1', 1 * ureg.M_s)
            parent_star2 = MainSequenceStar(system_name + '2', 1 * ureg.M_s)
            parent_binary = StellarBinary(system_name, parent_star1, parent_star2, 500 * ureg.au, 0.6)
            ss1 = StellarSystem(system_name + '1', parent_star1)
            ss2 = StellarSystem(system_name + '2', parent_star2)
            ssc_object = MultiStellarSystemSType(system_name, parent_binary, [ss1, ss2])
        if system_type == 'Stellar System':
            parent_star = MainSequenceStar(system_name, 1 * ureg.M_s)
            ssc_object = StellarSystem(system_name, parent_star)
        elif system_type == 'Planetary System':
            parent_planet = Planet(system_name, 1 * ureg.M_e)
            ssc_object = PlanetarySystem(system_name, parent_planet)

        save_as_ssc_light(ssc_object, filename)
        central_widget: CentralWidget = parent.parent().parent().central_widget
        central_widget.add_new_tab(filename)
    else:
        return


def open_project(parent):
    central_widget: CentralWidget = parent.parent().parent().central_widget
    filename = QFileDialog.getOpenFileName(parent, 'Open Project(s)', '',
                                           "All Files (*);;Stellar System Creator Light Files (*.sscl);;"
                                           "Stellar System Creator Files (*.ssc)")[0]
    try:
        if filename != '':
            central_widget.add_new_tab(filename)
    except Exception as e:
        print(e)
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle("'Open Project' has failed...")
        message_box.setText(f"File '{filename}' is not compatible or does not exist.")
        message_box.exec()


def save_as_project(parent):
    central_widget: CentralWidget = parent.parent().parent().central_widget
    ssc_object = central_widget.get_ssc_object_of_current_tab()
    filename: str = QFileDialog.getSaveFileName(parent, 'Save Project', '',
                                                "Stellar System Creator Light Files (*.sscl);;"
                                                "Stellar System Creator Files (*.ssc);;"
                                                "All Files (*)")[0]
    if filename != '':
        if filename.endswith('.ssc'):
            save_ssc_object(ssc_object, filename)
        else:
            system_rendering_preferences = central_widget.currentWidget().findChild(SystemImageWidget). \
                rendering_settings_dialog.get_system_rendering_preferences()
            save_as_ssc_light(ssc_object, filename, system_rendering_preferences)
    else:
        return

    # updating the tab name and the project treeview name
    central_widget.get_project_tree_view_of_current_tab().filename = filename
    import os
    new_tab_label = os.path.basename(filename).split('.')[0]
    central_widget.setTabText(central_widget.currentIndex(), new_tab_label)


def save_project(parent):
    central_widget: CentralWidget = parent.parent().parent().central_widget
    ssc_object = central_widget.get_ssc_object_of_current_tab()
    filename = central_widget.get_project_tree_view_of_current_tab().filename
    if filename.endswith('.ssc'):
        saved = save_ssc_object(ssc_object, filename)
    else:
        system_rendering_preferences = central_widget.currentWidget().findChild(SystemImageWidget).\
            rendering_settings_dialog.get_system_rendering_preferences()
        saved = save_as_ssc_light(ssc_object, filename, system_rendering_preferences)
    tab_text = central_widget.tabText(central_widget.currentIndex())
    if saved and tab_text.startswith('*'):
        central_widget.setTabText(central_widget.currentIndex(), tab_text[1:])


def export_as_project(parent):
    central_widget: CentralWidget = parent.parent().parent().central_widget
    ssc_object = central_widget.get_ssc_object_of_current_tab()
    filename: str = QFileDialog.getSaveFileName(parent, 'Save Project', '',
                                                "Portable Document Files (*.pdf);;"
                                                "Comma-Separated Values (*.csv);;"
                                                "JavaScript Open Notation (*.json);;"
                                                "All Files (*)")[0]
    if filename != '':
        if filename.endswith('.pdf'):
            export_object_to_pdf(ssc_object, filename)
        elif filename.endswith('.csv'):
            export_object_to_csv(ssc_object, filename)
        elif filename.endswith('.json'):
            export_object_to_json(ssc_object, filename)
        else:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("'Export Project As' has failed...")
            message_box.setText(f"File '{filename}' does not end in .pdf, .csv, or .json.")
            message_box.exec()
    else:
        return


def change_theme(parent, get_theme_pallet):
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("No Qt Application found.")
    app.setStyle("Fusion")
    app.setPalette(get_theme_pallet())

    app = QApplication.instance()
    if app is None:
        raise RuntimeError("No Qt Application found.")
    app.setStyle("Fusion")

    menubar: MenuBar = parent.parent().parent().menubar
    helpmenu: HelpMenu = menubar.findChild(HelpMenu)
    helpmenu.reset_menu_icons()
    helpmenu.help_dialog.reset_toolbar()

    filemenu: FileMenu = menubar.findChild(FileMenu)
    filemenu.reset_menu_icons()

    central_widget: CentralWidget = parent.parent().parent().central_widget
    for i in range(central_widget.count()):
        central_widget.set_tab_button(i)
        central_widget.widget(i).children()[1].children()[1].children()[0].set_minimize_icon()


def exit_application(parent):
    central_widget: CentralWidget = parent.parent().parent().central_widget
    for i in range(central_widget.count()):
        central_widget.setCurrentIndex(i)
        central_widget.tabCloseRequested.emit(i)

    if central_widget.count() < 1:
        sys.exit()


def open_documentation_in_browser():
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


def open_documentation_pdf():
    filename = pkg_resources.resource_filename('stellar_system_creator',
                                               'documentation/build/latex/stellarsystemcreator.pdf')
    import subprocess, os, platform
    if platform.system() == 'Darwin':  # macOS
        subprocess.call(('open', filename))
    elif platform.system() == 'Windows':  # Windows
        os.startfile(filename)
        # subprocess.call(('start', filename), shell=True)
    else:  # linux variants
        subprocess.call(('xdg-open', filename))


def add_file_association(executable_filename):
    import subprocess, platform
    if platform.system() == 'Darwin':  # macOS
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle("'Adding file association' failed...")
        message_box.setText(f"This action is not yet supported on macOS.")
        message_box.exec()
    elif platform.system() == 'Windows':  # Windows
        import ctypes

        def is_admin():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False

        if not executable_filename.endswith('.exe'):
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("'Adding file association' failed...")
            message_box.setText(f"This action can not be performed for programs that do not end in *.exe.")
            message_box.exec()
        elif is_admin():
            script = f'assoc .ssc=sscfile && ftype sscfile=\"{executable_filename}\" \"%1\"'
            p = subprocess.Popen(["start", "cmd", "/k", script], shell=True)
        else:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("'Adding file association' failed...")
            message_box.setText(f"This action requires administrator privileges. Re-open the program"
                                f"with administrator privileges and try again.")
            message_box.exec()
    else:  # linux variants
        # https://askubuntu.com/questions/289337/how-can-i-change-file-association-globally
        # https://unix.stackexchange.com/questions/20075/how-do-i-change-file-associations-from-the-command-line
        # https://askubuntu.com/questions/179865/how-do-i-change-the-mime-type-for-a-file
        # https://help.ubuntu.com/community/AddingMimeTypes
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle("'Adding file association' failed...")
        message_box.setText(f"This action is not yet supported on this OS.")
        message_box.exec()
