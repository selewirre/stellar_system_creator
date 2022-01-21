from typing import Union, Dict

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QRadioButton, QTabWidget, QSizePolicy, QLabel

from stellar_system_creator.gui.stellar_system_element_context_menus.stellar_bodies_context_menu.detail_dialog_widgets import \
    Tab, \
    InsolationModelRadioButtons, clearLayout, Label, UnitLabel, GroupBox, ImageLabel, LineEdit, DetailsLabel, \
    DetailsGroupBox, RingRadioButtons, RingColorsWidget, RingImage
from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
from stellar_system_creator.stellar_system_elements.stellar_body import Star, Planet, Satellite, TrojanSatellite


class InsolationTab(Tab):

    def __init__(self, sse: Union[Star, StellarBinary], parent=None, habitability_tab: "ParentHabitabilityTab" = None):
        super().__init__()

        self.sse = sse
        self.influenced_labels = None
        self.habitability_tab = habitability_tab

        widget = QWidget(parent)
        self.setWidget(widget)
        self.tab_layout = QVBoxLayout()
        widget.setLayout(self.tab_layout)
        self.insolation_labels = self.get_insolation_labels()
        self._set_insolation_model_radio_button()

    def _set_insolation_model_radio_button(self):
        self.insolation_model_radio_button = InsolationModelRadioButtons(self.sse, self.influenced_labels)
        self.insolation_model_radio_button.radio_buttons['Kopparapu'].toggled.connect(
            lambda: self.change_insolation_model(self.insolation_model_radio_button.radio_buttons['Kopparapu']))
        self.insolation_model_radio_button.radio_buttons['Selsis'].toggled.connect(
            lambda: self.change_insolation_model(self.insolation_model_radio_button.radio_buttons['Selsis']))

    def set_influenced_labels(self, influenced_labels: Dict):
        self.influenced_labels = influenced_labels
        if self.influenced_labels is not None:
            self.insolation_model_radio_button.influenced_labels = self.influenced_labels
            self._set_boxes()

    def _set_boxes(self):
        # setting model box
        self.model_group_box = DetailsGroupBox('Model', 'quantities/insolation_models/insolation_models.html')
        model_box_layout = QFormLayout()
        self.model_group_box.setLayout(model_box_layout)

        # setting sol equivalent box
        self.threshold_equivalent_group_box = QGroupBox('Insolation Threshold Sol Equivalent')
        threshold_equivalent_box_layout = QFormLayout()
        self.threshold_equivalent_group_box.setLayout(threshold_equivalent_box_layout)

        # setting common limits box
        self.common_habitability_limits_group_box = QGroupBox('Common Habitability Limits')
        common_habitability_limits_box_layout = QFormLayout()
        self.common_habitability_limits_group_box.setLayout(common_habitability_limits_box_layout)

        self.tab_layout.addWidget(self.model_group_box)
        self.tab_layout.addWidget(self.threshold_equivalent_group_box)
        self.tab_layout.addWidget(self.common_habitability_limits_group_box)
        self.tab_layout.addStretch()

        self._set_model_box_cells()
        self._set_sol_equivalent_box_cells()
        self._set_common_limits_box_cells()

    def _set_model_box_cells(self):
        # setting model group box
        self.model_group_box.layout().addRow("", self.insolation_model_radio_button)

    def _set_sol_equivalent_box_cells(self):
        # setting threshold earth equivalent group box
        for name in self.sse.insolation_model.names:
            self.threshold_equivalent_group_box.layout().addRow(f"{name}:", self.insolation_labels[name])

    def _set_common_limits_box_cells(self):
        # setting common habitability limits group box
        keys = ['Conservative Minimum Limit Name', 'Conservative Maximum Limit Name',
                'Relaxed Minimum Limit Name', 'Relaxed Maximum Limit Name', 'Earth Equivalent']
        tooltip_dirs = ['conservative_minimum_limit', 'conservative_maximum_limit', 'relaxed_minimum_limit',
                        'relaxed_maximum_limit', 'earth_equivalent_limit']
        for i, key in enumerate(keys):
            label = DetailsLabel(f"{key}:", f'quantities/insolation_models/{tooltip_dirs[i]}.html')
            self.common_habitability_limits_group_box.layout().addRow(label, self.insolation_labels[key])

    def update_text(self):
        for key in self.insolation_labels:
            self.insolation_labels[key].update_text()

    def change_insolation_model(self, button: QRadioButton):
        if button.isChecked():
            if self.sse.parent is not None:
                self.sse.farthest_parent.reset_insolation_model_and_habitability(button.text())
            else:
                self.sse.reset_insolation_model_and_habitability(button.text())
            layouts = [self.common_habitability_limits_group_box.layout(), self.threshold_equivalent_group_box.layout()]
            for layout in layouts:
                clearLayout(layout)
            self.insolation_labels = self.get_insolation_labels()
            self._set_common_limits_box_cells()
            self._set_sol_equivalent_box_cells()
            for key in self.influenced_labels:
                self.influenced_labels[key].update_text()
            if self.habitability_tab is not None:
                self.habitability_tab.changes_due_to_isolation_model_change()

    def get_insolation_labels(self) -> Dict:
        labels: Dict[(str, Union[Label, UnitLabel])] = {
            'Conservative Minimum Limit Name': Label(self.sse.insolation_model, 'conservative_min_name'),
            'Conservative Maximum Limit Name': Label(self.sse.insolation_model, 'conservative_max_name'),
            'Relaxed Minimum Limit Name': Label(self.sse.insolation_model, 'relaxed_min_name'),
            'Relaxed Maximum Limit Name': Label(self.sse.insolation_model, 'relaxed_max_name'),
            'Earth Equivalent': Label(self.sse.insolation_model, 'earth_equivalent')}

        for name in self.sse.insolation_model.names:
            labels[name] = UnitLabel(self.sse.insolation_model, 'orbit_thresholds_in_sol', name)

        return labels


class ParentHabitabilityTab(Tab):
    def __init__(self, sse: Union[Star, StellarBinary], parent=None):
        super().__init__()

        self.sse = sse
        self.influenced_labels: Union[Dict[(str, Union[UnitLabel, Label])], None] = None

        widget = QWidget(parent)
        self.setWidget(widget)
        self.zones_tab_widget_index = None
        self.tab_layout = QVBoxLayout()
        widget.setLayout(self.tab_layout)

    def set_boxes(self):
        self.habitability_labels = self.get_habitability_labels()
        self._set_boxes()

    def _set_boxes(self):
        # setting outlook group box
        self.outlook_group_box = GroupBox('Outlook')
        outlook_box_layout = QFormLayout()
        self.outlook_group_box.setLayout(outlook_box_layout)

        # setting zones group box
        self.zones_group_box = DetailsGroupBox('Zones', 'quantities/habitability/habitable_zones/habitable_zones.html')
        zones_box_layout = QVBoxLayout()
        self.zones_group_box.setLayout(zones_box_layout)

        self._set_outlook_box_cells()
        self._set_zones_box_cells()
        self.tab_layout.addWidget(self.outlook_group_box)
        self.tab_layout.addWidget(self.zones_group_box)
        self.tab_layout.addStretch()

    def _set_outlook_box_cells(self):
        label = DetailsLabel("Habitability:", 'quantities/habitability/habitability.html')
        self.outlook_group_box.layout().addRow(label, self.influenced_labels['Habitability'])
        self.outlook_group_box.layout().addRow("Violations:", self.influenced_labels['Habitability Violations'])

    def _set_zones_box_cells(self):
        self.zones_tab_widget = QTabWidget(self.widget().parent())
        self.zones_group_box.layout().addWidget(self.zones_tab_widget)

        hzlimits = self.sse.habitable_zone_limits
        self.habitability_subtabs = {}
        for hzltype in hzlimits:
            self.habitability_subtabs[hzltype] = QWidget(self.zones_tab_widget)
            subtab_layout = QFormLayout()
            for limit_name in hzlimits[hzltype]:
                subtab_layout.addRow(f'{limit_name}:', self.habitability_labels[f'{hzltype}/{limit_name}'])

            self.habitability_subtabs[hzltype].setLayout(subtab_layout)
            self.zones_tab_widget.addTab(self.habitability_subtabs[hzltype], hzltype)

        if self.zones_tab_widget_index is None:
            self.zones_tab_widget_index = self.zones_tab_widget.count() - 1
        self.zones_tab_widget.setCurrentIndex(self.zones_tab_widget_index)

    def changes_due_to_isolation_model_change(self):
        clearLayout(self.zones_group_box.layout())
        self.habitability_labels = self.get_habitability_labels()
        for key in self.influenced_labels:
            self.influenced_labels[key].update_text()
        # self._set_outlook_box_cells()
        self._set_zones_box_cells()

    def get_habitability_labels(self) -> Dict:
        labels: Dict[(str, UnitLabel)] = {}

        hzlimits = self.sse.habitable_zone_limits
        for hzltype in hzlimits:
            for limit_name in hzlimits[hzltype]:
                labels[f'{hzltype}/{limit_name}'] = UnitLabel(hzlimits, hzltype, limit_name)
        return labels

    def update_text(self):
        try:
            clearLayout(self.zones_group_box.layout())
            self.habitability_labels = self.get_habitability_labels()
            self._set_zones_box_cells()
        except AttributeError:
            pass
        # for key in self.habitability_labels:
        #     self.habitability_labels[key].update_text()


class ChildHabitabilityTab(Tab):
    def __init__(self, sse: Planet, parent=None):
        super().__init__()

        self.sse = sse
        self.influenced_labels: Union[Dict[(str, Union[UnitLabel, Label])], None] = None

        widget = QWidget(parent)
        self.setWidget(widget)
        self.tab_layout = QVBoxLayout()
        widget.setLayout(self.tab_layout)

    def set_boxes(self):
        # self.habitability_labels = self.get_habitability_labels()
        self._set_boxes()

    def _set_boxes(self):
        # setting outlook group box
        self.outlook_group_box = GroupBox('Outlook')
        outlook_box_layout = QFormLayout()
        self.outlook_group_box.setLayout(outlook_box_layout)

        # # setting zones group box
        # self.zones_group_box = GroupBox('Zones')
        # zones_box_layout = QVBoxLayout()
        # self.zones_group_box.setLayout(zones_box_layout)

        self._set_outlook_box_cells()
        # self._set_zones_box_cells()
        self.tab_layout.addWidget(self.outlook_group_box)
        # self.tab_layout.addWidget(self.zones_group_box)
        self.tab_layout.addStretch()

    def _set_outlook_box_cells(self):
        if isinstance(self.sse, Satellite):
            label = DetailsLabel("Habitability:", 'quantities/habitability/satellite_habitability.html')
        elif isinstance(self.sse, TrojanSatellite):
            label = DetailsLabel("Habitability:", 'quantities/habitability/trojan_satellite_habitability.html')
        elif isinstance(self.sse, Planet):
            label = DetailsLabel("Habitability:", 'quantities/habitability/planet_habitability.html')
        else:
            label = QLabel('Habitability:')
        self.outlook_group_box.layout().addRow(label, self.influenced_labels['Habitability'])
        self.outlook_group_box.layout().addRow("Violations:", self.influenced_labels['Habitability Violations'])

    # def _set_zones_box_cells(self):
    #     self.zones_tab_widget = QTabWidget(self.widget().parent())
    #     self.zones_group_box.layout().addWidget(self.zones_tab_widget)
    #
    #     hzlimits = self.sse.habitable_zone_limits
    #     self.habitability_subtabs = {}
    #     for hzltype in hzlimits:
    #         self.habitability_subtabs[hzltype] = QWidget(self.zones_tab_widget)
    #         subtab_layout = QFormLayout()
    #         for limit_name in hzlimits[hzltype]:
    #             subtab_layout.addRow(f'{limit_name}:', self.habitability_labels[f'{hzltype}/{limit_name}'])
    #
    #         self.habitability_subtabs[hzltype].setLayout(subtab_layout)
    #         self.zones_tab_widget.addTab(self.habitability_subtabs[hzltype], hzltype)
    #
    # def changes_due_to_isolation_model_change(self):
    #     clearLayout(self.zones_group_box.layout())
    #     self.habitability_labels = self.get_habitability_labels()
    #     for key in self.influenced_labels:
    #         self.influenced_labels[key].update_text()
    #     # self._set_outlook_box_cells()
    #     self._set_zones_box_cells()
    #
    # def get_habitability_labels(self) -> Dict:
    #     labels: Dict[(str, UnitLabel)] = {}
    #
    #     hzlimits = self.sse.habitable_zone_limits
    #     for hzltype in hzlimits:
    #         for limit_name in hzlimits[hzltype]:
    #             labels[f'{hzltype}/{limit_name}'] = UnitLabel(hzlimits, hzltype, limit_name)
    #     return labels

    def update_text(self):
        pass
    #     clearLayout(self.zones_group_box.layout())
    #     self.habitability_labels = self.get_habitability_labels()
    #     self._set_zones_box_cells()
    #     # for key in self.habitability_labels:
    #     #     self.habitability_labels[key].update_text()


class RingTab(Tab):
    def __init__(self, sse: Planet, parent=None):
        super().__init__()

        self.sse = sse
        self.ring_copy = self.sse.ring.copy()
        self.init_has_ring = self.sse.has_ring
        self.influenced_labels: Union[Dict[(str, Union[UnitLabel, Label])], None] = {}

        widget = QWidget(parent)
        self.setWidget(widget)
        self.tab_layout = QVBoxLayout()
        widget.setLayout(self.tab_layout)

        self.parameter_box = None
        self._set_ring_radio_button()
        self._set_influenced_labels()

    def set_boxes(self):
        self._set_boxes()

    def _set_boxes(self):
        # setting outlook group box
        self.parameter_box = GroupBox('Parameters')
        parameter_box_layout = QFormLayout()
        self.parameter_box.setLayout(parameter_box_layout)

        self.color_box = GroupBox('Colors')
        color_box_layout = QVBoxLayout()
        self.color_box.setLayout(color_box_layout)

        self.ring_image_box = GroupBox('Ring Image')
        ring_image_box_layout = QVBoxLayout()
        self.ring_image_box.setLayout(ring_image_box_layout)

        self._set_parameters_box_cells()
        self._set_color_box_cells()
        self._set_ring_image_box_cells()
        self.tab_layout.addWidget(self.parameter_box)
        self.tab_layout.addWidget(self.color_box)
        self.tab_layout.addWidget(self.ring_image_box)
        self.tab_layout.addStretch()

    def _set_influenced_labels(self):
        if self.sse.has_ring:
            self.influenced_labels = {'Inner Radius': UnitLabel(self.sse.ring, 'inner_radius'),
                                      'Outer Radius': UnitLabel(self.sse.ring, 'outer_radius')}
            self.ring_image = RingImage(self.sse)

    def reset_influenced_labels(self):
        self._set_influenced_labels()

    def _set_ring_radio_button(self):
        self.ring_radio_button = RingRadioButtons(self.sse, self.influenced_labels)
        self.ring_radio_button.radio_buttons['Yes'].toggled.connect(
            lambda: self.change_radio_button(self.ring_radio_button.radio_buttons['Yes']))
        self.ring_radio_button.radio_buttons['No'].toggled.connect(
            lambda: self.change_radio_button(self.ring_radio_button.radio_buttons['No']))

    def change_radio_button(self, button: QRadioButton):
        new_value = button.isChecked()
        if button.text() == 'No':
            new_value = not new_value

        if self.sse.has_ring != new_value:
            clearLayout(self.parameter_box.layout())
            clearLayout(self.color_box.layout())
            clearLayout(self.ring_image_box.layout())

            self.sse.has_ring = new_value
            self.sse.ring = self.sse.get_ring()
            self._set_ring_radio_button()
            if new_value:
                self.reset_influenced_labels()

            self._set_parameters_box_cells()
            self._set_color_box_cells()
            self._set_ring_image_box_cells()

    def _set_parameters_box_cells(self):
        label = DetailsLabel('Planet has ring system:', 'celestial_bodies/ring.html')
        self.parameter_box.layout().addRow(label, self.ring_radio_button)
        if self.sse.has_ring:
            self.parameter_box.layout().addRow('Inner Radius', self.influenced_labels['Inner Radius'])
            self.parameter_box.layout().addRow('Outer Radius', self.influenced_labels['Outer Radius'])

    def _set_color_box_cells(self):
        if self.sse.has_ring:
            self.color_box.layout().addWidget(RingColorsWidget(self.sse, self.ring_image))

    def _set_ring_image_box_cells(self):
        if self.sse.has_ring:
            self.ring_image_box.layout().addWidget(self.ring_image)

    def update_text(self):
        if self.sse.has_ring:
            if self.parameter_box is not None:
                clearLayout(self.parameter_box.layout())
                clearLayout(self.color_box.layout())
                clearLayout(self.ring_image_box.layout())

                self._set_ring_radio_button()
                self.reset_influenced_labels()

                self._set_parameters_box_cells()
                self._set_color_box_cells()
                self._set_ring_image_box_cells()


class ImageTab(Tab):

    def __init__(self, sse: Union[Star, Planet, Satellite], influenced_image_label: ImageLabel,
                 image_line_edit: LineEdit, image_check_box, parent):
        super().__init__()

        self.sse = sse
        self.influenced_image_label = influenced_image_label
        self.image_line_edit = image_line_edit
        self.image_check_box = image_check_box

        widget = QWidget(parent)
        self.setWidget(widget)
        self.tab_layout = QVBoxLayout()
        widget.setLayout(self.tab_layout)

    def set_boxes(self):
        self._set_boxes()

    def _set_boxes(self):
        # setting image_input group box
        self.image_input_group_box = GroupBox('Image Input')
        image_input_box_layout = QFormLayout()
        self.image_input_group_box.setLayout(image_input_box_layout)

        # setting "image" group box
        self.image_group_box = GroupBox('Image')
        self.image_group_box.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        image_box_layout = QVBoxLayout()
        self.image_group_box.setLayout(image_box_layout)

        self._set_image_input_box_cells()
        self._set_image_box_cells()
        self.tab_layout.addWidget(self.image_input_group_box)
        self.tab_layout.addWidget(self.image_group_box)
        # self.tab_layout.addStretch()

    def _set_image_input_box_cells(self):
        self.image_input_group_box.layout().addRow('Use Suggested Image', self.image_check_box)
        self.image_input_group_box.layout().addRow('Image Filename', self.image_line_edit)

    def _set_image_box_cells(self):
        self.image_group_box.layout().addWidget(self.influenced_image_label)
