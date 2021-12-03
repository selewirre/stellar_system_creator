# example for menubar on https://realpython.com/python-menus-toolbars/
# example for gui of interest https://stackoverflow.com/questions/53157230/embed-a-matplotlib-plot-in-a-pyqt5-gui
# example of multi-windows pyqt5 https://www.learnpyqt.com/tutorials/creating-multiple-windows/
# example for plots with pyqtgraph https://www.mfitzp.com/tutorials/plotting-pyqtgraph/
# example for drag and drop https://pyshine.com/Drag-Drop-CSV-File-on-PyQt5-GUI/

import sys

from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread
from PyQt5 import QtGui
# import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMenu, QAction, QFileDialog, QMdiArea, QMdiSubWindow, \
    QPushButton, QMessageBox, QWidget, QGridLayout, QVBoxLayout, QLineEdit, QCheckBox, QSizePolicy, QHBoxLayout
from PyQt5.QtGui import QPixmap, QDoubleValidator, QPalette, QColor, QIntValidator
from PIL import ImageQt, Image
from functools import partial


class RGBValidator(QDoubleValidator):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setBottom(0)
        self.setTop(255)

    def validate(self, p_str, p_int):

        if not p_str:
            return QIntValidator.Intermediate, p_str, p_int

        if self.bottom() <= float(p_str) <= self.top():
            return QIntValidator.Acceptable, p_str, p_int
        else:
            return QIntValidator.Invalid, p_str, p_int


class Window(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Solar System Creator")
        self.resize(600, 450)
        self.setWindowIcon(QtGui.QIcon('logo.ico'))
        # self.centralWidget = QLabel("Hello, World")
        # self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # self.setCentralWidget(self.centralWidget)

        # for drag and drop events
        self.setAcceptDrops(True)

        # self._create_mdi_area()
        # self.setCentralWidget(self.mdi_area)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self._creat_panels()
        self._create_option_panel_widgets()
        self._create_actions()
        self._connect_actions()
        self._create_menubar()

    def dragEnterEvent(self, e):
        """
        This function will detect the drag enter event from the mouse on the main window
        """
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        """
        This function will detect the drag move event on the main window
        """
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """
        This function will enable the drop file directly on to the
        main window. The file location will be stored in the self.filename
        """
        if e.mimeData().hasUrls:
            e.setDropAction(Qt.CopyAction)
            e.accept()
            filenames = []
            for url in e.mimeData().urls():
                filenames.append(str(url.toLocalFile()))
            if len(filenames) > 1:
                e.ignore()
            else:
                self.open_file(filenames[0])
        else:
            e.ignore()

    def resizeEvent(self, event):
        if self.input_pixmap is not None:
            self.open_file(self.input_filename)
        if self.output_image is not None:
            self.output_pixmap = QPixmap.fromImage(ImageQt.ImageQt(self.output_image))
            self.output_pixmap = self.output_pixmap.scaled(self.output_panel.width(), self.output_panel.height(),
                                                           Qt.KeepAspectRatio, Qt.FastTransformation)
            self.output_panel.setPixmap(self.output_pixmap)

    def _create_mdi_area(self):
        self.mdi_area = QMdiArea()

    def _creat_panels(self):

        self.options_panel = QWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.options_panel.setSizePolicy(sizePolicy)

        self.input_panel = QLabel("Input", alignment=Qt.AlignCenter)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.input_panel.setSizePolicy(sizePolicy)

        self.output_panel = QLabel("Output", alignment=Qt.AlignCenter)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.output_panel.setSizePolicy(sizePolicy)

        # gridlayout = QHBoxLayout(self.mdi_area)
        gridlayout = QHBoxLayout(self.central_widget)

        for panel, c in zip((self.options_panel, self.input_panel, self.output_panel), (1,1,1)):
            gridlayout.addWidget(panel, c)

        self.input_pixmap = None
        self.output_pixmap = None
        self.input_filename = ''
        self.output_image: Image.Image = None

    def _create_option_panel_widgets(self):
        self.go_button = QPushButton('Go!')
        self.go_button.clicked.connect(self.on_go_button_click)

        luminescence_stop_label = QLabel('Luminescence stop: ')
        self.luminescence_stop_editable_text = QLineEdit()
        self.luminescence_stop_editable_text.setValidator(RGBValidator())
        self.luminescence_stop_editable_text.setText('90')
        self.luminescence_stop_editable_text.setMaximumWidth(100)

        transparency_decay_label = QLabel('Transparency Power Decay: ')
        self.transparency_decay_editable_text = QLineEdit()
        validator = QDoubleValidator()
        validator.setBottom(0)
        self.transparency_decay_editable_text.setValidator(validator)
        self.transparency_decay_editable_text.setText('0.9')
        self.transparency_decay_editable_text.setMaximumWidth(100)

        self.status_label = QLabel('Status: ')
        self.status_text = QLabel('Waiting for input')
        self.status_text.setWordWrap(True)
        self.status_text.setMaximumWidth(300)
        self.status_text.setMinimumWidth(300)

        grid = QGridLayout()
        grid.setSpacing(20)

        grid.addWidget(self.go_button, 1, 1)
        grid.addWidget(luminescence_stop_label, 2, 1)
        grid.addWidget(self.luminescence_stop_editable_text, 2, 2)
        grid.addWidget(transparency_decay_label, 3, 1)
        grid.addWidget(self.transparency_decay_editable_text, 3, 2)
        grid.addWidget(self.status_label, 4, 1)
        grid.addWidget(self.status_text, 4, 2)

        self.options_panel.setLayout(grid)

    def _create_menubar(self):
        menubar = self.menuBar()
        filemenu = QMenu("&File", self)
        menubar.addMenu(filemenu)

        filemenu.addAction(self.open_action)
        filemenu.addSeparator()
        filemenu.addAction(self.save_action)

    def _create_actions(self):
        self.open_action = QAction("&Open", self)
        self.open_action.setShortcut('Ctrl+O')
        self.save_action = QAction("&Save As", self)
        self.save_action.setShortcut('Ctrl+S')

    def _connect_actions(self):
        self.open_action.triggered.connect(self.open_file_from_file_dialog)
        self.save_action.triggered.connect(self.save_file_from_file_dialog)

    def open_file_from_file_dialog(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File(s)')[0]
        self.open_file(filename)

    def open_file(self, filename):
        if filename != '':
            self.status_text.setText('Getting input image...')
            self.input_filename = filename
            self.input_pixmap = QPixmap(filename)
            self.input_pixmap = self.input_pixmap.scaled(self.input_panel.width(), self.input_panel.height(),
                                                         Qt.KeepAspectRatio, Qt.FastTransformation)
            self.input_panel.setPixmap(self.input_pixmap)
            self.status_text.setText('Got input image.')

    def save_file_from_file_dialog(self):
        if self.output_image is not None:
            filename: str = QFileDialog.getSaveFileName(self, 'Save File')[0]
            if filename != '':
                if filename.split('.')[-1] != 'png':
                    filename += '.png'
                self.output_image.save(filename)
        else:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("'Save As' has failed...")
            message_box.setText('No processed image was find.')
            message_box.exec()

    def on_go_button_click(self):
        if self.input_filename != '':
            self.go_button.setEnabled(False)
            self.setup_image_processing_thread()
            self.thread.start()
        else:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("'Go!' has failed...")
            message_box.setText('No input image was find.')
            message_box.exec()

    def setup_image_processing_thread(self):
        luminescence_stop = int(self.luminescence_stop_editable_text.text())
        transparency_decay = float(self.transparency_decay_editable_text.text())

        self.thread = QThread()
        # self.worker = ImageProcessingWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(partial(self.worker.run, self.input_filename, luminescence_stop,
                                            transparency_decay))

        self.worker.finished.connect(self.on_finished_image_processing)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.report_image_processing_progress)

    def on_finished_image_processing(self, output_image):
        self.output_image = output_image
        self.output_pixmap = QPixmap.fromImage(ImageQt.ImageQt(self.output_image))
        self.output_pixmap = self.output_pixmap.scaled(self.output_panel.width(), self.output_panel.height(),
                                                       Qt.KeepAspectRatio, Qt.FastTransformation)
        self.output_panel.setPixmap(self.output_pixmap)
        self.thread.finished.connect(lambda: self.go_button.setEnabled(True))

    def report_image_processing_progress(self, signal):
        self.status_text.setText(signal)


def get_dark_theme_pallet() -> QPalette:

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    palette.setColor(QPalette.Disabled, QPalette.Shadow, Qt.black)

    # QPalette.

    return palette


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(get_dark_theme_pallet())

    win = Window()

    win.showMaximized()
    sys.exit(app.exec_())
