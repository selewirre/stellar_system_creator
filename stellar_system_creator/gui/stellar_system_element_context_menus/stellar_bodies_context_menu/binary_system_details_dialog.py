from typing import Union, Dict, List

from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QTabWidget, QVBoxLayout, QWidget, QFormLayout

from stellar_system_creator.gui.stellar_system_element_context_menus.stellar_bodies_context_menu.basic_details_dialog import \
    BasicDetailsDialog
from stellar_system_creator.gui.stellar_system_element_context_menus.stellar_bodies_context_menu.basic_details_tabs import \
    InsolationTab, ParentHabitabilityTab
from stellar_system_creator.gui.stellar_system_element_context_menus.stellar_bodies_context_menu.detail_dialog_widgets import \
    LineEdit, \
    UnitLineEdit, UnitLabel, Label, TextBrowser, CheckBox, InsolationModelRadioButtons, ImageLabel, ImageLineEdit, \
    ComboBox, TabWidget, Tab, GroupBox
from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary


class StellarBinaryDetailsDialog(BasicDetailsDialog):

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
        self._set_orbital_characteristics_tab()
        self._set_children_orbit_limits_tab()
        self._set_grandchildren_orbit_limits_tab()
        self._set_insolation_tab()
        self._set_habitability_tab()

        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.physical_characteristics_tab, "Physical Characteristics")
        self.tab_widget.addTab(self.orbital_characteristics_tab, "Orbital Characteristics")
        self.tab_widget.addTab(self.children_orbit_limits_tab, "Children Orbit Limits")
        self.tab_widget.addTab(self.grandchildren_orbit_limits_tab, "Grandchildren Orbit Limits")
        self.tab_widget.addTab(self.insolation_tab, "Insolation")
        self.tab_widget.addTab(self.habitability_tab, "Habitability")

    def _set_check_boxes(self):
        sse: StellarBinary = self.parent_item.stellar_system_element

        self.check_boxes: Dict[(str, CheckBox)] = {}

    def _set_labels(self):
        sse: StellarBinary = self.parent_item.stellar_system_element
        sse.check_habitability()
        self.labels: Dict[(str, Union[Label, TextBrowser])] = {
            'Primary': Label(sse, 'primary_body', 'name'),
            'Secondary': Label(sse, 'secondary_body', 'name'),
            'Parent': Label(sse, 'parent', 'name'),
            'Farthest Parent': Label(sse, 'farthest_parent', 'name'),
            'Contact': Label(sse, 'contact'),
            'Habitability': Label(sse, 'habitability'),
            'Habitability Violations': TextBrowser(sse, 'habitability_violations')}

    def _set_unit_labels(self):
        sse: StellarBinary = self.parent_item.stellar_system_element

        self.ulabels: Dict[(str, UnitLabel)] = {
            'Total Mass': UnitLabel(sse, 'mass'),
            'Lifetime': UnitLabel(sse, 'lifetime'), 'Age': UnitLabel(sse, 'age'),
            'Binary P-type Critical Orbit (Inner)': UnitLabel(sse, 'binary_ptype_critical_orbit'),
            'Primary S-type Critical Orbit (Outer)': UnitLabel(sse, 'primary_stype_critical_orbit'),
            'Secondary S-type Critical Orbit (Outer)': UnitLabel(sse, 'secondary_stype_critical_orbit'),
            'Tidal Locking Radius': UnitLabel(sse, 'tidal_locking_radius'),
            'Hill Sphere': UnitLabel(sse, 'hill_sphere'),
            'Rough Inner Orbit Limit': UnitLabel(sse, 'rough_inner_orbit_limit'),
            'Rough Outer Orbit Limit': UnitLabel(sse, 'rough_outer_orbit_limit'),
            'Inner Orbit Limit': UnitLabel(sse, 'inner_orbit_limit'),
            'Outer Orbit Limit': UnitLabel(sse, 'outer_orbit_limit'),
            'Maximum Distance': UnitLabel(sse, 'maximum_distance'),
            'Minimum Distance': UnitLabel(sse, 'minimum_distance'),
            'Orbital Period': UnitLabel(sse, 'orbital_period'),
            'Inner Water Frost Limit': UnitLabel(sse, 'prevailing_water_frost_lines', 'Inner Limit'),
            'Sol Equivalent Water Frost Limit': UnitLabel(sse, 'prevailing_water_frost_lines', 'Sol Equivalent'),
            'Outer Water Frost Limit': UnitLabel(sse, 'prevailing_water_frost_lines', 'Outer Limit'),
            'Inner Rock Formation Limit': UnitLabel(sse, 'prevailing_rock_lines', 'Inner Limit'),
            'Outer Rock Formation Limit': UnitLabel(sse, 'prevailing_rock_lines', 'Outer Limit')}

    def _set_line_edits(self):
        sse: StellarBinary = self.parent_item.stellar_system_element

        self.le: Dict[(str, LineEdit)] = {'Name': LineEdit(sse, 'name', {}),
                                          'Eccentricity': LineEdit(sse, 'eccentricity', self.all_labels)}

    def _set_unit_line_edits(self):
        sse: StellarBinary = self.parent_item.stellar_system_element

        self.ule: Dict[(str, UnitLineEdit)] = {'Mean Distance': UnitLineEdit(sse, 'mean_distance', self.all_labels)}

    def _set_other_labels(self):
        self.other_labels = {'Insolation Model Tab': self.insolation_tab,
                             'Habitability Tab': self.habitability_tab}

    def _set_other_edits(self):
        self.other_edits = {'Insolation Model Radio Button': self.insolation_tab.insolation_model_radio_button}

    def _set_other_edit_init_values(self):
        self.other_edit_init_values = {'Insolation Model Radio Button':
                                       self.parent_item.stellar_system_element.insolation_model.name}

    def _set_general_tab(self):
        sse: StellarBinary = self.parent_item.stellar_system_element
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
        self.children_group_box = GroupBox('Children')
        children_box_layout = QFormLayout()
        self.children_group_box.setLayout(children_box_layout)
        self.add_keys_to_layout(children_box_layout, self.labels, ['Primary', 'Secondary'])

        tab_layout.addWidget(self.designations_group_box)
        tab_layout.addWidget(self.children_group_box)
        tab_layout.addStretch()

    def _set_physical_characteristics_tab(self):
        sse: StellarBinary = self.parent_item.stellar_system_element
        self.physical_characteristics_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.physical_characteristics_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting Material characteristics group box
        self.material_characteristics_group_box = GroupBox('Material Characteristics')
        material_characteristics_box_layout = QFormLayout()
        self.material_characteristics_group_box.setLayout(material_characteristics_box_layout)
        self.add_key_to_layout(material_characteristics_box_layout, self.ulabels, 'Total Mass')

        # setting age characteristics group box
        self.age_characteristics_group_box = GroupBox('Age Characteristics')
        age_characteristics_box_layout = QFormLayout()
        self.age_characteristics_group_box.setLayout(age_characteristics_box_layout)
        self.add_key_to_layout(age_characteristics_box_layout, self.ulabels, 'Age')
        self.add_key_to_layout(age_characteristics_box_layout, self.ulabels, 'Lifetime')

        tab_layout.addWidget(self.material_characteristics_group_box)
        tab_layout.addWidget(self.age_characteristics_group_box)
        tab_layout.addStretch()

    def _set_orbital_characteristics_tab(self):
        sse: StellarBinary = self.parent_item.stellar_system_element
        self.orbital_characteristics_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.orbital_characteristics_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting temperature related characteristics
        self.basic_orbital_characteristics_group_box = GroupBox('Basic Orbital Characteristics')
        basic_orbital_characteristics_box_layout = QFormLayout()
        self.basic_orbital_characteristics_group_box.setLayout(basic_orbital_characteristics_box_layout)
        self.add_key_to_layout(basic_orbital_characteristics_box_layout, self.le, 'Eccentricity')

        self.orbital_distance_characteristics_group_box = GroupBox('Orbital Distance Characteristics')
        orbital_distance_characteristics_box_layout = QFormLayout()
        self.orbital_distance_characteristics_group_box.setLayout(orbital_distance_characteristics_box_layout)
        self.add_key_to_layout(orbital_distance_characteristics_box_layout, self.ule, 'Mean Distance')
        keys = ['Minimum Distance', 'Maximum Distance']
        self.add_keys_to_layout(orbital_distance_characteristics_box_layout, self.ulabels, keys)
        self.add_key_to_layout(orbital_distance_characteristics_box_layout, self.labels, 'Contact')

        self.other_orbital_characteristics_group_box = GroupBox('Other Orbital Characteristics')
        other_orbital_characteristics_box_layout = QFormLayout()
        self.other_orbital_characteristics_group_box.setLayout(other_orbital_characteristics_box_layout)
        keys = ['Orbital Period']
        self.add_keys_to_layout(other_orbital_characteristics_box_layout, self.ulabels, keys)

        tab_layout.addWidget(self.basic_orbital_characteristics_group_box)
        tab_layout.addWidget(self.orbital_distance_characteristics_group_box)
        tab_layout.addWidget(self.other_orbital_characteristics_group_box)
        tab_layout.addStretch()

    def _set_children_orbit_limits_tab(self):
        sse: StellarBinary = self.parent_item.stellar_system_element
        self.children_orbit_limits_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.children_orbit_limits_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting Basic Limits group box
        self.basic_limits_group_box = GroupBox('Basic Limits')
        basic_limits_box_layout = QFormLayout()
        self.basic_limits_group_box.setLayout(basic_limits_box_layout)
        keys = ['Rough Inner Orbit Limit', 'Rough Outer Orbit Limit', 'Tidal Locking Radius',
                'Binary P-type Critical Orbit (Inner)',
                'Hill Sphere', 'Inner Orbit Limit', 'Outer Orbit Limit']
        self.add_keys_to_layout(basic_limits_box_layout, self.ulabels, keys)

        # setting Rock Line group box
        self.rock_line_group_box = GroupBox('Rock Formation Limits')
        rock_line_box_layout = QFormLayout()
        self.rock_line_group_box.setLayout(rock_line_box_layout)
        keys = ['Inner Rock Formation Limit', 'Outer Rock Formation Limit']
        self.add_keys_to_layout(rock_line_box_layout, self.ulabels, keys)

        # setting Water Frost Line group box
        self.water_frost_line_group_box = GroupBox('Water Frost Limits')
        water_frost_line_box_layout = QFormLayout()
        self.water_frost_line_group_box.setLayout(water_frost_line_box_layout)
        keys = ['Inner Water Frost Limit', 'Sol Equivalent Water Frost Limit', 'Outer Water Frost Limit']
        self.add_keys_to_layout(water_frost_line_box_layout, self.ulabels, keys)

        tab_layout.addWidget(self.basic_limits_group_box)
        tab_layout.addWidget(self.rock_line_group_box)
        tab_layout.addWidget(self.water_frost_line_group_box)
        tab_layout.addStretch()

    def _set_grandchildren_orbit_limits_tab(self):
        sse: StellarBinary = self.parent_item.stellar_system_element
        self.grandchildren_orbit_limits_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.grandchildren_orbit_limits_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting grandchildren S-Type Limits group box
        self.grandchildren_limits_group_box = GroupBox('S-Type Binary Grandchildren Limits')
        grandchildren_limits_box_layout = QFormLayout()
        self.grandchildren_limits_group_box.setLayout(grandchildren_limits_box_layout)
        keys = ['Primary S-type Critical Orbit (Outer)', 'Secondary S-type Critical Orbit (Outer)']
        self.add_keys_to_layout(grandchildren_limits_box_layout, self.ulabels, keys)

        tab_layout.addWidget(self.grandchildren_limits_group_box)
        tab_layout.addStretch()

    def _initialize_insolation_tab(self):
        sse: StellarBinary = self.parent_item.stellar_system_element
        self.insolation_tab = InsolationTab(sse, self.tab_widget, self.habitability_tab)

    def _set_insolation_tab(self):
        sse: StellarBinary = self.parent_item.stellar_system_element
        self.insolation_tab.set_influenced_labels(self.all_labels)

    def _initialize_habitability_tab(self):
        sse: StellarBinary = self.parent_item.stellar_system_element
        self.habitability_tab = ParentHabitabilityTab(sse, self.tab_widget)

    def _set_habitability_tab(self):
        sse: StellarBinary = self.parent_item.stellar_system_element
        label_keys = ['Habitability', 'Habitability Violations']
        self.habitability_tab.influenced_labels = {key: self.all_labels[key] for key in label_keys}
        self.habitability_tab.set_boxes()

    def return_other_edits_to_initial_values(self):
        self.other_edits['Insolation Model Radio Button'].radio_buttons[
            self.other_edit_init_values['Insolation Model Radio Button']].setChecked(True)

    def confirm_other_edit_changes(self):
        self.other_edit_init_values['Insolation Model Radio Button'] = \
            self.parent_item.stellar_system_element.insolation_model.name
