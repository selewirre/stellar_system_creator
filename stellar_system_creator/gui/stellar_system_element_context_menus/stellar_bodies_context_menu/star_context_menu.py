from typing import Union

from PyQt5.QtWidgets import QAction, QMessageBox

from stellar_system_creator.stellar_system_elements.binary_system import StellarBinary
from stellar_system_creator.stellar_system_elements.stellar_body import MainSequenceStar, BlackHole
from ..stellar_bodies_context_menu.stellar_body_context_menu import \
    StellarBodyTreeViewItemContextMenu
from ..stellar_bodies_context_menu.star_details_dialog import StarDetailsDialog


class StarTreeViewItemContextMenu(StellarBodyTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()
        self.addAction(self.convert_action)

    def _connect_actions(self):
        super()._connect_actions()
        self.convert_action.triggered.connect(self.convert_process)

    def _create_menu_actions(self):
        super()._create_menu_actions()
        self.convert_action = QAction(f"&Convert to {self.get_opposite_star_type()}", self)

    def details_action_process(self):
        details_dialog = StarDetailsDialog(self.parent_item)
        details_dialog.show()

    def convert_process(self):
        from ..standard_items import TreeViewItemFromString, TreeViewItemFromStellarSystemElement as tvifsse
        tree_view_item: Union[TreeViewItemFromString, tvifsse] = self.parent_item
        # print(tree_view_item.ssc_object.name)
        # print(self.parent_item.ssc_object.name)
        ssc_object = self.parent_item.ssc_object
        question = QMessageBox.question(self, 'Convert?', f"Are you sure you want to convert "
                                                          f"{ssc_object.name} from a "
                                                          f"{self.get_current_star_type()} to a "
                                                          f"{self.get_opposite_star_type()}? "
                                                          f"This process will permanently delete all changes "
                                                          f"you made on {ssc_object.name}.",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if question == QMessageBox.No:
            return

        name = ssc_object.name
        init_values = {'mass': ssc_object.mass}

        if isinstance(tree_view_item.ssc_object.parent, StellarBinary):
            from ..category_context_menu import replace_in_stellar_binary
            if isinstance(ssc_object, MainSequenceStar):
                replacing_class = BlackHole
            elif isinstance(ssc_object, BlackHole):
                replacing_class = MainSequenceStar
            else:
                replacing_class = None
            if replacing_class is not None:
                replace_in_stellar_binary(name, tree_view_item, init_values, replacing_class)
        else:
            from ..category_context_menu import replace_in_solo_star
            if isinstance(ssc_object, MainSequenceStar):
                replacing_class = BlackHole
            elif isinstance(ssc_object, BlackHole):
                replacing_class = MainSequenceStar
            else:
                replacing_class = None
            if replacing_class is not None:
                replace_in_solo_star(name, tree_view_item, init_values, replacing_class)

    def get_opposite_star_type(self):
        ssc_object = self.parent_item.ssc_object
        if isinstance(ssc_object, MainSequenceStar):
            return 'Black Hole'
        elif isinstance(ssc_object, BlackHole):
            return 'Star'
        else:
            return ''

    def get_current_star_type(self):
        ssc_object = self.parent_item.ssc_object
        if isinstance(ssc_object, MainSequenceStar):
            return 'Star'
        elif isinstance(ssc_object, BlackHole):
            return 'Black Hole'
        else:
            return ''
