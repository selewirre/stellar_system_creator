from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QFormLayout

from stellar_system_creator.stellar_system_elements import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem

from stellar_system_creator.astrothings.radius_models.planetary_radius_model import planet_compositions
from stellar_system_creator.stellar_system_elements.stellar_body import Planet, Planet, TrojanSatellite, Satellite, \
    Trojan, AsteroidBelt
from .basic_details_dialog import BasicDetailsDialog
from ..stellar_bodies_context_menu.detail_dialog_widgets import UnitLabel, \
    Label, GroupBox, TabWidget, Tab, ComboBox, LineEdit, UnitLineEdit, TextBrowser, CheckBox, DetailsLabel
from .basic_details_tabs import InsolationTab, ParentHabitabilityTab, ImageTab, ChildHabitabilityTab, RingTab


class PlanetDetailsDialog(BasicDetailsDialog):

    def __post_init__(self):
        self._set_tab_widget()
        self._initialize_habitability_tab()
        # self._initialize_insolation_tab()
        self._initialize_ring_tab()
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
        self._set_surface_characteristics_tab()
        self._set_children_orbit_limits_tab()
        # self._set_insolation_tab()
        self._set_miscellaneous_tab()
        self._set_habitability_tab()
        self._set_ring_tab()
        self._set_image_tab()

        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.physical_characteristics_tab, "Physical Characteristics")
        self.tab_widget.addTab(self.orbital_characteristics_tab, "Orbital Characteristics")
        self.tab_widget.addTab(self.surface_characteristics_tab, "Surface Characteristics")
        self.tab_widget.addTab(self.children_orbit_limits_tab, "Children Orbit Limits")
        self.tab_widget.addTab(self.miscellaneous_tab, "Miscellaneous")
        # self.tab_widget.addTab(self.insolation_tab, "Insolation")
        self.tab_widget.addTab(self.ring_tab, "Ring")
        self.tab_widget.addTab(self.habitability_tab, "Habitability")
        self.tab_widget.addTab(self.image_tab, "Image")

    def _set_check_boxes(self):
        super()._set_check_boxes()
        sse: Planet = self.parent_item.ssc_object

        self.check_boxes['Use Suggested Eccentricity'] = CheckBox(self.le['Eccentricity'])

    def _set_other_labels(self):
        self.other_labels = {'Habitability Tab': self.habitability_tab, 'Ring Tab': self.ring_tab}

    def _set_other_edits(self):
        sse: Planet = self.parent_item.ssc_object
        self.other_edits = {'Composition Type': ComboBox(sse, 'composition',
                                                         list(planet_compositions.keys()), self.all_labels),
                            'Orbit Type': ComboBox(sse, 'orbit_type', ['Prograde', 'Retrograde'], self.all_labels)
                            }

    def _set_other_edit_init_values(self):
        self.other_edit_init_values = {'Composition Type': self.other_edits['Composition Type'].currentText(),
                                       'Orbit Type': self.other_edits['Orbit Type'].currentText()}

    def _set_line_edits(self):
        sse: Planet = self.parent_item.ssc_object
        super()._set_line_edits()

        self.le['Albedo'] = LineEdit(sse, 'albedo', self.all_labels)
        self.le['Normalized Greenhouse'] = LineEdit(sse, 'normalized_greenhouse', self.all_labels)
        self.le['Heat Distribution'] = LineEdit(sse, 'heat_distribution', self.all_labels)
        self.le['Emissivity'] = LineEdit(sse, 'emissivity', self.all_labels)
        self.le['Eccentricity'] = LineEdit(sse, 'orbital_eccentricity', self.all_labels)

    def _set_labels(self):
        sse: Planet = self.parent_item.ssc_object
        super()._set_labels()

        self.labels['Suggested Eccentricity'] = Label(sse, 'suggested_orbital_eccentricity')
        self.labels['Chemical Composition'] = Label(sse, 'chemical_composition')
        self.labels['Tectonic Activity'] = Label(sse, 'tectonic_activity')
        self.labels['Orbital Stability'] = Label(sse, 'orbital_stability')
        self.labels['Orbital Type Factor'] = Label(sse, 'orbit_type_factor')
        self.labels['Orbital Stability Violations'] = TextBrowser(sse, 'stability_violations')

    def _set_unit_line_edits(self):
        sse: Planet = self.parent_item.ssc_object
        super()._set_unit_line_edits()

        self.ule['Axial Tilt'] = UnitLineEdit(sse, 'axial_tilt', self.all_labels)
        self.ule['Semi-Major Axis'] = UnitLineEdit(sse, 'semi_major_axis', self.all_labels)
        self.ule['Inclination'] = UnitLineEdit(sse, 'inclination', self.all_labels)
        self.ule['Argument of Periapsis'] = UnitLineEdit(sse, 'argument_of_periapsis', self.all_labels)
        self.ule['Longitude of the Ascending Node'] = UnitLineEdit(sse, 'longitude_of_ascending_node', self.all_labels)

    def _set_unit_labels(self):
        sse: Planet = self.parent_item.ssc_object
        super()._set_unit_labels()

        self.ulabels['Day Period'] = UnitLabel(sse, 'day_period')

        self.ulabels['Incident Flux'] = UnitLabel(sse, 'incident_flux')

        self.ulabels['Surface Gravity'] = UnitLabel(sse, 'surface_gravity')
        self.ulabels['Surface Pressure'] = UnitLabel(sse, 'surface_pressure')
        self.ulabels['Escape Velocity'] = UnitLabel(sse, 'escape_velocity')

        self.ulabels['Primordial Heating'] = UnitLabel(sse, 'internal_heating_fluxes', 'Primordial')
        self.ulabels['Radiogenic Heating'] = UnitLabel(sse, 'internal_heating_fluxes', 'Radiogenic')
        self.ulabels['Tidal Heating'] = UnitLabel(sse, 'internal_heating_fluxes', 'Tidal')
        self.ulabels['Total Heating'] = UnitLabel(sse, 'internal_heating_fluxes', 'Total')

        self.ulabels['Induced Tide Height to Parent'] = UnitLabel(sse, 'induced_tide_height_to_parent')
        self.ulabels['Induced Tide Height to Self'] = UnitLabel(sse, 'induced_tide_height_to_self')

        self.ulabels['Semi-Major Axis Minimum Limit'] = UnitLabel(sse, 'semi_major_axis_minimum_limit')
        self.ulabels['Semi-Major Axis Maximum Limit'] = UnitLabel(sse, 'semi_major_axis_maximum_limit')
        self.ulabels['Semi-Minor Axis'] = UnitLabel(sse, 'semi_minor_axis')
        self.ulabels['Apoapsis'] = UnitLabel(sse, 'apoapsis')
        self.ulabels['Periapsis'] = UnitLabel(sse, 'periapsis')
        self.ulabels['Orbital Period'] = UnitLabel(sse, 'orbital_period')
        self.ulabels['Orbital Velocity'] = UnitLabel(sse, 'orbital_velocity')
        self.ulabels['Angular Diameter from Parent'] = UnitLabel(sse, 'angular_diameter_from_parent')
        self.ulabels['Angular Diameter of Parent'] = UnitLabel(sse, 'angular_diameter_of_parent')

    def _set_general_tab(self):
        sse: Planet = self.parent_item.ssc_object
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
        self.add_keys_to_layout(classifications_box_layout, self.labels, ['Mass Class'])

        self.composition_group_box = GroupBox('Composition')
        composition_box_layout = QFormLayout()
        self.composition_group_box.setLayout(composition_box_layout)
        self.add_keys_to_layout(composition_box_layout, self.other_edits, ['Composition Type'],
                                ['quantities/material/composition_type.html'])
        self.add_keys_to_layout(composition_box_layout, self.all_labels, ['Chemical Composition'],
                                ['quantities/material/chemical_composition.html'])

        tab_layout.addWidget(self.designations_group_box)
        tab_layout.addWidget(self.classifications_group_box)
        tab_layout.addWidget(self.composition_group_box)
        tab_layout.addStretch()

    def _set_physical_characteristics_tab(self):
        sse: Planet = self.parent_item.ssc_object
        self.physical_characteristics_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.physical_characteristics_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting Material characteristics group box
        self.material_characteristics_group_box = GroupBox('Material Characteristics')
        material_characteristics_box_layout = QFormLayout()
        self.material_characteristics_group_box.setLayout(material_characteristics_box_layout)
        self.add_key_to_layout(material_characteristics_box_layout, self.ule, 'Mass',
                               'quantities/material/mass.html')
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
        # self.spectral_characteristics_group_box = GroupBox('Spectral Characteristics')
        # spectral_characteristics_box_layout = QFormLayout()
        # self.spectral_characteristics_group_box.setLayout(spectral_characteristics_box_layout)
        # self.add_key_to_layout(spectral_characteristics_box_layout, self.check_boxes, 'Use Suggested Luminosity')
        # self.add_key_to_layout(spectral_characteristics_box_layout, self.ule, 'Luminosity')
        # keys = ['Suggested Luminosity', 'Temperature']
        # self.add_keys_to_layout(spectral_characteristics_box_layout, self.ulabels, keys)

        # setting Rotational characteristics group box
        self.rotational_characteristics_group_box = GroupBox('Rotational Characteristics')
        rotational_characteristics_box_layout = QFormLayout()
        self.rotational_characteristics_group_box.setLayout(rotational_characteristics_box_layout)
        self.add_key_to_layout(rotational_characteristics_box_layout, self.check_boxes, 'Use Suggested Spin Period')
        self.add_key_to_layout(rotational_characteristics_box_layout, self.ule, 'Spin Period',
                               'quantities/rotational/spin_period.html')
        self.add_key_to_layout(rotational_characteristics_box_layout, self.ulabels, 'Suggested Spin Period',
                               'quantities/rotational/spin_period.html')
        self.add_key_to_layout(rotational_characteristics_box_layout, self.ulabels, 'Day Period',
                               'quantities/rotational/day_period.html')
        self.add_key_to_layout(rotational_characteristics_box_layout, self.ule, 'Axial Tilt',
                               'quantities/rotational/axial_tilt.html')

        # setting age characteristics group box
        self.age_characteristics_group_box = GroupBox('Age Characteristics')
        age_characteristics_box_layout = QFormLayout()
        self.age_characteristics_group_box.setLayout(age_characteristics_box_layout)
        self.add_key_to_layout(age_characteristics_box_layout, self.check_boxes, 'Use Suggested Age')
        self.add_key_to_layout(age_characteristics_box_layout, self.ule, 'Age',
                               'quantities/life/age.html')
        self.add_key_to_layout(age_characteristics_box_layout, self.ulabels, 'Suggested Age',
                               'quantities/life/age.html')
        self.add_key_to_layout(age_characteristics_box_layout, self.ulabels, 'Lifetime',
                               'quantities/life/lifetime.html')

        tab_layout.addWidget(self.material_characteristics_group_box)
        tab_layout.addWidget(self.geometric_characteristics_group_box)
        # tab_layout.addWidget(self.spectral_characteristics_group_box)
        tab_layout.addWidget(self.rotational_characteristics_group_box)
        tab_layout.addWidget(self.age_characteristics_group_box)
        # tab_layout.addWidget(self.other_basic_characteristics_group_box)
        tab_layout.addStretch()

    def _set_orbital_characteristics_tab(self):
        sse: Planet = self.parent_item.ssc_object
        self.orbital_characteristics_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.orbital_characteristics_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting temperature related characteristics
        self.basic_orbital_characteristics_group_box = GroupBox('Basic Orbital Characteristics')
        basic_orbital_characteristics_box_layout = QFormLayout()
        self.basic_orbital_characteristics_group_box.setLayout(basic_orbital_characteristics_box_layout)
        self.add_key_to_layout(basic_orbital_characteristics_box_layout, self.other_edits, 'Orbit Type',
                               'quantities/orbital/orbit_type.html')
        self.add_key_to_layout(basic_orbital_characteristics_box_layout, self.labels, 'Orbital Type Factor',
                               'quantities/orbital/orbit_type_factor.html')
        self.add_key_to_layout(basic_orbital_characteristics_box_layout, self.check_boxes, 'Use Suggested Eccentricity')
        self.add_key_to_layout(basic_orbital_characteristics_box_layout, self.le, 'Eccentricity',
                               'quantities/orbital/eccentricity.html')
        self.add_key_to_layout(basic_orbital_characteristics_box_layout, self.labels, 'Suggested Eccentricity',
                               'quantities/orbital/eccentricity.html')

        self.orbital_distance_characteristics_group_box = GroupBox('Orbital Distance Characteristics')
        orbital_distance_characteristics_box_layout = QFormLayout()
        self.orbital_distance_characteristics_group_box.setLayout(orbital_distance_characteristics_box_layout)
        self.add_key_to_layout(orbital_distance_characteristics_box_layout, self.ule, 'Semi-Major Axis',
                               'quantities/orbital/semi_major_axis.html')
        keys = ['Semi-Major Axis Minimum Limit', 'Semi-Major Axis Maximum Limit', 'Semi-Minor Axis', 'Apoapsis',
                'Periapsis']
        tooltip_dirs = [f'quantities/orbital/{fn}.html' for fn in
                        ['semi_major_axis_minimum_limit', 'semi_major_axis_maximum_limit', 'semi_minor_axis',
                         'apoapsis', 'periapsis']]
        self.add_keys_to_layout(orbital_distance_characteristics_box_layout, self.ulabels, keys, tooltip_dirs)

        self.other_orbital_characteristics_group_box = GroupBox('Other Orbital Characteristics')
        other_orbital_characteristics_box_layout = QFormLayout()
        self.other_orbital_characteristics_group_box.setLayout(other_orbital_characteristics_box_layout)
        keys = ['Orbital Period', 'Orbital Velocity']
        tooltip_dirs = [f'quantities/orbital/{fn}.html' for fn in
                        ['orbital_period', 'orbital_velocity']]
        self.add_keys_to_layout(other_orbital_characteristics_box_layout, self.ulabels, keys, tooltip_dirs)

        self.orbital_stability_characteristics_group_box = GroupBox('Orbital Stability')
        orbital_stability_characteristics_box_layout = QFormLayout()
        self.orbital_stability_characteristics_group_box.setLayout(orbital_stability_characteristics_box_layout)
        keys = ['Orbital Stability', 'Orbital Stability Violations']
        tooltip_dirs = [f'quantities/orbital/{fn}.html' for fn in
                        ['orbital_stability', None]]
        self.add_keys_to_layout(orbital_stability_characteristics_box_layout, self.labels, keys, tooltip_dirs)

        self.orientation_characteristics_group_box = GroupBox('Orientation')
        orientation_characteristics_box_layout = QFormLayout()
        self.orientation_characteristics_group_box.setLayout(orientation_characteristics_box_layout)
        keys = ['Inclination', 'Argument of Periapsis', 'Longitude of the Ascending Node']
        tooltip_dirs = [f'quantities/orbital/{fn}.html' for fn in
                        ['inclination', 'argument_of_periapsis', 'longitude_of_the_ascending_node']]
        self.add_keys_to_layout(orientation_characteristics_box_layout, self.ule, keys, tooltip_dirs)

        tab_layout.addWidget(self.basic_orbital_characteristics_group_box)
        tab_layout.addWidget(self.orbital_distance_characteristics_group_box)
        tab_layout.addWidget(self.other_orbital_characteristics_group_box)
        tab_layout.addWidget(self.orbital_stability_characteristics_group_box)
        tab_layout.addWidget(self.orientation_characteristics_group_box)
        tab_layout.addStretch()

    def _set_surface_characteristics_tab(self):
        sse: Planet = self.parent_item.ssc_object
        self.surface_characteristics_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.surface_characteristics_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting temperature related characteristics
        self.temperature_characteristics_group_box = GroupBox('Temperature Characteristics')
        temperature_characteristics_box_layout = QFormLayout()
        self.temperature_characteristics_group_box.setLayout(temperature_characteristics_box_layout)
        keys = ['Albedo', 'Normalized Greenhouse', 'Emissivity', 'Heat Distribution']
        tooltip_dirs = [f'quantities/surface/emission/{fn}.html' for fn in
                        ['albedo', 'normalized_greenhouse', 'emissivity', 'heat_distribution']]
        self.add_keys_to_layout(temperature_characteristics_box_layout, self.le, keys, tooltip_dirs)
        keys = ['Incident Flux', 'Temperature']
        tooltip_dirs = [f'quantities/surface/emission/{fn}.html' for fn in
                        ['incident_flux', 'temperature']]
        self.add_keys_to_layout(temperature_characteristics_box_layout, self.ulabels, keys, tooltip_dirs)
        self.add_key_to_layout(temperature_characteristics_box_layout, self.check_boxes, 'Use Suggested Luminosity')
        self.add_key_to_layout(temperature_characteristics_box_layout, self.ule, 'Luminosity',
                               'quantities/surface/emission/luminosity.html')
        self.add_key_to_layout(temperature_characteristics_box_layout, self.ulabels, 'Suggested Luminosity',
                               'quantities/surface/emission/luminosity.html')

        # setting gravity related characteristics
        self.gravity_characteristics_group_box = GroupBox('Gravity Characteristics')
        gravity_characteristics_box_layout = QFormLayout()
        self.gravity_characteristics_group_box.setLayout(gravity_characteristics_box_layout)
        keys = ['Surface Gravity', 'Escape Velocity']
        tooltip_dirs = [f'quantities/surface/gravity/{fn}.html' for fn in
                        ['surface_gravity', 'escape_velocity']]
        self.add_keys_to_layout(gravity_characteristics_box_layout, self.ulabels, keys, tooltip_dirs)

        # setting gravity related characteristics
        self.internal_heating_characteristics_group_box = GroupBox('Internal Heating Characteristics')
        internal_heating_characteristics_box_layout = QFormLayout()
        self.internal_heating_characteristics_group_box.setLayout(internal_heating_characteristics_box_layout)
        self.add_key_to_layout(internal_heating_characteristics_box_layout, self.labels, 'Tectonic Activity',
                               'quantities/surface/internal_heating/tectonic_activity.html')
        keys = ['Primordial Heating', 'Radiogenic Heating', 'Tidal Heating', 'Total Heating']
        tooltip_dirs = [f'quantities/surface/internal_heating/{fn}.html' for fn in
                        ['primordial_heating', 'radiogenic_heating', 'tidal_heating', 'internal_heating']]
        self.add_keys_to_layout(internal_heating_characteristics_box_layout, self.ulabels, keys, tooltip_dirs)

        # setting tidal related characteristics
        self.tidal_characteristics_group_box = GroupBox('Internal Heating Characteristics')
        tidal_characteristics_box_layout = QFormLayout()
        self.tidal_characteristics_group_box.setLayout(tidal_characteristics_box_layout)
        keys = ['Induced Tide Height to Parent', 'Induced Tide Height to Self']
        tooltip_dirs = [f'quantities/surface/{fn}.html' for fn in
                        ['induced_tide', 'induced_tide']]
        self.add_keys_to_layout(tidal_characteristics_box_layout, self.ulabels, keys, tooltip_dirs)

        tab_layout.addWidget(self.temperature_characteristics_group_box)
        tab_layout.addWidget(self.gravity_characteristics_group_box)
        tab_layout.addWidget(self.internal_heating_characteristics_group_box)
        tab_layout.addWidget(self.tidal_characteristics_group_box)
        tab_layout.addStretch()

    def _set_children_orbit_limits_tab(self):
        sse: Planet = self.parent_item.ssc_object
        self.children_orbit_limits_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.children_orbit_limits_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting Basic Limits group box
        self.basic_limits_group_box = GroupBox('Basic Limits')
        basic_limits_box_layout = QFormLayout()
        self.basic_limits_group_box.setLayout(basic_limits_box_layout)
        keys = ['Tidal Locking Radius', 'Dense Roche Limit', 'Inner Orbit Limit',
                'Hill Sphere', 'S-Type Critical Orbit', 'Outer Orbit Limit']
        tooltip_dirs = [f'quantities/children_orbit_limits/{fn}.html' for fn in
                        ['tidal_locking_radius', 'dense_roche_limit', 'inner_orbit_limit', 'hill_sphere',
                         's_type_critical_orbit', 'outer_orbit_limit']]
        self.add_keys_to_layout(basic_limits_box_layout, self.ulabels, keys, tooltip_dirs)

        tab_layout.addWidget(self.basic_limits_group_box)
        tab_layout.addStretch()

    def _set_miscellaneous_tab(self):
        sse: Planet = self.parent_item.ssc_object
        self.miscellaneous_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.miscellaneous_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting Relative size group box
        self.relative_size_group_box = GroupBox('Relative size of objects in the sky')
        relative_size_box_layout = QFormLayout()
        self.relative_size_group_box.setLayout(relative_size_box_layout)
        keys = ['Angular Diameter from Parent', 'Angular Diameter of Parent']
        tooltip_dirs = [f'quantities/surface/{fn}.html' for fn in
                        ['angular_diameter', 'angular_diameter']]
        self.add_keys_to_layout(relative_size_box_layout, self.ulabels, keys, tooltip_dirs)

        tab_layout.addWidget(self.relative_size_group_box)
        tab_layout.addStretch()

    def _initialize_ring_tab(self):
        sse: Planet = self.parent_item.ssc_object
        self.ring_tab = RingTab(sse, self.tab_widget)

    def _set_ring_tab(self):
        sse: Planet = self.parent_item.ssc_object
        self.ring_tab.set_boxes()

    # def _initialize_insolation_tab(self):
    #     sse: Planet = self.parent_item.ssc_object
    #     self.insolation_tab = InsolationTab(sse, self.tab_widget, self.habitability_tab)
    #
    # def _set_insolation_tab(self):
    #     sse: Planet = self.parent_item.ssc_object
    #     self.insolation_tab.set_influenced_labels(self.all_labels)

    def _initialize_habitability_tab(self):
        sse: Planet = self.parent_item.ssc_object
        self.habitability_tab = ChildHabitabilityTab(sse, self.tab_widget)

    def _set_habitability_tab(self):
        sse: Planet = self.parent_item.ssc_object
        label_keys = ['Habitability', 'Habitability Violations']
        self.habitability_tab.influenced_labels = {key: self.all_labels[key] for key in label_keys}
        self.habitability_tab.set_boxes()

    def _set_image_tab(self):
        sse: Planet = self.parent_item.ssc_object
        image_label = self.all_labels['Image Array']
        image_line_edit = self.ule['Image Filename']
        image_check_box = self.check_boxes['Use Suggested Image']
        self.image_tab = ImageTab(sse, image_label, image_line_edit, image_check_box, self.tab_widget)
        self.image_tab.set_boxes()

    def return_other_edits_to_initial_values(self):
        self.other_edits['Composition Type'].setCurrentText(self.other_edit_init_values['Composition Type'])
        self.other_edits['Orbit Type'].setCurrentText(self.other_edit_init_values['Orbit Type'])
        self.parent_item.ssc_object.has_ring = self.ring_tab.init_has_ring
        self.parent_item.ssc_object.ring = self.ring_tab.ring_copy

    def confirm_other_edit_changes(self):
        self.other_edit_init_values['Composition Type'] = self.parent_item.ssc_object.chemical_composition
        self.other_edit_init_values['Orbit Type'] = self.parent_item.ssc_object.orbit_type

    def accept(self) -> None:
        super().accept()

        parent = self.parent_item
        if self.parent_item.ssc_object.__class__ == Planet:
            target_system = StellarSystem
        else:
            target_system = PlanetarySystem

        from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items import \
            TreeViewItemFromStellarSystemElement

        while not parent.ssc_object.__class__ == target_system:
            parent = parent.parent()
            while not isinstance(parent, TreeViewItemFromStellarSystemElement):
                parent = parent.parent()

        parent.ssc_object.sort_all_by_distance()


class SatelliteDetailsDialog(PlanetDetailsDialog):

    def _set_tabs(self):
        super()._set_tabs()
        self.tab_widget.removeTab(6)

    def _set_unit_labels(self):
        sse: Satellite = self.parent_item.ssc_object
        super()._set_unit_labels()

        self.ulabels['Maximum Mass Limit'] = UnitLabel(sse, 'maximum_mass_limit')

    def _set_physical_characteristics_tab(self):
        sse: Planet = self.parent_item.ssc_object
        super()._set_physical_characteristics_tab()
        material_characteristics_box_layout = self.material_characteristics_group_box.layout()
        key = 'Maximum Mass Limit'
        material_characteristics_box_layout.insertRow(1, f"{key}:", self.ulabels[key])


class TrojanSatelliteDetailsDialog(SatelliteDetailsDialog):

    def _set_line_edits(self):
        sse: TrojanSatellite = self.parent_item.ssc_object
        super()._set_line_edits()

    def _set_tabs(self):
        super()._set_tabs()
        self.tab_widget.removeTab(4)

    def _set_children_orbit_limits_tab(self):
        sse: Planet = self.parent_item.ssc_object
        self.children_orbit_limits_tab = Tab()

    def _set_orbital_characteristics_tab(self):
        sse: Planet = self.parent_item.ssc_object
        super()._set_orbital_characteristics_tab()
        basic_orbital_characteristics_box_layout = self.basic_orbital_characteristics_group_box.layout()
        key = 'Lagrange Position'
        label = DetailsLabel(f"{key}:", 'quantities/orbital/lagrange_position.html')
        basic_orbital_characteristics_box_layout.insertRow(1, label, self.other_edits[key])

        self.other_edits['Orbit Type'].setEnabled(False)
        self.check_boxes['Use Suggested Eccentricity'].setEnabled(False)
        self.le['Eccentricity'].setEnabled(False)
        self.labels['Suggested Eccentricity'].setEnabled(False)
        self.ule['Semi-Major Axis'].setEnabled(False)
        self.ule['Inclination'].setEnabled(False)
        self.ule['Argument of Periapsis'].setEnabled(False)
        self.ule['Longitude of the Ascending Node'].setEnabled(False)

    def _set_other_edits(self):
        super()._set_other_edits()
        sse: Planet = self.parent_item.ssc_object
        self.other_edits['Lagrange Position'] = ComboBox(sse, 'lagrange_position', ['1', '-1'], self.all_labels)

    def _set_other_edit_init_values(self):
        super()._set_other_edit_init_values()
        self.other_edit_init_values['Lagrange Position'] = self.other_edits['Lagrange Position'].currentText()

    def return_other_edits_to_initial_values(self):
        super().return_other_edits_to_initial_values()
        self.other_edits['Lagrange Position'].setCurrentText(self.other_edit_init_values['Lagrange Position'])

    def confirm_other_edit_changes(self):
        super().confirm_other_edit_changes()
        self.other_edit_init_values['Lagrange Position'] = self.parent_item.ssc_object.lagrange_position


class TrojanDetailsDialog(PlanetDetailsDialog):

    def _set_line_edits(self):
        sse: Trojan = self.parent_item.ssc_object
        super()._set_line_edits()

        self.le['Relative Count'] = LineEdit(sse, 'relative_count', self.all_labels)

    def _set_unit_line_edits(self):
        sse: Trojan = self.parent_item.ssc_object
        super()._set_unit_line_edits()

        self.ule['Extent'] = UnitLineEdit(sse, 'extend', self.all_labels)

    def _set_tabs(self):
        super()._set_tabs()
        self.tab_widget.removeTab(8)
        self.tab_widget.removeTab(6)
        self.tab_widget.removeTab(4)
        self.tab_widget.removeTab(3)

    def _set_physical_characteristics_tab(self):
        sse: Trojan = self.parent_item.ssc_object
        self.physical_characteristics_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.physical_characteristics_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting Material characteristics group box
        self.material_characteristics_group_box = GroupBox('Material Characteristics')
        material_characteristics_box_layout = QFormLayout()
        self.material_characteristics_group_box.setLayout(material_characteristics_box_layout)
        self.add_key_to_layout(material_characteristics_box_layout, self.ule, 'Mass',
                               'quantities/material/mass.html')
        self.add_key_to_layout(material_characteristics_box_layout, self.ulabels, 'Density',
                               'quantities/material/density.html')

        # setting relative count
        self.distribution_characteristics_group_box = GroupBox('Distribution Characteristics')
        distribution_characteristics_box_layout = QFormLayout()
        self.distribution_characteristics_group_box.setLayout(distribution_characteristics_box_layout)
        self.add_key_to_layout(distribution_characteristics_box_layout, self.le, 'Relative Count',
                               'quantities/material/relative_count.html')

        # setting age characteristics group box
        self.age_characteristics_group_box = GroupBox('Age Characteristics')
        age_characteristics_box_layout = QFormLayout()
        self.age_characteristics_group_box.setLayout(age_characteristics_box_layout)
        self.add_key_to_layout(age_characteristics_box_layout, self.check_boxes, 'Use Suggested Age')
        self.add_key_to_layout(age_characteristics_box_layout, self.ule, 'Age',
                               'quantities/life/age.html')
        self.add_key_to_layout(age_characteristics_box_layout, self.ulabels, 'Suggested Age',
                               'quantities/life/age.html')
        self.add_key_to_layout(age_characteristics_box_layout, self.ulabels, 'Lifetime',
                               'quantities/life/lifetime.html')

        tab_layout.addWidget(self.material_characteristics_group_box)
        tab_layout.addWidget(self.distribution_characteristics_group_box)
        tab_layout.addWidget(self.age_characteristics_group_box)
        tab_layout.addStretch()

    def _set_children_orbit_limits_tab(self):
        sse: Planet = self.parent_item.ssc_object
        self.children_orbit_limits_tab = Tab()

    def _set_orbital_characteristics_tab(self):
        sse: Trojan = self.parent_item.ssc_object
        super()._set_orbital_characteristics_tab()
        basic_orbital_characteristics_box_layout = self.basic_orbital_characteristics_group_box.layout()
        key = 'Lagrange Position'
        label = DetailsLabel(f"{key}:", 'quantities/orbital/lagrange_position.html')
        basic_orbital_characteristics_box_layout.insertRow(1, label, self.other_edits[key])
        orbital_distance_characteristics_box_layout = self.orbital_distance_characteristics_group_box.layout()
        key = 'Extent'
        self.add_key_to_layout(orbital_distance_characteristics_box_layout, self.ule, key,
                               'quantities/orbital/extent.html')

        self.other_edits['Orbit Type'].setEnabled(False)
        self.check_boxes['Use Suggested Eccentricity'].setEnabled(False)
        self.le['Eccentricity'].setEnabled(False)
        self.labels['Suggested Eccentricity'].setEnabled(False)
        self.ule['Semi-Major Axis'].setEnabled(False)
        self.ule['Inclination'].setEnabled(False)
        self.ule['Argument of Periapsis'].setEnabled(False)
        self.ule['Longitude of the Ascending Node'].setEnabled(False)

    def _set_other_edits(self):
        super()._set_other_edits()
        sse: Planet = self.parent_item.ssc_object
        self.other_edits['Lagrange Position'] = ComboBox(sse, 'lagrange_position', ['1', '-1'], self.all_labels)

    def _set_other_edit_init_values(self):
        super()._set_other_edit_init_values()
        self.other_edit_init_values['Lagrange Position'] = self.other_edits['Lagrange Position'].currentText()

    def return_other_edits_to_initial_values(self):
        super().return_other_edits_to_initial_values()
        self.other_edits['Lagrange Position'].setCurrentText(self.other_edit_init_values['Lagrange Position'])

    def confirm_other_edit_changes(self):
        super().confirm_other_edit_changes()
        self.other_edit_init_values['Lagrange Position'] = self.parent_item.ssc_object.lagrange_position


class AsteroidBeltDetailsDialog(PlanetDetailsDialog):

    def _set_line_edits(self):
        sse: AsteroidBelt = self.parent_item.ssc_object
        super()._set_line_edits()

        self.le['Relative Count'] = LineEdit(sse, 'relative_count', self.all_labels)

    def _set_unit_line_edits(self):
        sse: AsteroidBelt = self.parent_item.ssc_object
        super()._set_unit_line_edits()

        self.ule['Extent'] = UnitLineEdit(sse, 'extend', self.all_labels)

    def _set_tabs(self):
        super()._set_tabs()
        self.tab_widget.removeTab(8)
        self.tab_widget.removeTab(6)
        self.tab_widget.removeTab(4)
        self.tab_widget.removeTab(3)

    def _set_physical_characteristics_tab(self):
        sse: AsteroidBelt = self.parent_item.ssc_object
        self.physical_characteristics_tab = Tab()
        widget = QWidget(self.tab_widget)
        self.physical_characteristics_tab.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        # setting Material characteristics group box
        self.material_characteristics_group_box = GroupBox('Material Characteristics')
        material_characteristics_box_layout = QFormLayout()
        self.material_characteristics_group_box.setLayout(material_characteristics_box_layout)
        self.add_key_to_layout(material_characteristics_box_layout, self.ule, 'Mass',
                               'quantities/material/mass.html')
        self.add_key_to_layout(material_characteristics_box_layout, self.ulabels, 'Density',
                               'quantities/material/density.html')

        # setting relative count
        self.distribution_characteristics_group_box = GroupBox('Distribution Characteristics')
        distribution_characteristics_box_layout = QFormLayout()
        self.distribution_characteristics_group_box.setLayout(distribution_characteristics_box_layout)
        self.add_key_to_layout(distribution_characteristics_box_layout, self.le, 'Relative Count',
                               'quantities/material/relative_count.html')

        # setting age characteristics group box
        self.age_characteristics_group_box = GroupBox('Age Characteristics')
        age_characteristics_box_layout = QFormLayout()
        self.age_characteristics_group_box.setLayout(age_characteristics_box_layout)
        self.add_key_to_layout(age_characteristics_box_layout, self.check_boxes, 'Use Suggested Age')
        self.add_key_to_layout(age_characteristics_box_layout, self.ule, 'Age',
                               'quantities/life/age.html')
        self.add_key_to_layout(age_characteristics_box_layout, self.ulabels, 'Suggested Age',
                               'quantities/life/age.html')
        self.add_key_to_layout(age_characteristics_box_layout, self.ulabels, 'Lifetime',
                               'quantities/life/lifetime.html')

        tab_layout.addWidget(self.material_characteristics_group_box)
        tab_layout.addWidget(self.distribution_characteristics_group_box)
        tab_layout.addWidget(self.age_characteristics_group_box)
        tab_layout.addStretch()

    def _set_children_orbit_limits_tab(self):
        sse: Planet = self.parent_item.ssc_object
        self.children_orbit_limits_tab = Tab()

    def _set_orbital_characteristics_tab(self):
        sse: Trojan = self.parent_item.ssc_object
        super()._set_orbital_characteristics_tab()
        orbital_distance_characteristics_box_layout = self.orbital_distance_characteristics_group_box.layout()
        key = 'Extent'
        self.add_key_to_layout(orbital_distance_characteristics_box_layout, self.ule, key,
                               'quantities/orbital/extent.html')

        self.other_edits['Orbit Type'].setEnabled(False)
        self.le['Eccentricity'].setEnabled(False)
        self.ule['Inclination'].setEnabled(False)
        self.ule['Argument of Periapsis'].setEnabled(False)
        self.ule['Longitude of the Ascending Node'].setEnabled(False)
