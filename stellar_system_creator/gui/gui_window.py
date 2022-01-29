# example for menubar on https://realpython.com/python-menus-toolbars/
# example for gui of interest https://stackoverflow.com/questions/53157230/embed-a-matplotlib-plot-in-a-pyqt5-gui
# example of multi-windows pyqt5 https://www.learnpyqt.com/tutorials/creating-multiple-windows/
# example for plots with pyqtgraph https://www.mfitzp.com/tutorials/plotting-pyqtgraph/
# example for drag and drop https://pyshine.com/Drag-Drop-CSV-File-on-PyQt5-GUI/
# https://realpython.com/python-pyqt-layout/
# example on layout with splitter https://stackoverflow.com/questions/58822249/how-to-create-resizable-layout-ui-in-pyqt
# example on tabs https://www.geeksforgeeks.org/creating-a-tabbed-browser-using-pyqt5/
# contains many Qicons https://www.pythonguis.com/faq/built-in-qicons-pyqt/
# more Qicons https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
# example on threading https://realpython.com/python-pyqt-qthread/
# zoom in functionality https://stackoverflow.com/questions/47708282/zoom-functionality-using-qt/47710623#47710623
# context menu for treeview "https://wiki.python.org/moin/PyQt/Creating a context menu for a tree view"
# example on qdialog (popup windows) https://www.tutorialspoint.com/pyqt5/pyqt5_qdialog_class.htm
# example on dialogbuttonbox with tabwidget https://codetorial.net/en/pyqt5/widget/qtabwidget_advanced.html
# example on radiobutton https://pythonbasics.org/pyqt-radiobutton/
# example on qthread https://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
import datetime
import logging
import os
import sys
from functools import partial

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from stellar_system_creator.gui.gui_central_widget import CentralWidget
from stellar_system_creator.gui.gui_fancy_loader_screen import LoadingScreenImage
from stellar_system_creator.gui.gui_menubar import MenuBar
from stellar_system_creator.gui.gui_theme import get_dark_theme_pallet

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons


class Window(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None, filename: str = None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Stellar System Creator")
        self.resize(1000, 600)
        self.setWindowIcon(QtGui.QIcon('logo.ico'))

        # for drag and drop events
        self.setAcceptDrops(True)

        self.ls = LoadingScreenImage()
        self.ls.show()

        self.timer = QTimer()
        self.timer.timeout.connect(partial(self.loading, filename))
        self.timer.start(30)
        self.counts = 0

    def _setup(self):
        self._create_central_widget()
        self._create_menubar()

    def _create_central_widget(self):
        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)

    def _create_menubar(self):
        self.menubar = MenuBar()
        self.setMenuBar(self.menubar)

    def open_file(self, filename):
        if filename is not None:
            try:
                if filename != '':
                    self.central_widget.add_new_tab(filename)
            except Exception as e:
                print(e)
                message_box = QMessageBox()
                message_box.setIcon(QMessageBox.Information)
                message_box.setWindowTitle("'Open Project' has failed...")
                message_box.setText(f"File '{filename}' is not compatible or does not exist.")
                message_box.exec()

    def loading(self, filename: str):
        if self.counts == 0:
            self.ls.label.setText(f'Loading ... Initializing GUI')
            self.ls.label.resize(self.ls.label.sizeHint())
        elif self.counts == 1:
            self._setup()
            if isinstance(filename, str):
                self.ls.label.setText(f'Loading ... Opening File {os.path.basename(filename)}')
                self.ls.label.resize(self.ls.label.sizeHint())
        elif self.counts == 2:
            self.open_file(filename)
            self.ls.close()
            self.ls.deleteLater()
            self.show()
            self.timer.stop()
        else:
            self.ls.close()
            self.ls.deleteLater()
            self.show()
            self.timer.stop()

        self.counts += 1


class Application(QApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyle("Fusion")
        self.setPalette(get_dark_theme_pallet())


def run(filename=None):
    app = Application(sys.argv)
    win = Window(filename=filename)
    sys.exit(app.exec_())


def main(filename=None, divert_errors_to_log=False):
    if divert_errors_to_log:
        try:
            run(filename)
        except Exception:
            time = str(datetime.datetime.now())
            time = time.replace(' ', '_')
            time = time.replace('-', '_')
            time = time.replace(':', '_')
            time = time.replace('.', 'p')
            logging.basicConfig(filename=f'../Error_Report_{time}.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s')
            logging.error('A critical error occurred.', exc_info=True)
    else:
        run(filename)


if __name__ == "__main__":
    # https://stackoverflow.com/questions/162291/how-to-check-if-a-process-is-running-via-a-batch-script
    if len(sys.argv) == 1:
        file_name = None
    else:
        file_name = sys.argv[1]
        file_name = os.path.abspath(file_name)

    # filename = '../examples/output_files/QuezuliferhWideBinarySystem.sscl'
    main(file_name)
