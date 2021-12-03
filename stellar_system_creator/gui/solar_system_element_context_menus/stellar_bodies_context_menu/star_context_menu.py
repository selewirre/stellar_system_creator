from ..stellar_bodies_context_menu.stellar_body_context_menu import \
    StellarBodyTreeViewItemContextMenu
from ..stellar_bodies_context_menu.star_details_dialog import StarDetailsDialog


class StarTreeViewItemContextMenu(StellarBodyTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

    def details_action_process(self):
        details_dialog = StarDetailsDialog(self.parent_item)
        details_dialog.exec()

