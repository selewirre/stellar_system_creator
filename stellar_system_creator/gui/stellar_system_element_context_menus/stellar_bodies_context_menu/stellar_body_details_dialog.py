import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QWidget, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit, \
    QLabel, QTextBrowser, QDialogButtonBox


class StellarBodyDetailsDialog(QDialog):

    def __init__(self, parent_item):
        from ..standard_items import TreeViewItemFromStellarSystemElement
        self.parent_item: TreeViewItemFromStellarSystemElement = parent_item
        super().__init__(self.parent_item.model().parent().parent())

        # self.setWindowIcon(QIcon.fromTheme("document-properties"))
        # self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(f"{parent_item.text()} details")

        self._set_tabs()
        self._set_button_box()

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def _set_tabs(self):
        self.tab_widget = QTabWidget(self)

        self._set_characteristics_tab()
        self.image_tab = QWidget(self.tab_widget)

        self.tab_widget.addTab(self.characteristics_tab, "Characteristics")
        self.tab_widget.addTab(self.image_tab, "Image")

    def _set_characteristics_tab(self):
        sse = self.parent_item.stellar_system_element
        self.characteristics_tab = QWidget(self.tab_widget)
        characteristics_tab_outer_layout = QHBoxLayout()
        characteristics_tab_layout_column_1 = QVBoxLayout()
        characteristics_tab_layout_column_2 = QVBoxLayout()

        # set designations group box
        self.designations_group_box = QGroupBox('Designations and Classifications')
        designations_box_layout = QFormLayout()
        designations_box_layout.addRow("Name:", QLineEdit(sse.name))
        designations_box_layout.addRow("Parent:", QLabel(sse.parent.name if sse.parent is not None else 'None'))
        designations_box_layout.addRow("Farthest Parent:", QLabel(sse.farthest_parent.name
                                                                  if sse.farthest_parent is not None else 'None'))
        designations_box_layout.addRow("Mass Class:", QLabel(sse.mass_class))
        self.designations_group_box.setLayout(designations_box_layout)
        characteristics_tab_layout_column_1.addWidget(self.designations_group_box)

        # set physical characteristics group box
        self.physical_characteristics_group_box = QGroupBox('Physical Characteristics')
        physical_characteristics_layout = QFormLayout()
        physical_characteristics_layout.addRow("Mass (units):",
                                               QLineEdit(f"{sse.mass:.3g}"))
        physical_characteristics_layout.addRow("Radius (units):",
                                               QLineEdit(f"{sse.radius:.3g}"))
        physical_characteristics_layout.addRow("Suggested Radius (units):",
                                               QLabel(f"{sse.suggested_radius:.3g}"))
        physical_characteristics_layout.addRow("Luminosity (units):",
                                               QLineEdit(f"{sse.luminosity:.3g}"))
        physical_characteristics_layout.addRow("Suggested Luminosity (units):",
                                               QLabel(f"{sse.suggested_luminosity:.3g}"))
        physical_characteristics_layout.addRow("Temperature (units):",
                                               QLabel(f"{sse.temperature:.3g}"))
        physical_characteristics_layout.addRow("Circumference (units):",
                                               QLabel(f"{sse.circumference:.3g}"))
        physical_characteristics_layout.addRow("Surface Area (units):",
                                               QLabel(f"{sse.surface_area:.3g}"))
        physical_characteristics_layout.addRow("Volume (units):",
                                               QLabel(f"{sse.volume:.3g}"))
        physical_characteristics_layout.addRow("Density (units):",
                                               QLabel(f"{sse.density:.3g}"))

        self.physical_characteristics_group_box.setLayout(physical_characteristics_layout)
        characteristics_tab_layout_column_1.addWidget(self.physical_characteristics_group_box)

        self.orbital_characteristics_group_box = QGroupBox('Orbital Characteristics')
        characteristics_tab_layout_column_2.addWidget(self.orbital_characteristics_group_box)

        self.rotational_characteristics_group_box = QGroupBox('Rotational Characteristics')
        characteristics_tab_layout_column_2.addWidget(self.rotational_characteristics_group_box)

        self.orbital_characteristics_in_binary_group_box = QGroupBox('Orbital Characteristics in Binary')
        orbital_characteristics_in_binary_box_layout = QFormLayout()
        # orbital_characteristics_in_binary_box_layout.addRow("Part of Binary System:",
        #                                                     QLabel('No' if np.isnan(sse.eccentricity) else 'Yes'))
        # orbital_characteristics_in_binary_box_layout.addRow("Eccentricity:",
        #                                                     QLineEdit(f"{sse.eccentricity:.3g}"))
        # orbital_characteristics_in_binary_box_layout.addRow("Distance to Binary Barycenter:",
        #                                                     QLabel(f"{sse.distance_to_binary_barycenter:.3g}"))
        # orbital_characteristics_in_binary_box_layout.addRow("Minimum Distance to Binary Barycenter:",
        #                                                     QLabel(f"{sse.minimum_distance_to_binary_barycenter:.3g}"))
        # orbital_characteristics_in_binary_box_layout.addRow("Maximum Distance to Binary Barycenter:",
        #                                                     QLabel(f"{sse.maximum_distance_to_binary_barycenter:.3g}"))
        self.orbital_characteristics_in_binary_group_box.setLayout(orbital_characteristics_in_binary_box_layout)
        characteristics_tab_layout_column_2.addWidget(self.orbital_characteristics_in_binary_group_box)

        self.orbital_limitations_for_children_group_box = QGroupBox('Orbital Limitations for Children')
        orbital_limitations_for_children_box_layout = QFormLayout()
        self.orbital_limitations_for_children_group_box.setLayout(orbital_limitations_for_children_box_layout)
        characteristics_tab_layout_column_2.addWidget(self.orbital_limitations_for_children_group_box)

        self.habitability_group_box = QGroupBox('Habitability')
        habitability_box_layout = QFormLayout()
        habitability_box_layout.addRow("Habitable:", QLabel('Yes' if sse.habitability else 'No'))
        habitability_violation_text_browser = QTextBrowser()
        habitability_violation_text_browser.setText(sse.habitability_violations)
        habitability_box_layout.addRow("Habitability Violations:", habitability_violation_text_browser)
        self.habitability_group_box.setLayout(habitability_box_layout)
        characteristics_tab_layout_column_2.addWidget(self.habitability_group_box)

        characteristics_tab_outer_layout.addLayout(characteristics_tab_layout_column_1)
        characteristics_tab_outer_layout.addLayout(characteristics_tab_layout_column_2)
        self.characteristics_tab.setLayout(characteristics_tab_outer_layout)

    def _set_button_box(self):
        self.button_box = QDialogButtonBox((QDialogButtonBox.Cancel | QDialogButtonBox.Ok), self)
