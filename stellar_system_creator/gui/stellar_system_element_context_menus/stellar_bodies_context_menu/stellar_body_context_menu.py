from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QMenu, QAction

from .stellar_body_details_dialog import StellarBodyDetailsDialog


class StellarBodyTreeViewItemContextMenu(QMenu):

    def __init__(self, parent_item):
        from ..standard_items import TreeViewItemFromStellarSystemElement
        self.parent_item: TreeViewItemFromStellarSystemElement = parent_item
        super().__init__()

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
        from ..standard_items import TreeViewItemFromString
        parent: TreeViewItemFromString = self.parent_item.parent()
        for i in range(parent.rowCount()):
            if parent.child(i) == self.parent_item:
                ssc = self.parent_item.ssc_object
                if parent.parent() is None:
                    system = parent.model().parent().scc_object
                else:
                    system = parent.parent().ssc_object
                system.remove_object(ssc)
                parent.removeRow(i)
