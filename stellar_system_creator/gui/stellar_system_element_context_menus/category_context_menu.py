from PyQt5.QtWidgets import QMenu, QAction, QDialog, QDialogButtonBox, QVBoxLayout, QWidget, QLineEdit, QFormLayout, \
    QComboBox, QHBoxLayout, QRadioButton, QSizePolicy
from PyQt5.Qt import QStandardItem
from stellar_system_creator.stellar_system_elements.stellar_body import MainSequenceStar, Planet, AsteroidBelt, \
    Satellite, Trojan, TrojanSatellite
from stellar_system_creator.astrothings.units import ureg
from stellar_system_creator.stellar_system_elements.planetary_system import PlanetarySystem
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem

category_add_element_class = {'Stellar Parent': MainSequenceStar,
                              'Planetary Parent': Planet,
                              'Planetary System': PlanetarySystem,
                              'Asteroid Belt': AsteroidBelt,
                              'Satellite': Satellite,
                              'Trojan': {'Trojan Asteroids': Trojan, 'Trojan Satellite': TrojanSatellite}
                              }

category_add_element_init_values = {'Stellar Parent': {'mass': 1 * ureg.M_s},
                                    'Planetary Parent': {'mass': 1 * ureg.M_e},
                                    'Planetary System': {},
                                    'Asteroid Belt': {},
                                    'Satellite': {'mass': 0.01 * ureg.M_e},
                                    'Trojan': {'Trojan Asteroids': {'lagrange_position': 1},
                                               'Trojan Satellite': {'mass': 0.01 * ureg.M_e, 'lagrange_position': 1}}
                                    }


def add_star(tree_view_item, ssc_parent, init_values):
    from stellar_system_creator.gui.gui_project_tree_view import get_stellar_body_dict
    if tree_view_item.parent() is None:
        system = tree_view_item.model().parent().scc_object
    else:
        system = tree_view_item.parent().parent().ssc_parent
    new_object = MainSequenceStar(parent=system.parent, **init_values)
    new_object_dict = get_stellar_body_dict(new_object)
    if tree_view_item.rowCount():
        tree_view_item.child(0).context_menu.delete_permanently_process()
        tree_view_item.appendRow(new_object_dict['TreeViewItem'])
    system.replace_parent(new_object)


def add_planetary_system(tree_view_item, ssc_parent, init_values):
    new_planet = Planet(init_values['name'], parent=ssc_parent,
                        **category_add_element_init_values['Planetary Parent'])
    new_object = PlanetarySystem(**init_values, parent=new_planet)

    from stellar_system_creator.gui.gui_project_tree_view import get_planetary_system_dict, \
        set_planetary_system_tree_model_from_ssc_object

    new_object_dict = get_planetary_system_dict(new_object)

    set_planetary_system_tree_model_from_ssc_object(new_object_dict['TreeViewItem'], new_object)
    tree_view_item.appendRow(new_object_dict['TreeViewItem'])


def add_planet(tree_view_item, ssc_parent, init_values):
    from stellar_system_creator.gui.gui_project_tree_view import get_stellar_body_dict
    new_object = Planet(parent=tree_view_item.parent().parent().ssc_parent, **init_values)
    new_object_dict = get_stellar_body_dict(new_object)
    if tree_view_item.rowCount():
        tree_view_item.child(0).context_menu.delete_permanently_process()
        tree_view_item.appendRow(new_object_dict['TreeViewItem'])
    ssc: PlanetarySystem = tree_view_item.parent().stellar_system_element
    ssc.replace_parent(new_object)


def add_asteroid_belt(tree_view_item, ssc_parent, init_values):
    from stellar_system_creator.gui.gui_project_tree_view import get_stellar_body_dict
    new_object = AsteroidBelt(parent=ssc_parent, **init_values)
    new_object_dict = get_stellar_body_dict(new_object)
    tree_view_item.appendRow(new_object_dict['TreeViewItem'])


def add_satellite(tree_view_item, ssc_parent, init_values):
    from stellar_system_creator.gui.gui_project_tree_view import get_stellar_body_dict
    new_object = Satellite(parent=ssc_parent, **init_values)
    new_object_dict = get_stellar_body_dict(new_object)
    tree_view_item.appendRow(new_object_dict['TreeViewItem'])


def add_trojan(tree_view_item, ssc_parent, init_values):
    from stellar_system_creator.gui.gui_project_tree_view import get_stellar_body_dict
    new_object = Trojan(parent=ssc_parent, **init_values)
    new_object_dict = get_stellar_body_dict(new_object)
    tree_view_item.appendRow(new_object_dict['TreeViewItem'])


def add_trojan_satellite(tree_view_item, ssc_parent, init_values):
    from stellar_system_creator.gui.gui_project_tree_view import get_stellar_body_dict
    new_object = TrojanSatellite(parent=ssc_parent, **init_values)
    new_object_dict = get_stellar_body_dict(new_object)
    tree_view_item.appendRow(new_object_dict['TreeViewItem'])


add_element_function = {'Stellar Parent': add_star,
                        'Planetary System': add_planetary_system,
                        'Planetary Parent': add_planet,
                        'Asteroid Belt': add_asteroid_belt,
                        'Satellite': add_satellite,
                        'Trojan': add_trojan,
                        'Trojan Satellite': add_trojan_satellite}


class CategoryBasedTreeViewItemContextMenu(QMenu):

    def __init__(self, parent_item, ssc_parent):
        self.parent_item: QStandardItem = parent_item
        super().__init__(self.parent_item.parent())
        self.category = self.parent_item.text()
        if self.category.endswith('s'):
            self.category = self.category[:-1]

        self.ssc_parent = ssc_parent
        self._create_menu_actions()
        self._connect_actions()
        self._create_menu()

    def _create_menu(self):
        self.addSection(self.parent_item.text())
        self.addAction(self.add_element_action)
        self.addSeparator()
        self.addAction(self.expand_all_action)
        self.addAction(self.collapse_all_action)

    def _connect_actions(self):
        self.add_element_action.triggered.connect(self.add_element_process)
        self.expand_all_action.triggered.connect(self.expand_all_process)
        self.collapse_all_action.triggered.connect(self.collapse_all_process)

    def _create_menu_actions(self):
        self.add_element_action = QAction(f"&Add {self.category}...", self)
        self.expand_all_action = QAction(f"&Expand all", self)
        self.collapse_all_action = QAction(f"&Collapse all", self)

    def add_element_process(self):
        print(f'clicked {self.parent_item.text()}')
        aed = AddElementDialog(self)
        aed.exec()
        if aed.init_values is not None:
            add_element_function[self.category](self.parent_item, self.ssc_parent, aed.init_values)
            # self.parent_item.appendRow()

    def expand_all_process(self):
        from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
        tree_view: ProjectTreeView = self.parent_item.model().parent()
        tree_view.expandRecursively(self.parent_item.index())

    def collapse_all_process(self):
        from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
        tree_view: ProjectTreeView = self.parent_item.model().parent()
        tree_view.collapse_recursively(self.parent_item)


class AddElementDialog(QDialog):

    def __init__(self, parent_item: CategoryBasedTreeViewItemContextMenu):
        self.parent_item: CategoryBasedTreeViewItemContextMenu = parent_item
        super().__init__(self.parent_item.parent_item.model().parent().parent())
        self.__post_init__()

    def __post_init__(self):
        self._set_main_widget()
        self._set_button_box()

        self.setWindowTitle(f"Add {self.parent_item.category}")

        self.init_values = None
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

        layout.addRow('Name', self.name_line_edit)

    def _set_button_box(self):
        self.button_box = QDialogButtonBox((QDialogButtonBox.Cancel | QDialogButtonBox.Ok), self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def accept(self) -> None:
        if self.name_line_edit.text() != '':
            self.init_values = category_add_element_init_values[self.parent_item.category]
            if isinstance(self.option_buttons, OptionRadioButtons):
                self.init_values = self.init_values[self.option_buttons.text()]

            self.init_values['name'] = self.name_line_edit.text()
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
