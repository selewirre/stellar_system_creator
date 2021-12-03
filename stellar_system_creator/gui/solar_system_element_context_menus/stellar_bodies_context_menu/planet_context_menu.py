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


class SatelliteTreeViewItemContextMenu(StellarBodyTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()


class AsteroidBeltTreeViewItemContextMenu(StellarBodyTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()


class TrojanTreeViewItemContextMenu(StellarBodyTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

