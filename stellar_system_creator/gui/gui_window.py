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

import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from stellar_system_creator.gui.gui_menubar import MenuBar
from stellar_system_creator.gui.gui_central_widget import CentralWidget


class Window(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Solar System Creator")
        self.resize(1000, 1000)
        self.setWindowIcon(QtGui.QIcon('logo.ico'))

        # for drag and drop events
        self.setAcceptDrops(True)

        self._create_central_widget()
        self._create_menubar()

    def _create_central_widget(self):
        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)

    def _create_menubar(self):
        self.menubar = MenuBar()
        self.setMenuBar(self.menubar)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # app.setPalette(get_dark_theme_pallet())
    win = Window()
    import pkg_resources
    filename = '../examples/output_files/TrakunaStellarSystem.ssc'
    win.central_widget.add_new_tab(filename)
    win.show()
    # win.showMaximized()
    sys.exit(app.exec_())
