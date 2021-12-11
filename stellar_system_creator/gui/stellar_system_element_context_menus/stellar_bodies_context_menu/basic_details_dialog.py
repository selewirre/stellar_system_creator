from typing import Union, Dict, List

from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from stellar_system_creator.gui.stellar_system_element_context_menus.stellar_bodies_context_menu.detail_dialog_widgets import \
    LineEdit, \
    UnitLineEdit, UnitLabel, Label, TextBrowser, CheckBox, InsolationModelRadioButtons, ImageLabel, ImageLineEdit, \
    ComboBox
from stellar_system_creator.stellar_system_elements.stellar_body import AsteroidBelt, Planet, Star, StellarBody, Satellite, Trojan


class BasicDetailsDialog(QDialog):

    def __init__(self, parent_item):
        from ..standard_items import TreeViewItemFromStellarSystemElement
        self.parent_item: TreeViewItemFromStellarSystemElement = parent_item
        self.parent_item.ssc_object.__post_init__()
        super().__init__(self.parent_item.model().parent().parent())
        self.parent_item.ssc_object.__post_init__()
        self.__post_init__()

    def __post_init__(self):
        self._set_labels()
        self._set_unit_labels()
        self._set_other_labels()
        self._set_all_labels()
        self._set_line_edits()
        self._set_unit_line_edits()
        self._set_other_edits()
        self._set_check_boxes()
        self._set_line_edit_init_values()
        self._set_other_edit_init_values()
        self._set_unit_line_edit_init_values()

        self._set_button_box()

    def _set_check_boxes(self):
        sse: Union[StellarBody, Star, Planet, AsteroidBelt,
                   Satellite, Trojan] = self.parent_item.ssc_object

        self.check_boxes: Dict[(str, CheckBox)] = {
            'Use Suggested Radius': CheckBox(self.ule['Radius']),
            'Use Suggested Luminosity': CheckBox(self.ule['Luminosity']),
            'Use Suggested Spin Period': CheckBox(self.ule['Spin Period']),
            'Use Suggested Age': CheckBox(self.ule['Age']),
            'Use Suggested Image': CheckBox(self.ule['Image Filename'])
                }

    def _set_line_edits(self):
        sse: Union[StellarBody, Star, Planet, AsteroidBelt,
                   Satellite, Trojan] = self.parent_item.ssc_object

        self.le: Dict[(str, LineEdit)] = {'Name': LineEdit(sse, 'name', {})}

    def _set_line_edit_init_values(self):
        self.init_le_values = {key: self.le[key].text() for key in self.le}

    def _set_other_edit_init_values(self):
        pass

    def _set_all_labels(self):
        self.all_labels = {**self.labels, **self.ulabels, **self.other_labels}

    def _set_other_labels(self):
        pass

    def _set_other_edits(self):
        pass

    def _set_labels(self):
        sse: Union[StellarBody, Star, Planet, AsteroidBelt,
                   Satellite, Trojan] = self.parent_item.ssc_object

        self.labels: Dict[(str, Union[Label, TextBrowser])] = {
            'Parent': Label(sse, 'parent', 'name'),
            'Farthest Parent': Label(sse, 'farthest_parent', 'name'),
            'Mass Class': Label(sse, 'mass_class'),
            'Habitability': Label(sse, 'habitability'),
            'Habitability Violations': TextBrowser(sse, 'habitability_violations'),
            'Image Array': ImageLabel(sse, 'image_array')}

    def _set_unit_line_edits(self):
        sse: Union[StellarBody, Star, Planet, AsteroidBelt,
                   Satellite, Trojan] = self.parent_item.ssc_object

        self.ule: Dict[(str, UnitLineEdit)] = {'Mass': UnitLineEdit(sse, 'mass', self.all_labels),
                                               'Radius': UnitLineEdit(sse, 'radius', self.all_labels),
                                               'Luminosity': UnitLineEdit(sse, 'luminosity', self.all_labels),
                                               'Spin Period': UnitLineEdit(sse, 'spin_period', self.all_labels),
                                               'Age': UnitLineEdit(sse, 'age', self.all_labels),
                                               'Image Filename': ImageLineEdit(
                                                   sse, {'Image Array': self.all_labels['Image Array']})}

    def _set_unit_line_edit_init_values(self):
        self.init_ule_values = {key: self.ule[key].line_edit.text() for key in self.ule}

    def _set_unit_labels(self):
        sse: Union[StellarBody, Star, Planet, AsteroidBelt,
                   Satellite, Trojan] = self.parent_item.ssc_object

        self.ulabels: Dict[(str, UnitLabel)] = {'Suggested Radius': UnitLabel(sse, 'suggested_radius'),
                                                'Circumference': UnitLabel(sse, 'circumference'),
                                                'Surface Area': UnitLabel(sse, 'surface_area'),
                                                'Volume': UnitLabel(sse, 'volume'),
                                                'Density': UnitLabel(sse, 'density'),
                                                'Suggested Luminosity': UnitLabel(sse, 'suggested_luminosity'),
                                                'Temperature': UnitLabel(sse, 'temperature'),
                                                'Suggested Spin Period': UnitLabel(sse, 'suggested_spin_period'),
                                                'Suggested Age': UnitLabel(sse, 'suggested_age'),
                                                'Lifetime': UnitLabel(sse, 'lifetime'),
                                                'Tidal Locking Radius': UnitLabel(sse, 'tidal_locking_radius'),
                                                'Hill Sphere': UnitLabel(sse, 'hill_sphere'),
                                                'Dense Roche Limit': UnitLabel(sse, 'dense_roche_limit'),
                                                'S-Type Critical Orbit': UnitLabel(sse, 'stype_critical_orbit'),
                                                'Inner Orbit Limit': UnitLabel(sse, 'inner_orbit_limit'),
                                                'Outer Orbit Limit': UnitLabel(sse, 'outer_orbit_limit'),
                                                }

    @staticmethod
    def add_key_to_layout(layout, dictionary: Dict, key):
        layout.addRow(f"{key}:", dictionary[key])

    def add_keys_to_layout(self, layout, dictionary: Dict, keys: List):
        for key in keys:
            self.add_key_to_layout(layout, dictionary, key)

    def _set_button_box(self):
        self.button_box = QDialogButtonBox((QDialogButtonBox.Cancel | QDialogButtonBox.Ok), self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Enter or a0.key() == Qt.Key_Return or a0.key() == Qt.Key_Escape:
            return
        super().keyPressEvent(a0)

    def accept(self) -> None:
        self.confirm_text_changes()
        self.parent_item.update_text()
        self.parent_item.set_stellar_system_element_icon()
        super().accept()

    def reject(self) -> None:
        self.return_texts_to_initial_values()
        super().reject()

    @staticmethod
    def change_text(qobj: Union[LineEdit, UnitLineEdit, UnitLabel, ComboBox, InsolationModelRadioButtons],
                    text: str, process_change=True) -> None:
        if isinstance(qobj, (UnitLabel, LineEdit)):
            qobj.setText(text)
        elif isinstance(qobj, InsolationModelRadioButtons):
            qobj.radio_buttons[text].toggle()
        elif isinstance(qobj, ComboBox):
            qobj.setCurrentText(text)
        else:
            qobj.line_edit.setText(text)
        qobj.setFocus()
        qobj.change_text_action(process_change)
        qobj.clearFocus()

    def confirm_text_changes(self) -> None:
        self.confirm_line_edit_changes()
        self.confirm_unit_line_edit_changes()
        self.confirm_other_edit_changes()
        self.parent_item.ssc_object.update_children()

    def confirm_line_edit_changes(self) -> None:
        for key in self.le:
            self.init_le_values[key] = self.le[key].text()

    def confirm_unit_line_edit_changes(self) -> None:
        for key in self.ule:
            self.init_ule_values[key] = self.ule[key].line_edit.text()

    def confirm_other_edit_changes(self) -> None:
        pass

    def return_texts_to_initial_values(self) -> None:
        self.return_line_edits_to_initial_values()
        self.return_unit_line_edits_to_initial_values()
        self.return_other_edits_to_initial_values()
        self.parent_item.ssc_object.__post_init__()

    def return_line_edits_to_initial_values(self) -> None:
        for key in self.le:
            if self.le[key].text() != self.init_le_values[key]:
                self.change_text(self.le[key], self.init_le_values[key], process_change=False)

    def return_unit_line_edits_to_initial_values(self) -> None:
        for key in self.ule:
            if self.ule[key].line_edit.text() != self.init_ule_values[key]:
                self.change_text(self.ule[key], self.init_ule_values[key], process_change=False)

    def return_other_edits_to_initial_values(self) -> None:
        pass
