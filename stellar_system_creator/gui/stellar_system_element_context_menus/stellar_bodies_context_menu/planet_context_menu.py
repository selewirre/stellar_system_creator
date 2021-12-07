from .planet_details_dialog import PlanetDetailsDialog, SatelliteDetailsDialog, TrojanSatelliteDetailsDialog, \
    TrojanDetailsDialog, AsteroidBeltDetailsDialog
from ..stellar_bodies_context_menu.stellar_body_context_menu import \
    StellarBodyTreeViewItemContextMenu


class PlanetTreeViewItemContextMenu(StellarBodyTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

    def details_action_process(self):
        details_dialog = PlanetDetailsDialog(self.parent_item)
        details_dialog.exec()


class SatelliteTreeViewItemContextMenu(StellarBodyTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

    def details_action_process(self):
        details_dialog = SatelliteDetailsDialog(self.parent_item)
        details_dialog.exec()


class AsteroidBeltTreeViewItemContextMenu(StellarBodyTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

    def details_action_process(self):
        details_dialog = AsteroidBeltDetailsDialog(self.parent_item)
        details_dialog.exec()


class TrojanTreeViewItemContextMenu(StellarBodyTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

    def details_action_process(self):
        details_dialog = TrojanDetailsDialog(self.parent_item)
        details_dialog.exec()


class TrojanSatelliteTreeViewItemContextMenu(StellarBodyTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

    def details_action_process(self):
        details_dialog = TrojanSatelliteDetailsDialog(self.parent_item)
        details_dialog.exec()
