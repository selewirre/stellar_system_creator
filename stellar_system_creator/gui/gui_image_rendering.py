import tempfile
from functools import partial
from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout

from stellar_system_creator.solar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.solar_system_elements.solar_system import SolarSystem


class SystemRenderingWidget(QSvgWidget):

    def __init__(self, ssc_object: Union[SolarSystem, PlanetarySystem, None] = None):
        super().__init__()
        self.render_image(ssc_object)

    def render_image(self, ssc_object: Union[SolarSystem, PlanetarySystem, None]):

        if ssc_object is not None:
            save_format = 'svg'
            with tempfile.NamedTemporaryFile("r+b", delete=True) as fd:
                if isinstance(ssc_object, SolarSystem):
                    ssc_object.draw_solar_system(save_fig=True, save_temp_file=fd, save_format=save_format)
                elif isinstance(ssc_object, PlanetarySystem):
                    ssc_object.draw_planetary_system(save_fig=True, save_temp_file=fd, save_format=save_format)
                fd.seek(0)
                self.renderer().load(fd.name)

            self.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
            self.show()
        else:
            self.hide()


class SystemImageWidget(QWidget):

    def __init__(self, ssc_object: Union[SolarSystem, PlanetarySystem, None] = None):
        super().__init__()
        self.ssc_object = ssc_object

        self.system_rendering_widget = SystemRenderingWidget()
        self._set_options_widget()

        layout = QVBoxLayout()

        layout.addWidget(self.options_widget)
        layout.addWidget(self.system_rendering_widget)
        layout.setAlignment(self.options_widget, Qt.AlignTop)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setStretchFactor(self.options_widget, 0)
        layout.setStretchFactor(self.system_rendering_widget, 1)
        # layout.sets
        self.setLayout(layout)

    def _set_options_widget(self):
        self.options_widget = QWidget(self)
        layout = QHBoxLayout()

        render_button = QPushButton('Render', self)
        render_button.adjustSize()
        render_button.pressed.connect(partial(self.system_rendering_widget.render_image, self.ssc_object))

        layout.addWidget(render_button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.options_widget.setLayout(layout)
        self.options_widget.setFixedSize(self.options_widget.sizeHint())


