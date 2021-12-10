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
        self.addSeparator()
        self.addAction(self.delete_permanently_action)

    def _connect_actions(self):
        self.details_action.triggered.connect(self.details_action_process)
        self.delete_permanently_action.triggered.connect(self.delete_permanently_process)

    def _create_menu_actions(self):
        self.details_action = QAction("&Details...", self)
        self.delete_permanently_action = QAction(f"&Delete Permanently...", self)

    def details_action_process(self):
        pass

    def delete_permanently_process(self):
        from .standard_items import TreeViewItemFromStellarSystemElement
        parent: TreeViewItemFromStellarSystemElement = self.parent_item.parent()
        for i in range(parent.rowCount()):
            if parent.child(i) == self.parent_item:
                ssc = self.parent_item.stellar_system_element
                if parent.parent() is None:
                    system = parent.model().parent().scc_object
                else:
                    system = parent.parent().stellar_system_element
                system.remove_object(ssc)
                parent.removeRow(i)


class BinarySystemTreeViewItemContextMenu(SystemTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()


class StellarSystemTreeViewItemContextMenu(SystemTreeViewItemContextMenu):

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


