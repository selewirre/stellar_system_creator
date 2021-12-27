from typing import Union

from PyQt5.QtWidgets import QMenu, QAction, QDialog, QDialogButtonBox, QVBoxLayout, QWidget, QLineEdit, QFormLayout, \
    QComboBox, QHBoxLayout, QRadioButton, QSizePolicy, QMessageBox
from PyQt5.Qt import QStandardItem

from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
from stellar_system_creator.stellar_system_elements.stellar_body import MainSequenceStar, Planet, AsteroidBelt, \
    Satellite, Trojan, TrojanSatellite
from stellar_system_creator.astrothings.units import ureg
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem

category_add_element_init_values = {
    'Stellar Parent': {'Star': {'mass': 1 * ureg.M_s},
                       'Stellar Binary': {'mean_distance': 0.1 * ureg.au, 'eccentricity': 0.2}},
    'Planetary Parent': {'Planet': {'mass': 1 * ureg.M_e}},
    'Asteroid Belt': {},
    'Satellite': {'mass': 0.01 * ureg.M_e},
    'Trojan': {'Trojan Asteroids': {'lagrange_position': 1},
               'Trojan Satellite': {'mass': 0.01 * ureg.M_e, 'lagrange_position': 1}}
}


# add_element_function = {'Star': add_star,
#                         'Stellar Binary': add_stellar_binary,
#                         'Planetary System': add_planetary_system,
#                         'Planetary Parent': add_planet,
#                         'Asteroid Belt': add_asteroid_belt,
#                         'Satellite': add_satellite,
#                         'Trojan': add_trojan,
#                         'Trojan Satellite': add_trojan_satellite}

def add_stellar_binary(name, tree_view_item):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
    tree_view_item: TreeViewItemFromString

    init_values_star = category_add_element_init_values['Stellar Parent']['Star']
    new_star1 = MainSequenceStar('Star1', **init_values_star)
    new_star2 = MainSequenceStar('Star2', **init_values_star)

    init_values_binary = category_add_element_init_values['Stellar Parent']['Stellar Binary']
    if tree_view_item.ssc_parent.parent is not None:
        new_object = StellarBinary(name=name, parent=tree_view_item.ssc_parent.parent.parent, **init_values_binary,
                                   primary_body=new_star1, secondary_body=new_star2)
    else:
        new_object = StellarBinary(name=name, parent=None, **init_values_binary,
                                   primary_body=new_star1, secondary_body=new_star2)

    if tree_view_item.rowCount():
        tree_view_item.child(0).context_menu.delete_permanently_process()

    tree_view_item.ssc_parent.replace_parent(new_object)
    new_tree_view_item = tvifsse(new_object)
    tree_view_item.appendRow(new_tree_view_item)

    new_star1_tree_view_item = tvifsse(new_star1)
    new_star2_tree_view_item = tvifsse(new_star2)
    new_tree_view_item.appendRow(new_star1_tree_view_item)
    new_tree_view_item.appendRow(new_star2_tree_view_item)


def add_star(name, tree_view_item):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
    tree_view_item: TreeViewItemFromString

    init_values = category_add_element_init_values['Stellar Parent']['Star']
    if tree_view_item.ssc_parent.parent is not None:
        new_object = MainSequenceStar(name=name, parent=tree_view_item.ssc_parent.parent.parent, **init_values)
    else:
        new_object = MainSequenceStar(name=name, parent=None, **init_values)

    if tree_view_item.rowCount():
        tree_view_item.child(0).context_menu.delete_permanently_process()

    tree_view_item.ssc_parent.replace_parent(new_object)
    new_tree_view_item = tvifsse(new_object)
    tree_view_item.appendRow(new_tree_view_item)


def add_stellar_system(name, tree_view_item):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
    tree_view_item: TreeViewItemFromString

    if tree_view_item.ssc_parent.children is not None:
        if len(tree_view_item.ssc_parent.children) >= 2:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("'Add Stellar System' has failed...")
            message_box.setText(f"{tree_view_item.ssc_parent.name} already has two stellar systems. "
                                f"Remove at least one before trying again.")
            message_box.exec()
            return

    init_values = category_add_element_init_values['Stellar Parent']['Star']
    new_object = MainSequenceStar(name=name, parent=tree_view_item.ssc_parent.parent, **init_values)
    new_object_system = StellarSystem(name, new_object)
    tree_view_item.ssc_parent.add_child(new_object_system)

    new_tree_view_item = tvifsse(new_object_system)
    tree_view_item.appendRow(new_tree_view_item)
    new_tree_view_item.update_text()

    stellar_parent_treeview = TreeViewItemFromString('Stellar Parent', new_object_system)
    planetary_systems_treeview = TreeViewItemFromString('Planetary Systems', new_object_system)
    asteroid_belts_treeview = TreeViewItemFromString('Asteroid Belts', new_object_system)
    new_tree_view_item.appendRow(stellar_parent_treeview)
    new_tree_view_item.appendRow(planetary_systems_treeview)
    new_tree_view_item.appendRow(asteroid_belts_treeview)

    new_planet_tree_view_item = tvifsse(new_object)
    stellar_parent_treeview.appendRow(new_planet_tree_view_item)


def add_planetary_system(name, tree_view_item):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
    tree_view_item: TreeViewItemFromString

    init_values = category_add_element_init_values['Planetary Parent']['Planet']
    new_object = Planet(name=name, parent=tree_view_item.ssc_parent.parent, **init_values)
    new_object_system = PlanetarySystem(name, new_object)
    tree_view_item.ssc_parent.add_planetary_system(new_object_system)

    new_tree_view_item = tvifsse(new_object_system)
    tree_view_item.appendRow(new_tree_view_item)
    new_tree_view_item.update_text()

    planetary_parent_treeview = TreeViewItemFromString('Planetary Parent', new_object_system)
    satellite_treeview = TreeViewItemFromString('Satellites', new_object_system)
    trojan_treeview = TreeViewItemFromString('Trojans', new_object_system)
    new_tree_view_item.appendRow(planetary_parent_treeview)
    new_tree_view_item.appendRow(satellite_treeview)
    new_tree_view_item.appendRow(trojan_treeview)

    new_planet_tree_view_item = tvifsse(new_object)
    planetary_parent_treeview.appendRow(new_planet_tree_view_item)


def add_planet(name, tree_view_item):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
    tree_view_item: TreeViewItemFromString

    init_values = category_add_element_init_values['Planetary Parent']['Planet']
    new_object = Planet(name=name, parent=tree_view_item.ssc_parent.parent.parent, **init_values)

    if tree_view_item.rowCount():
        tree_view_item.child(0).context_menu.delete_permanently_process()

    tree_view_item.ssc_parent.replace_parent(new_object)
    new_tree_view_item = tvifsse(new_object)
    tree_view_item.appendRow(new_tree_view_item)


def add_asteroid_belt(name, tree_view_item):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
    tree_view_item: TreeViewItemFromString

    init_values = category_add_element_init_values['Asteroid Belt']
    new_object = AsteroidBelt(name=name, parent=tree_view_item.ssc_parent.parent, **init_values)
    tree_view_item.ssc_parent.add_asteroid_belt(new_object)

    new_tree_view_item = tvifsse(new_object)
    tree_view_item.appendRow(new_tree_view_item)


def add_satellite(name, tree_view_item):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
    tree_view_item: TreeViewItemFromString

    init_values = category_add_element_init_values['Satellite']
    new_object = Satellite(name=name, parent=tree_view_item.ssc_parent.parent, **init_values)
    tree_view_item.ssc_parent.add_satellite(new_object)

    new_tree_view_item = tvifsse(new_object)
    tree_view_item.appendRow(new_tree_view_item)


def add_trojan(name, tree_view_item):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
    tree_view_item: TreeViewItemFromString

    init_values = category_add_element_init_values['Trojan']['Trojan Asteroids']
    new_object = Trojan(name=name, parent=tree_view_item.ssc_parent.parent, **init_values)
    tree_view_item.ssc_parent.add_trojan(new_object)

    new_tree_view_item = tvifsse(new_object)
    tree_view_item.appendRow(new_tree_view_item)


def add_trojan_satellite(name, tree_view_item):
    from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
        import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
    tree_view_item: TreeViewItemFromString

    init_values = category_add_element_init_values['Trojan']['Trojan Satellite']
    new_object = TrojanSatellite(name=name, parent=tree_view_item.ssc_parent.parent, **init_values)
    tree_view_item.ssc_parent.add_trojan(new_object)

    new_tree_view_item = tvifsse(new_object)
    tree_view_item.appendRow(new_tree_view_item)


add_element_function = {'Stellar System': add_stellar_system,
                        'Stellar Binary': add_stellar_binary,
                        'Star': add_star,
                        'Planetary System': add_planetary_system,
                        'Planetary Parent': add_planet,
                        'Asteroid Belt': add_asteroid_belt,
                        'Satellite': add_satellite,
                        'Trojan Asteroids': add_trojan,
                        'Trojan Satellite': add_trojan_satellite}


class CategoryBasedTreeViewItemContextMenu(QMenu):

    def __init__(self, parent_item):
        from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items import \
            TreeViewItemFromString
        self.parent_item: TreeViewItemFromString = parent_item
        super().__init__()
        self.category = self.parent_item.text()
        if self.category.endswith('s'):
            self.category = self.category[:-1]
            self.add_element_text = f"&Add {self.category}..."
        else:
            self.add_element_text = f"&Replace {self.category}..."

        self._create_menu_actions()
        self._connect_actions()
        self._create_menu()

    def _create_menu(self):
        self.addSection(self.parent_item.text())
        if self.category != 'S-type Binary':
            self.addAction(self.add_element_action)
        self.addSeparator()
        self.addAction(self.expand_all_action)
        self.addAction(self.collapse_all_action)
        # if self.category != 'Stellar Parent':
        if self.category != 'S-type Binary':
            self.addSeparator()
            self.addAction(self.delete_all_action)

    def _connect_actions(self):
        self.add_element_action.triggered.connect(self.add_element_process)
        self.expand_all_action.triggered.connect(self.expand_all_process)
        self.collapse_all_action.triggered.connect(self.collapse_all_process)
        self.delete_all_action.triggered.connect(self.delete_all_process)

    def _create_menu_actions(self):
        self.add_element_action = QAction(self.add_element_text, self)
        self.expand_all_action = QAction(f"&Expand all", self)
        self.collapse_all_action = QAction(f"&Collapse all", self)
        self.delete_all_action = QAction(f"&Delete all...", self)

    def add_element_process(self):
        aed = AddElementDialog(self)
        aed.exec()
        if aed.category is not None:
            add_element_function[aed.category](aed.name_line_edit.text(), self.parent_item)
            self.parent_item.model().parent().update_tab_title()

    def expand_all_process(self):
        from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
        tree_view: ProjectTreeView = self.parent_item.model().parent()
        tree_view.expandRecursively(self.parent_item.index())

    def collapse_all_process(self):
        from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
        tree_view: ProjectTreeView = self.parent_item.model().parent()
        tree_view.collapse_recursively(self.parent_item)

    def delete_all_process(self):
        question = QMessageBox.question(self, 'Delete all?', f"Are you sure you want to permanently delete "
                                                             f"all {self.parent_item.text()}?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if question == QMessageBox.No:
            return

        for i in reversed(range(self.parent_item.rowCount())):
            self.parent_item.child(i).context_menu.delete_permanently_process(False)


class AddElementDialog(QDialog):

    def __init__(self, parent_item: CategoryBasedTreeViewItemContextMenu):
        self.parent_item: CategoryBasedTreeViewItemContextMenu = parent_item
        super().__init__(self.parent_item.parent_item.model().parent().parent())
        self.__post_init__()

    def __post_init__(self):
        self.setWindowTitle(f"Add {self.parent_item.category}")
        self._set_main_widget()
        self._set_button_box()
        self.category = None

        layout = QVBoxLayout()
        layout.addWidget(self.main_widget)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.name_line_edit.setFocus()

    def _set_main_widget(self):
        self.main_widget = QWidget()
        layout = QFormLayout()
        self.main_widget.setLayout(layout)

        self.name_line_edit = QLineEdit()

        self.option_buttons = None
        if self.parent_item.category == 'Trojan':
            self.option_buttons = OptionRadioButtons(['Trojan Asteroids', 'Trojan Satellite'])
            layout.addRow('Options', self.option_buttons)
        elif self.parent_item.category == 'Stellar Parent':
            self.option_buttons = OptionRadioButtons(['Star', 'Stellar Binary'])
            layout.addRow('Options', self.option_buttons)

        layout.addRow('Name', self.name_line_edit)

    def _set_button_box(self):
        self.button_box = QDialogButtonBox((QDialogButtonBox.Cancel | QDialogButtonBox.Ok), self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def accept(self) -> None:
        if self.name_line_edit.text() != '':
            if isinstance(self.option_buttons, OptionRadioButtons):
                self.category = self.option_buttons.text()
            else:
                self.category = self.parent_item.category

            super().accept()


class OptionRadioButtons(QWidget):

    def __init__(self, option_text_list):
        super().__init__()

        self._text = ''
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        # self.setFixedWidth(400)
        self.radio_buttons = {}
        for option_text in option_text_list:
            self.radio_buttons[option_text] = QRadioButton(option_text)
            layout.addWidget(self.radio_buttons[option_text])
            self.radio_buttons[option_text].toggled.connect(
                lambda: self.toggle_button_process(self.radio_buttons[option_text]))

        self._text = self.radio_buttons[option_text_list[0]].text()
        self.radio_buttons[option_text_list[0]].setChecked(True)

    def text(self):
        return self._text

    def toggle_button_process(self, button: QRadioButton):
        if button.isChecked():
            self._text = button.text()
