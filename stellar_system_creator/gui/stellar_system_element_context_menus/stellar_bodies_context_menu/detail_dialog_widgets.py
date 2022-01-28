from functools import partial
from typing import Union, Dict, List

import cairocffi
import cairocffi as cairo
import pkg_resources
from PyQt5.QtGui import QPixmap
from bs4 import BeautifulSoup
import codecs

import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QGroupBox, QWidget, QComboBox, QLineEdit, QLabel, QTextBrowser, QSizePolicy, \
    QCheckBox, QTabBar, QStylePainter, QStyleOptionTab, QStyle, QTabWidget, QScrollArea, \
    QRadioButton, QPushButton, QFileDialog, QToolTip, QBoxLayout, QVBoxLayout

from stellar_system_creator.astrothings.radius_models.planetary_radius_model import planet_compositions
from stellar_system_creator.astrothings.units import Q_
from bidict import bidict

from stellar_system_creator.astrothings.insolation_models.insolation_models import InsolationThresholdModel
from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
from stellar_system_creator.stellar_system_elements.stellar_body import StellarBody, Star, Planet, Satellite, Ring
from stellar_system_creator.visualization.drawing_tools import GradientColor
from stellar_system_creator.visualization.system_plot import add_ring_path_part, get_ndarray_from_cairo_image_surface

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons


class DetailsLabel(QLabel):
    def __init__(self, text: str, relative_tooltip_url_directory: str):
        text = f"ⓘ {text}"

        super().__init__(text)

        self.documentation_filename = relative_tooltip_url_directory
        self.setToolTip('Double-click for more info.')

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        from stellar_system_creator.gui.gui_window import Window
        from stellar_system_creator.gui.gui_menubar import HelpMenu
        # noinspection PyTypeChecker
        window_widget: Window = self.parent().parent().parent().parent().parent().parent().parent(). \
            parent().parent().parent().parent().parent()
        help_menu: HelpMenu = window_widget.menubar.findChild(HelpMenu)
        help_menu.open_documentation_process(self.documentation_filename)


class DetailsGroupBox(QGroupBox):
    def __init__(self, text: str, relative_tooltip_url_directory: str):
        text = f"ⓘ {text}"
        super().__init__(text)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.documentation_filename = relative_tooltip_url_directory
        self.setToolTip('Double-click for more info.')

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        from stellar_system_creator.gui.gui_window import Window
        from stellar_system_creator.gui.gui_menubar import HelpMenu
        # noinspection PyTypeChecker
        window_widget: Window = self.parent().parent().parent().parent().parent().parent(). \
            parent().parent().parent().parent().parent()
        help_menu: HelpMenu = window_widget.menubar.findChild(HelpMenu)
        help_menu.open_documentation_process(self.documentation_filename)


class UnitLineEdit(QWidget):

    def __init__(self, sse: Union[StellarBody, StellarBinary], value_name: str, influenced_labels: Dict, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.sse = sse
        self.value_name = value_name
        self.value: Q_ = self.get_value()

        self._set_unit_drop_menu()
        self._set_line_edit()

        layout = QHBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.unit_drop_menu)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.unit_drop_menu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedSize(150, self.sizeHint().height())
        self.unit_drop_menu.setFixedWidth(75)

        self.influenced_labels = influenced_labels

    def get_value(self) -> Q_:
        return self.sse.__dict__[self.value_name]

    def _set_unit_drop_menu(self):
        self.unit_drop_menu = UnitComboBox()
        self.dict_pretty = bidict({})
        self.dict_pretty, unit_str = get_unit_bidict(self.value)
        self.unit_drop_menu.addItems(list(self.dict_pretty.inverse.keys()))
        self.unit_drop_menu.setCurrentText(self.dict_pretty[unit_str])
        self.unit_drop_menu.currentTextChanged.connect(self.change_drop_menu_text_action)

    def _set_line_edit(self):
        self.line_edit = QLineEdit(get_value_string(self.value))
        self.line_edit.editingFinished.connect(self.change_text_action)
        # self.line_edit.inputRejected.connect(self.keep_old_text_action)

    def change_text_action(self, process_change=True) -> None:
        if self.hasFocus() or self.line_edit.hasFocus() \
                or self.previousInFocusChain() or self.line_edit.previousInFocusChain():
            try:
                self.sse.__dict__[self.value_name] = \
                    Q_(float(self.line_edit.text()), self.dict_pretty.inverse[self.unit_drop_menu.currentText()])
                if process_change:
                    self.sse.__post_init__()
                    for key in self.influenced_labels:
                        self.influenced_labels[key].update_text()
            except Exception:
                self.keep_old_text_action()

    def keep_old_text_action(self) -> None:
        if self.hasFocus() or self.line_edit.hasFocus():
            units = self.dict_pretty.inverse[self.unit_drop_menu.currentText()]
            self.value = self.get_value().to(units)
            self.line_edit.setText(get_value_string(self.value))

    def change_drop_menu_text_action(self):
        new_units = self.dict_pretty.inverse[self.unit_drop_menu.currentText()]
        self.value = self.value.to(new_units)
        self.line_edit.setText(get_value_string(self.value))

    def set_to_nan(self, process_change=True):
        new_units = self.dict_pretty.inverse[self.unit_drop_menu.currentText()]
        self.value = self.value.to(new_units) * np.nan
        self.line_edit.setText(get_value_string(self.value))
        self.sse.__dict__[self.value_name] = \
            Q_(float(self.line_edit.text()), self.dict_pretty.inverse[self.unit_drop_menu.currentText()])
        if process_change:
            self.sse.__post_init__()
            for key in self.influenced_labels:
                self.influenced_labels[key].update_text()


class UnitLabel(QWidget):

    def __init__(self, sse: Union[StellarBody, StellarBinary, InsolationThresholdModel],
                 value_name: str, sub_value_name: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sse = sse
        self.value_name = value_name
        self.sub_value_name = sub_value_name
        self.sizeflag = 0
        self.value: Q_ = self.get_value()

        self._set_unit_drop_menu()
        self._set_label()

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.unit_drop_menu)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.unit_drop_menu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if not self.sizeflag:
            self.setFixedSize(150, self.sizeHint().height())
        else:
            layout.addStretch()
            # self.setFixedSize(600, self.sizeHint().height())
        self.unit_drop_menu.setFixedWidth(75)

    def get_value(self) -> Q_:
        if isinstance(self.sse, dict):
            if isinstance(self.sse[self.value_name], dict) and self.sub_value_name is not None:
                return self.sse[self.value_name][self.sub_value_name]
        elif isinstance(self.sse.__dict__[self.value_name], dict) and self.sub_value_name is not None:
            return self.sse.__dict__[self.value_name][self.sub_value_name]
        elif self.sub_value_name is not None:
            return self.sse.__dict__[self.value_name].__dict__(self.sub_value_name)
        else:
            if isinstance(self.sse.__dict__[self.value_name], dict):
                self.sizeflag = 1
            return self.sse.__dict__[self.value_name]

    def _set_unit_drop_menu(self):
        self.unit_drop_menu = UnitComboBox()
        self.dict_pretty = bidict({})
        self.dict_pretty, unit_str = get_unit_bidict(self.value)
        self.unit_drop_menu.addItems(list(self.dict_pretty.inverse.keys()))
        self.unit_drop_menu.setCurrentText(self.dict_pretty[unit_str])
        self.unit_drop_menu.currentTextChanged.connect(self.update_text)

    def _set_label(self):
        self.label = QLabel(get_value_string(self.value))

    def update_text(self):
        units = self.dict_pretty.inverse[self.unit_drop_menu.currentText()]
        self.value = self.get_value()
        if self.sizeflag:
            self.value = {key: self.value[key].to(units) for key in self.value}
        else:
            self.value = self.value.to(units)
        self.label.setText(get_value_string(self.value))


class LineEdit(QLineEdit):

    def __init__(self, sse: Union[StellarBody, StellarBinary], value_name: str, influenced_labels: Dict, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.sse = sse
        self.value_name = value_name
        self.setText(get_value_string_no_unit(self.sse.__dict__[self.value_name]))
        self.editingFinished.connect(self.change_text_action)
        self.setFixedSize(150, self.sizeHint().height())
        # self.inputRejected.connect(self.keep_old_text_action)

        self.influenced_labels = influenced_labels

    def change_text_action(self, process_change=True) -> None:
        if self.hasFocus() or self.previousInFocusChain():
            text = self.text()
            try:
                value = float(text)
            except ValueError:
                value = text

            if isinstance(value, float):
                value_type = (float, int)
            else:
                value_type = type(value)
            if not isinstance(self.sse.__dict__[self.value_name], value_type):
                self.keep_old_text_action()
            else:
                self.sse.__dict__[self.value_name] = value
                if process_change:
                    self.sse.__post_init__()
                    for key in self.influenced_labels:
                        self.influenced_labels[key].update_text()

    def keep_old_text_action(self) -> None:
        if self.hasFocus():
            self.setText(get_value_string_no_unit(self.get_value()))

    def get_value(self):
        return self.sse.__dict__[self.value_name]

    def set_to_nan(self, process_change=True):
        self.setText(str(np.nan))
        self.sse.__dict__[self.value_name] = np.nan
        if process_change:
            self.sse.__post_init__()
            for key in self.influenced_labels:
                self.influenced_labels[key].update_text()


class Label(QLabel):

    def __init__(self, sse: Union[StellarBody, StellarBinary, InsolationThresholdModel],
                 value_name: str, sub_value_name: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sse = sse
        self.value_name = value_name
        self.sub_value_name = sub_value_name
        self.update_text()

    def update_text(self) -> None:
        if self.sse is None:
            text_value = None
        elif self.value_name not in self.sse.__dict__:
            text_value = None
        elif isinstance(self.sse.__dict__[self.value_name], dict) and self.sub_value_name is not None:
            text_value = self.sse.__dict__[self.value_name][self.sub_value_name]
        elif self.sub_value_name is not None and self.sse.__dict__[self.value_name] is not None:
            text_value = self.sse.__dict__[self.value_name].__dict__[self.sub_value_name]
        else:
            text_value = self.sse.__dict__[self.value_name]

        text = get_value_string_no_unit(text_value)

        self.setText(text)


class TextBrowser(QTextBrowser):

    def __init__(self, sse: Union[StellarBody, StellarBinary], value_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sse = sse
        self.value_name = value_name
        self.update_text()

    def update_text(self) -> None:
        if self.sse is None:
            text = 'None'
        elif self.value_name not in self.sse.__dict__:
            text = 'None'
        else:
            text = str(self.sse.__dict__[self.value_name])
        if text is None:
            text = 'None'
        self.setText(text)


class CheckBox(QCheckBox):

    def __init__(self, linked_line_edit: Union[UnitLineEdit, LineEdit], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linked_line_edit = linked_line_edit
        self.value_name = self.linked_line_edit.value_name
        self.toggled.connect(self.on_toggle_action)

        self.set_initial_check_status()

    def set_initial_check_status(self):
        self.linked_line_edit.value_name = f'suggested_{self.value_name}'
        suggested_value = self.linked_line_edit.get_value()
        self.linked_line_edit.value_name = f'{self.value_name}'
        user_value = self.linked_line_edit.get_value()
        if suggested_value == user_value:
            self.setChecked(True)

    def on_toggle_action(self):
        if self.isChecked():
            self.update_text()
            self.linked_line_edit.setEnabled(False)
            self.setFocus()
        else:
            self.linked_line_edit.setEnabled(True)
            self.update_text()

    def update_text(self) -> None:
        disable_later = False
        if not self.linked_line_edit.isEnabled():
            disable_later = True
            self.linked_line_edit.setEnabled(True)
        if self.isChecked():
            self.linked_line_edit.setFocus()
            self.linked_line_edit.set_to_nan()
            # self.linked_line_edit.value_name = f'suggested_{self.value_name}'
            # self.linked_line_edit.keep_old_text_action()
            # self.linked_line_edit.value_name = f'{self.value_name}'
            # self.linked_line_edit.change_text_action()
        else:
            self.linked_line_edit.setFocus()
            self.linked_line_edit.keep_old_text_action()  # unlike its name, it just takes the existing argument
            self.linked_line_edit.change_text_action()
        if disable_later:
            self.linked_line_edit.setEnabled(False)


class GroupBox(QGroupBox):

    def __init__(self, *args, **kwargs):
        super(GroupBox, self).__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)


class HorizontalTabBar(QTabBar):
    # from https://www.py4u.net/discuss/145307

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        for index in range(self.count()):
            self.initStyleOption(option, index)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            painter.drawText(self.tabRect(index),
                             Qt.AlignCenter | Qt.TextDontClip,
                             self.tabText(index))

    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        if size.width() < size.height():
            size.transpose()
        return size


class TabWidget(QTabWidget):
    # from https://www.py4u.net/discuss/145307

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(HorizontalTabBar())


class Tab(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalScrollBar().setEnabled(False)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)


class InsolationModelRadioButtons(QWidget):

    def __init__(self, sse: Union[Star, StellarBinary], influenced_labels: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sse = sse
        self.influenced_labels = influenced_labels
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.setFixedWidth(200)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        kopparapu_button = QRadioButton("Kopparapu")
        layout.addWidget(kopparapu_button)
        selsis_button = QRadioButton("Selsis")
        layout.addWidget(selsis_button)
        self.radio_buttons = {'Kopparapu': kopparapu_button, 'Selsis': selsis_button}

        if self.sse.insolation_model.name == 'Kopparapu':
            kopparapu_button.setChecked(True)
        else:
            selsis_button.setChecked(True)


class RingRadioButtons(QWidget):

    def __init__(self, sse: Planet, influenced_labels: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sse = sse
        self.influenced_labels = influenced_labels
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.setFixedWidth(200)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        yes_button = QRadioButton("Yes")
        layout.addWidget(yes_button)
        no_button = QRadioButton("No")
        layout.addWidget(no_button)
        self.radio_buttons = {'Yes': yes_button, 'No': no_button}

        if self.sse.has_ring:
            yes_button.setChecked(True)
        else:
            no_button.setChecked(True)


class GradientColorWidget(QWidget):

    def __init__(self, gradient_color: GradientColor, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.gradient_color = gradient_color
        layout = QHBoxLayout()

        self.remove_button = QPushButton('-')
        self.remove_button.setContentsMargins(0, 0, 0, 0)
        self.remove_button.setFixedWidth(30)
        self.remove_button.pressed.connect(self.press_remove_button_process)

        self.pos_label = QLabel(' Position: ')
        self.pos_line_edit = QLineEdit(str(self.gradient_color.pos))
        self.pos_line_edit.editingFinished.connect(self.pos_line_edit_process)
        self.pos_line_edit.setFixedWidth(50)

        self.red_label = QLabel(' Red: ')
        self.red_line_edit = QLineEdit(str(255 * self.gradient_color.red))
        self.red_line_edit.editingFinished.connect(partial(self.color_line_edit_process, 'red'))
        self.red_line_edit.setFixedWidth(50)

        self.green_label = QLabel(' Green: ')
        self.green_line_edit = QLineEdit(str(255 * self.gradient_color.green))
        self.green_line_edit.editingFinished.connect(partial(self.color_line_edit_process, 'green'))
        self.green_line_edit.setFixedWidth(50)

        self.blue_label = QLabel(' Blue: ')
        self.blue_line_edit = QLineEdit(str(255 * self.gradient_color.blue))
        self.blue_line_edit.editingFinished.connect(partial(self.color_line_edit_process, 'blue'))
        self.blue_line_edit.setFixedWidth(50)

        self.alpha_label = QLabel(' Alpha: ')
        self.alpha_line_edit = QLineEdit(str(255 * self.gradient_color.alpha))
        self.alpha_line_edit.editingFinished.connect(partial(self.color_line_edit_process, 'alpha'))
        self.alpha_line_edit.setFixedWidth(50)

        self.line_edits = {'red': self.red_line_edit,
                           'green': self.green_line_edit,
                           'blue': self.blue_line_edit,
                           'alpha': self.alpha_line_edit, }

        layout.addWidget(self.remove_button)

        layout.addWidget(self.pos_label)
        layout.addWidget(self.pos_line_edit)

        layout.addWidget(self.red_label)
        layout.addWidget(self.red_line_edit)

        layout.addWidget(self.green_label)
        layout.addWidget(self.green_line_edit)

        layout.addWidget(self.blue_label)
        layout.addWidget(self.blue_line_edit)

        layout.addWidget(self.alpha_label)
        layout.addWidget(self.alpha_line_edit)

        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def press_remove_button_process(self):
        self.parent().remove_gradient(self)

    def pos_line_edit_process(self):
        try:
            value = float(self.pos_line_edit.text())
            if 0 <= value <= 1:
                self.gradient_color.pos = value
            else:
                self.pos_line_edit.setText(str(self.gradient_color.pos))
        except ValueError:
            self.pos_line_edit.setText(str(self.gradient_color.pos))
        self.parent().update_ssc_object()

    def color_line_edit_process(self, color):
        try:
            value = float(self.line_edits[color].text())
            if 0 <= value <= 255:
                if color == 'red':
                    self.gradient_color.red = value / 255.
                elif color == 'green':
                    self.gradient_color.green = value / 255.
                elif color == 'blue':
                    self.gradient_color.blue = value / 255.
                elif color == 'alpha':
                    self.gradient_color.alpha = value / 255.
            else:
                self.line_edits[color].setText(str(255 * self.gradient_color.__dict__[color]))
        except ValueError:
            self.line_edits[color].setText(str(255 * self.gradient_color.__dict__[color]))
        self.parent().update_ssc_object()


class RingImage(QLabel):

    def __init__(self, sse: Planet, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sse = sse
        self.update_text()

    def update_text(self):
        self.setPixmap(self.get_image())

    def get_image(self):
        try:
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 500)
            context = cairo.Context(surface)

            units = self.sse.ring.outer_radius.u
            add_ring_path_part(context, 250, 250,
                               250 * (self.sse.ring.inner_radius / self.sse.ring.outer_radius).m, 250,
                               250 * (np.array(self.sse.ring.forbidden_bands.to(units).m)) /
                               self.sse.ring.outer_radius.to(units).m,
                               self.sse.ring.ring_radial_gradient_colors, 0, 90, 'all')

            image_array = get_ndarray_from_cairo_image_surface(surface)

            # noinspection PyTypeChecker
            image = QtGui.QImage(image_array, image_array.shape[1], image_array.shape[0],
                                 image_array.shape[1] * 4, QtGui.QImage.Format_RGBA8888)

            pix = QtGui.QPixmap(image)
        except Exception:
            pix = QtGui.QPixmap()

        pix = pix.scaled(275, 275, QtCore.Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return pix


class RingColorsWidget(QWidget):

    def __init__(self, sse: Planet, ring_image: RingImage, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sse = sse
        self.ring_image = ring_image
        layout = QVBoxLayout()

        if self.sse.has_ring:
            self.add_gradient_color_button = QPushButton('+')
            self.add_gradient_color_button.setContentsMargins(0, 0, 0, 0)
            self.add_gradient_color_button.setFixedWidth(30)
            self.add_gradient_color_button.pressed.connect(self.press_add_gradient_color_process)
            layout.addWidget(self.add_gradient_color_button)

            for gradient_color in self.sse.ring.ring_radial_gradient_colors:
                layout.addWidget(GradientColorWidget(gradient_color))

            layout.addStretch()

        self.setLayout(layout)

    def press_add_gradient_color_process(self):
        self.layout().addWidget(GradientColorWidget(GradientColor(0.5, 1, 1, 1, 1)))
        self.update_ssc_object()

    def remove_gradient(self, widget: GradientColorWidget):
        if len(self.findChildren(GradientColorWidget)) > 1:
            self.layout().removeWidget(widget)
            widget.deleteLater()
            self.adjustSize()
            self.update_ssc_object(widget)

    def update_ssc_object(self, removed_child: Union[GradientColorWidget, None] = None):
        if self.sse.has_ring:
            gradient_color_list = []
            for child in self.children():
                if isinstance(child, GradientColorWidget) and child != removed_child:
                    gradient_color_list.append(child.gradient_color)
            self.sse.ring.change_ring_radial_gradient_colors(gradient_color_list)
            self.ring_image.update_text()


class ComboBox(QComboBox):
    def __init__(self, sse: Planet, value_name: str, value_list: List, influenced_labels: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sse = sse
        self.value_name = value_name
        self.value_list = value_list
        self.value_type = type(self.sse.__dict__[self.value_name])
        self.influenced_labels = influenced_labels

        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.setFixedWidth(150)

        self.addItems(self.value_list)
        self.setCurrentText(self._get_value())
        self.currentTextChanged.connect(self.change_text_action)

    def _get_value(self):
        return str(self.sse.__dict__[self.value_name])

    def change_text_action(self, process_change=True) -> None:
        self.sse.__dict__[self.value_name] = self.value_type(self.currentText())
        if process_change:
            self.sse.__post_init__()
            for key in self.influenced_labels:
                self.influenced_labels[key].update_text()


class UnitComboBox(QComboBox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, *args, **kwargs):
        pass


class ImageLabel(QLabel):

    def __init__(self, sse: Union[Star, Planet, Satellite], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sse = sse
        # self.setScaledContents(True)
        self.update_text()

    def update_text(self):
        self.setPixmap(self.get_image(self.sse.image_array))

    @staticmethod
    def get_image(image_array):
        try:
            if image_array.shape[0] > image_array.shape[1]:
                padding = (image_array.shape[0] - image_array.shape[1]) // 2
                image_array = np.pad(image_array, ((0, 0), (padding, padding), (0, 0)))
            else:
                padding = (image_array.shape[1] - image_array.shape[0]) // 2
                image_array = np.pad(image_array, ((padding, padding), (0, 0), (0, 0)))

            # noinspection PyTypeChecker
            image = QtGui.QImage(image_array, image_array.shape[1], image_array.shape[0],
                                 image_array.shape[1] * 4, QtGui.QImage.Format_RGBA8888)

            pix = QtGui.QPixmap(image)
        except Exception:
            pix = QtGui.QPixmap()

        pix = pix.scaled(275, 275, QtCore.Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return pix


class ImageLineEdit(QWidget):

    def __init__(self, sse: Union[StellarBody, StellarBinary], influenced_labels: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sse = sse
        self.value_name = ''
        self.value = self.get_value()

        self._set_line_edit()
        self._set_browse_button()

        layout = QHBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.browse_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedSize(400, self.sizeHint().height())
        self.line_edit.setFixedWidth(300)
        self.browse_button.setFixedWidth(60)

        self.influenced_labels = influenced_labels

    def get_value(self):
        if self.value_name == '':
            return str(self.sse.image_filename)
        else:
            return 'None'

    def _set_line_edit(self):
        self.line_edit = QLineEdit(self.value, self)
        self.line_edit.editingFinished.connect(self.change_text_action)

    def _set_browse_button(self):
        self.browse_button = QPushButton(self)
        self.browse_button.setText('Browse')
        self.browse_button.clicked.connect(self.browse_action)

    def browse_action(self):
        old_image_dir = self.sse.image_filename
        if old_image_dir is None or old_image_dir == 'None':
            old_image_dir = pkg_resources.resource_filename('stellar_system_creator',
                                                            f'visualization/default_images/'
                                                            f'habitableworld.png')

        filename = QFileDialog.getOpenFileName(self, 'Choose Image', old_image_dir,
                                               "All Files (*);;Image Files (*.jpg, *.png)")[0]
        self.line_edit.setText(filename)
        self.line_edit.setFocus()
        self.change_text_action()
        self.line_edit.clearFocus()

    def change_text_action(self, process_change=True) -> None:
        if self.hasFocus() or self.line_edit.hasFocus() \
                or self.previousInFocusChain() or self.line_edit.previousInFocusChain():
            self.sse.image_filename = self.line_edit.text()
            if process_change:
                self.sse.__post_init__()
                # self.keep_old_text_action()  # in case it internally didn't find the file, we go back to None
                for key in self.influenced_labels:
                    self.influenced_labels[key].update_text()

    def keep_old_text_action(self) -> None:
        if self.hasFocus() or self.line_edit.hasFocus():
            self.line_edit.setText(self.get_value())

    def set_to_nan(self, process_change=True):
        self.line_edit.setText(str(None))
        self.sse.__dict__[self.value_name] = None
        self.setFocus()
        self.change_text_action(process_change)
        self.clearFocus()


def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


def get_value_string(value: Q_):
    if isinstance(value, dict):
        return '\n'.join([f'{key}:\t{value[key].m:.3g}' for key in value])
    else:
        return f'{value.m:.3g}'


def get_value_string_no_unit(value):
    if isinstance(value, dict):
        return '\n'.join([f'{key}:\t{value[key]}' for key in value])
    elif isinstance(value, bool):
        return str(value)
    elif isinstance(value, (int, float)):
        return f'{value:.3g}'
    else:
        return str(value)


def get_unit_bidict(value: Q_):
    if isinstance(value, dict):
        unit_str = str(f'{value[list(value.keys())[0]].units:~P}')
        unit_dimensions = value[list(value.keys())[0]].dimensionality
    else:
        unit_str = str(f'{value.units:~P}')
        unit_dimensions = value.dimensionality
    dict_pretty = bidict({})
    if len(unit_dimensions) == 1:
        if unit_dimensions['[length]'] == 1:
            dict_pretty = bidict({'nm': 'nm',
                                  'm': 'm',
                                  'ft': 'ft',
                                  'km': 'km',
                                  'mi': 'mi',
                                  'au': 'A.U.',
                                  'R_e': 'Re',
                                  'R_j': 'Rj',
                                  'R_s': 'Rs',
                                  'ly': 'ly'})
        elif unit_dimensions['[length]'] == 2:
            dict_pretty = bidict({'nm²': 'nm²',
                                  'm²': 'm²',
                                  'ft²': 'ft²',
                                  'km²': 'km²',
                                  'mi²': 'mi²',
                                  'au²': 'A.U.²',
                                  'R_e²': 'Re²',
                                  'R_j²': 'Rj²',
                                  'R_s²': 'Rs²',
                                  'A_e': 'Ae',
                                  'A_j': 'Aj',
                                  'A_s': 'As'})
        elif unit_dimensions['[length]'] == 3:
            dict_pretty = bidict({'nm³': 'nm³',
                                  'm³': 'm³',
                                  'ft³': 'ft³',
                                  'km³': 'km³',
                                  'mi³': 'mi³',
                                  'au³': 'A.U.³',
                                  'R_e³': 'Re³',
                                  'R_j³': 'Rj³',
                                  'R_s³': 'Rs³',
                                  'V_e': 'Ve',
                                  'V_j': 'Vj',
                                  'V_s': 'Vs'})
        elif unit_dimensions['[mass]'] == 1:
            dict_pretty = bidict({'kg': 'kg',
                                  'M_e': 'Me',
                                  'M_j': 'Mj',
                                  'M_s': 'Ms'})
        elif unit_dimensions['[time]'] == 1:
            dict_pretty = bidict({'s': 'second',
                                  'min': 'minute',
                                  'hr': 'hour',
                                  'd': 'day',
                                  'a': 'year',
                                  'Ga': 'gigayear',
                                  'T_s': 'Ts'})
        elif unit_dimensions['[temperature]'] == 1:
            dict_pretty = bidict({'K': 'K', 'degC': '°C', 'degF': '°F'})
    elif len(unit_dimensions) == 2:
        if unit_dimensions['[length]'] == 1 and unit_dimensions['[time]'] == -1:
            dict_pretty = bidict({'m/s': 'm/s',
                                  'km/s': 'km/s',
                                  'km/hr': 'km/hr',
                                  'ft/s': 'ft/s',
                                  'mi/s': 'mi/s',
                                  'mi/hr': 'mi/hr',
                                  'vorb_e': 'vorb_e',
                                  'vesc_e': 'vesc_e'})
        elif unit_dimensions['[length]'] == 1 and unit_dimensions['[time]'] == -2:
            dict_pretty = bidict({'m/s²': 'm/s²',
                                  'km/s²': 'km/s²',
                                  'km/hr²': 'km/hr²',
                                  'ft/s²': 'ft/s²',
                                  'mi/s²': 'mi/s²',
                                  'mi/hr²': 'mi/hr²',
                                  'g_e': 'g_e'})
        elif unit_dimensions['[mass]'] == 1 and unit_dimensions['[length]'] == -3:
            dict_pretty = bidict({'kg/m³': 'kg/m³',
                                  'g/cm³': 'g/cm³',
                                  'rho_e': 'ρe',
                                  'rho_j': 'ρj',
                                  'rho_s': 'ρs'})
        elif unit_dimensions['[mass]'] == 1 and unit_dimensions['[time]'] == -3:
            dict_pretty = bidict({'W/m²': 'W/m²',
                                  'S_s': 'Ss',
                                  'L_s/au²': 'Ls/au²',
                                  'L_s/mi²': 'Ls/mi²',
                                  'L_s/m²': 'Ls/m²',
                                  'L_s/ft²': 'Ls/ft²',
                                  'L_s/km²': 'Ls/km²',
                                  'L_s/nm²': 'Ls/nm²',
                                  'L_s/R_e²': 'Ls/Re²',
                                  'L_s/R_j²': 'Ls/Rj²',
                                  'L_s/R_s²': 'Ls/Rs²',
                                  'L_s/ly²': 'Ls/ly²',
                                  'W/nm²': 'W/nm²',
                                  'W/ft²': 'W/ft²',
                                  'W/km²': 'W/km²',
                                  'W/mi²': 'W/mi²',
                                  'W/au²': 'W/au²',
                                  'W/R_e²': 'W/R_e²',
                                  'W/R_j²': 'W/R_j²',
                                  'W/R_s²': 'W/R_s²',
                                  'W/ly²': 'W/ly²'})
    elif len(unit_dimensions) == 3:
        if unit_dimensions['[length]'] == 2 and unit_dimensions['[mass]'] == 1 and unit_dimensions['[time]'] == -3:
            dict_pretty = bidict({'W': 'W', 'L_s': 'Ls'})

    if dict_pretty == bidict({}):
        dict_pretty = bidict({unit_str: unit_str})

    return dict_pretty, unit_str


def get_html_script(url: str) -> str:
    """Source: https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python"""
    # url = '../../../documentation/build/html/quantities/geometric/radius.html'
    html = codecs.open(url, 'r')
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # print(soup.contents)
    # print(soup.find_all('h1'))
    t = str(soup.find_all('section')[1])
    t = t.split('\n')[2:-1]
    t = '\n'.join(t)
    # print(t)
    # t = str(soup.contents[-1])
    # print(t)
    # t = t.replace('math notranslate nohighlight','math')
    t = t.replace('span class="math notranslate nohighlight"', 'mathjax')
    # t = t.replace('span class="math notranslate nohighlight"', 'mathjax')
    return t
    # text = '\n'.join([element.get_text() for element in soup.body.find_all('p')][:-1])

    # return text

# a = get_html_script('/home/villy/Documents/projects/stellar_system_creator/stellar_system_creator/documentation/build/html/quantities/geometric/radius.html')


# print(a)
