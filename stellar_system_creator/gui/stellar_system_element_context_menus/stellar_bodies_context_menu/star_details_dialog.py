from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QFormLayout

from stellar_system_creator.stellar_system_elements.stellar_body import Star
from .basic_details_dialog import BasicDetailsDialog
from ..stellar_bodies_context_menu.detail_dialog_widgets import UnitLabel, \
    Label, GroupBox, TabWidget, Tab
from .basic_details_tabs import InsolationTab, ParentHabitabilityTab, ImageTab


class StarDetailsDialog(BasicDetailsDialog):

    def __post_init__(self):
        self._set_tab_widget()
        self._initialize_habitability_tab()
        self._initialize_insolation_tab()
        super().__post_init__()
        self.setWindowTitle(f"{self.parent_item.text()} details")
        # self.setWindowIcon(QIcon.fromTheme("document-properties"))
        # self.setWindowModality(Qt.ApplicationModal)
        # self.setWindowModality(Qt.ApplicationSuspended)
        # self.setModal(False)

        self._set_tabs()

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def _set_tab_widget(self):
        self.tab_widget = TabWidget(self)
        self.tab_widget.setTabPosition(QTabWidget.West)

    def _set_tabs(self):
        self._set_general_tab()
        self._set_physical_characteristics_tab()
        self._set_children_orbit_limits_tab()
        self._set_insolation_tab()
        self._set_habitability_tab()
        self._set_image_tab()

        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.physical_characteristics_tab, "Physical Characteristics")
        self.tab_widget.addTab(self.children_orbit_limits_tab, "Children Orbit Limits")
        self.tab_widget.addTab(self.insolation_tab, "Insolation")
        self.tab_widget.addTab(self.habitability_tab, "Habitability")
        self.tab_widget.addTab(self.image_tab, "Image")

    def _set_other_labels(self):
        self.other_labels = {'Insolation Model Tab': self.insolation_tab,
                             'Habitability Tab': self.habitability_tab}

    def _set_other_edits(self):
        self.other_edits = {'Insolation Model Radio Button': self.insolation_tab.insolation_model_radio_button}

    def _set_other_edit_init_values(self):
        self.other_edit_init_values = {'Insolation Model Radio Button':
                                       self.parent_item.ssc_object.insolation_model.name}

    def _set_line_edits(self):
        sse: Star = self.parent_item.ssc_object
        super()._set_line_edits()

    def _set_labels(self):
        sse: Star = self.parent_item.ssc_object
        super()._set_labels()

        self.labels['Luminosity Class'] = Label(sse, 'luminosity_class')
        self.labels['Appearance Frequency'] = Label(sse, 'appearance_frequency')

    def _set_unit_line_edits(self):
        sse: Star = self.parent_item.ssc_object
        super()._set_unit_line_edits()

    def _set_unit_labels(self):
        sse: Star = self.parent_item.ssc_object
        super()._set_unit_labels()

        self.ulabels['Peak Wavelength'] = UnitLabel(sse, 'peak_wavelength')
        self.ulabels['Rough Inner Orbit Limit'] = UnitLabel(sse, 'rough_inner_orbit_limit')
        self.ulabels['Rough Outer Orbit Limit'] = UnitLabel(sse, 'rough_outer_orbit_limit')
        self.ulabels['Inner Water Frost Limit'] = UnitLabel(sse, 'prevailing_water_frost_lines', 'Inner Limit')
        self.ulabels['Sol Equivalent Water Frost Limit'] = UnitLabel(sse, 'prevailing_water_frost_lines',
                                                                     'Sol Equivalent')
        self.ulabels['Outer Water Frost Limit'] = UnitLabel(sse, 'prevailing_water_frost_lines', 'Outer Limit')
        self.ulabels['Inner Rock Formation Limit'] = UnitLabel(sse, 'prevailing_rock_lines', 'Inner Limit')
        self.ulabels['Outer Rock Formation Limit'] = UnitLabel(sse, 'prevailing_rock_lines', 'Outer Limit')

    def _set_general_tab(self):
        sse: Star = self.parent_item.ssc_object
        self.general_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.general_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting Designations group box
        self.designations_group_box = GroupBox('Designations')
        designations_box_layout = QFormLayout()
        self.designations_group_box.setLayout(designations_box_layout)
        self.add_key_to_layout(designations_box_layout, self.le, 'Name')
        self.add_keys_to_layout(designations_box_layout, self.labels, ['Parent', 'Farthest Parent'])

        # setting Classifications group box
        self.classifications_group_box = GroupBox('Classifications')
        classifications_box_layout = QFormLayout()
        self.classifications_group_box.setLayout(classifications_box_layout)
        self.add_keys_to_layout(classifications_box_layout, self.labels,
                                ['Mass Class', 'Luminosity Class', 'Appearance Frequency'])

        tab_layout.addWidget(self.designations_group_box)
        tab_layout.addWidget(self.classifications_group_box)
        tab_layout.addStretch()

    def _set_physical_characteristics_tab(self):
        sse: Star = self.parent_item.ssc_object
        self.physical_characteristics_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.physical_characteristics_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting Material characteristics group box
        self.material_characteristics_group_box = GroupBox('Material Characteristics')
        material_characteristics_box_layout = QFormLayout()
        self.material_characteristics_group_box.setLayout(material_characteristics_box_layout)
        self.add_key_to_layout(material_characteristics_box_layout, self.ule, 'Mass', 'quantities/material/mass.html')
        self.add_key_to_layout(material_characteristics_box_layout, self.ulabels, 'Density',
                               'quantities/material/density.html')

        # setting Geometric characteristics group box
        self.geometric_characteristics_group_box = GroupBox('Geometric Characteristics')
        geometric_characteristics_box_layout = QFormLayout()
        self.geometric_characteristics_group_box.setLayout(geometric_characteristics_box_layout)
        self.add_key_to_layout(geometric_characteristics_box_layout, self.check_boxes, 'Use Suggested Radius')
        self.add_key_to_layout(geometric_characteristics_box_layout, self.ule, 'Radius',
                               'quantities/geometric/radius.html')
        keys = ['Suggested Radius', 'Circumference', 'Surface Area', 'Volume']
        tooltip_dirs = [f'quantities/geometric/{s}.html' for s in ['radius', 'circumference', 'surface_area', 'volume']]
        self.add_keys_to_layout(geometric_characteristics_box_layout, self.ulabels, keys, tooltip_dirs)

        # setting Spectral characteristics group box
        self.spectral_characteristics_group_box = GroupBox('Spectral Characteristics')
        spectral_characteristics_box_layout = QFormLayout()
        self.spectral_characteristics_group_box.setLayout(spectral_characteristics_box_layout)
        self.add_key_to_layout(spectral_characteristics_box_layout, self.check_boxes, 'Use Suggested Luminosity')
        self.add_key_to_layout(spectral_characteristics_box_layout, self.ule, 'Luminosity',
                               'quantities/surface/emission/luminosity.html')
        keys = ['Suggested Luminosity', 'Temperature', 'Peak Wavelength']
        tooltip_dirs = [f'quantities/surface/emission/{s}.html'
                        for s in ['luminosity', 'temperature', 'peak_wavelength']]
        self.add_keys_to_layout(spectral_characteristics_box_layout, self.ulabels, keys, tooltip_dirs)

        # setting Rotational characteristics group box
        self.rotational_characteristics_group_box = GroupBox('Rotational Characteristics')
        rotational_characteristics_box_layout = QFormLayout()
        self.rotational_characteristics_group_box.setLayout(rotational_characteristics_box_layout)
        self.add_key_to_layout(rotational_characteristics_box_layout, self.check_boxes, 'Use Suggested Spin Period')
        self.add_key_to_layout(rotational_characteristics_box_layout, self.ule, 'Spin Period',
                               'quantities/rotational/spin_period.html')
        self.add_key_to_layout(rotational_characteristics_box_layout, self.ulabels, 'Suggested Spin Period',
                               'quantities/rotational/spin_period.html')

        # setting age characteristics group box
        self.age_characteristics_group_box = GroupBox('Age Characteristics')
        age_characteristics_box_layout = QFormLayout()
        self.age_characteristics_group_box.setLayout(age_characteristics_box_layout)
        self.add_key_to_layout(age_characteristics_box_layout, self.check_boxes, 'Use Suggested Age')
        self.add_key_to_layout(age_characteristics_box_layout, self.ule, 'Age', 'quantities/life/age.html')
        self.add_key_to_layout(age_characteristics_box_layout, self.ulabels, 'Suggested Age',
                               'quantities/life/age.html')
        self.add_key_to_layout(age_characteristics_box_layout, self.ulabels, 'Lifetime',
                               'quantities/life/lifetime.html')

        tab_layout.addWidget(self.material_characteristics_group_box)
        tab_layout.addWidget(self.geometric_characteristics_group_box)
        tab_layout.addWidget(self.spectral_characteristics_group_box)
        tab_layout.addWidget(self.rotational_characteristics_group_box)
        tab_layout.addWidget(self.age_characteristics_group_box)
        tab_layout.addStretch()

    def _set_children_orbit_limits_tab(self):
        sse: Star = self.parent_item.ssc_object
        self.children_orbit_limits_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.children_orbit_limits_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting Basic Limits group box
        self.basic_limits_group_box = GroupBox('Basic Limits')
        basic_limits_box_layout = QFormLayout()
        self.basic_limits_group_box.setLayout(basic_limits_box_layout)
        keys = ['Tidal Locking Radius', 'Rough Inner Orbit Limit', 'Dense Roche Limit', 'Inner Orbit Limit',
                'Rough Outer Orbit Limit', 'Hill Sphere', 'S-Type Critical Orbit', 'Outer Orbit Limit']
        tooltip_dirs = [f'quantities/children_orbit_limits/{s}.html'
                        for s in ['tidal_locking_radius', 'rough_inner_orbit_limit', 'dense_roche_limit',
                                  'inner_orbit_limit', 'rough_outer_orbit_limit', 'hill_sphere',
                                  's_type_critical_orbit', 'outer_orbit_limit']]
        self.add_keys_to_layout(basic_limits_box_layout, self.ulabels, keys, tooltip_dirs)

        # setting Rock Line group box
        self.rock_line_group_box = GroupBox('Rock Formation Limits')
        rock_line_box_layout = QFormLayout()
        self.rock_line_group_box.setLayout(rock_line_box_layout)
        keys = ['Inner Rock Formation Limit', 'Outer Rock Formation Limit']
        tooltip_dirs = [f'quantities/children_orbit_limits/{s}.html'
                        for s in ['inner_rock_formation_limit', 'outer_rock_formation_limit']]
        self.add_keys_to_layout(rock_line_box_layout, self.ulabels, keys, tooltip_dirs)

        # setting Water Frost Line group box
        self.water_frost_line_group_box = GroupBox('Water Frost Limits')
        water_frost_line_box_layout = QFormLayout()
        self.water_frost_line_group_box.setLayout(water_frost_line_box_layout)
        keys = ['Inner Water Frost Limit', 'Sol Equivalent Water Frost Limit', 'Outer Water Frost Limit']
        tooltip_dirs = [f'quantities/children_orbit_limits/{s}.html'
                        for s in ['inner_water_frost_limit', 'sol_equivalent_water_frost_limit',
                                  'outer_water_frost_limit']]
        self.add_keys_to_layout(water_frost_line_box_layout, self.ulabels, keys, tooltip_dirs)

        tab_layout.addWidget(self.basic_limits_group_box)
        tab_layout.addWidget(self.rock_line_group_box)
        tab_layout.addWidget(self.water_frost_line_group_box)
        tab_layout.addStretch()

    def _initialize_insolation_tab(self):
        sse: Star = self.parent_item.ssc_object
        self.insolation_tab = InsolationTab(sse, self.tab_widget, self.habitability_tab)

    def _set_insolation_tab(self):
        sse: Star = self.parent_item.ssc_object
        self.insolation_tab.set_influenced_labels(self.all_labels)

    def _initialize_habitability_tab(self):
        sse: Star = self.parent_item.ssc_object
        self.habitability_tab = ParentHabitabilityTab(sse, self.tab_widget)

    def _set_habitability_tab(self):
        sse: Star = self.parent_item.ssc_object
        label_keys = ['Habitability', 'Habitability Violations']
        self.habitability_tab.influenced_labels = {key: self.all_labels[key] for key in label_keys}
        self.habitability_tab.set_boxes()

    def _set_image_tab(self):
        sse: Star = self.parent_item.ssc_object
        image_label = self.all_labels['Image Array']
        image_line_edit = self.ule['Image Filename']
        image_check_box = self.check_boxes['Use Suggested Image']
        self.image_tab = ImageTab(sse, image_label, image_line_edit, image_check_box, self.tab_widget)
        self.image_tab.set_boxes()

    def return_other_edits_to_initial_values(self):
        self.other_edits['Insolation Model Radio Button'].radio_buttons[
            self.other_edit_init_values['Insolation Model Radio Button']].setChecked(True)

    def confirm_other_edit_changes(self):
        self.other_edit_init_values['Insolation Model Radio Button'] = \
            self.parent_item.ssc_object.insolation_model.name

