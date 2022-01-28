from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QApplication


def get_dark_theme_pallet() -> QPalette:

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
    # palette.setColor(QPalette.Disabled, QPalette.Shadow, Qt.black)
    palette.setColor(QPalette.Active, QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
    palette.setColor(QPalette.Disabled, QPalette.WindowText, Qt.darkGray)
    palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
    palette.setColor(QPalette.Disabled, QPalette.Light, QColor(53, 53, 53))

    return palette


def get_light_theme_pallet() -> QPalette:
    palette = QPalette()
    return palette


def get_icon_with_theme_colors(source_dir: str, palette: Union[QPalette, None] = None) -> QIcon:
    if palette is None:
        palette = QApplication.instance().palette()
    if palette.color(QPalette.ButtonText) == Qt.white:
        image = QImage(source_dir)
        image.invertPixels(QImage.InvertRgb)
        pixmap = QPixmap.fromImage(image)
        return QIcon(pixmap)
    else:
        return QIcon(source_dir)
