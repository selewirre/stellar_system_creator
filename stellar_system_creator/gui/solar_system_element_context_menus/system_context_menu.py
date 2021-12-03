from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QMenu, QAction


class SystemTreeViewItemContextMenu(QMenu):

    def __init__(self, parent_item):
        self.parent_item: QStandardItem = parent_item
        super().__init__(self.parent_item.parent())

        self._create_menu_actions()
        self._connect_actions()
        self._create_menu()

    def _create_menu(self):
        self.addSection(self.parent_item.text())
        self.addAction(self.details_action)

    def _connect_actions(self):
        self.details_action.triggered.connect(self.details_action_process)

    def _create_menu_actions(self):
        self.details_action = QAction("&Details...", self)

    def details_action_process(self):
        pass
        # details_dialog = ElementDetailsDialog(self.parent_item)


class BinarySystemTreeViewItemContextMenu(SystemTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        pass
        # super()._create_menu()

    def _connect_actions(self):
        pass
        # super()._connect_actions()

    def _create_menu_actions(self):
        pass
        # super()._create_menu_actions()


class SolarSystemTreeViewItemContextMenu(SystemTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()


class PlanetarySystemTreeViewItemContextMenu(SystemTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

