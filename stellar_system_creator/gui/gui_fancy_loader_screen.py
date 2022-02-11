import os

import pkg_resources
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, QFileInfo, Qt, QRect
from PyQt5.QtGui import QRegion, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QDesktopWidget, QLabel, QDialog


# This is if I wanted a video. Cool Idea but kind of too much?
class LoadingScreenVideo(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        self.setLayout(layout)

        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.stateChanged.connect(self.state_changed_process)

        file = QFileInfo('loading_screen.mp4').absoluteFilePath()
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file)))

        self.move_to_center_of_screen()

        rect = QRect(23, 20, 460, 460)
        my_region = QRegion(rect, QRegion.Ellipse)
        self.setMask(my_region)

    def state_changed_process(self):
        if not self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.play()

    def move_to_center_of_screen(self):
        self.resize(500, 500)
        rectangle = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        rectangle.moveCenter(center)
        self.move(rectangle.topLeft())


class LoadingScreenImage(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('logo.ico'))

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.image_widget = QLabel()
        loading_image_path_name = pkg_resources.resource_filename('stellar_system_creator', 'gui/brand_image_fancy.png')
        pixmap = QPixmap(os.path.abspath(loading_image_path_name))
        self.image_widget.setPixmap(pixmap)
        self.resize(self.image_widget.sizeHint())

        layout = QVBoxLayout()
        layout.addWidget(self.image_widget)
        self.setLayout(layout)

        self.label = QLabel('Loading... Please wait', self.image_widget)
        self.label.move(self.image_widget.width()/25, self.image_widget.height()/40)
        self.move_to_center_of_screen()

    def move_to_center_of_screen(self):
        rectangle = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        rectangle.moveCenter(center)
        self.move(rectangle.topLeft())

    def flush(self):
        pass
