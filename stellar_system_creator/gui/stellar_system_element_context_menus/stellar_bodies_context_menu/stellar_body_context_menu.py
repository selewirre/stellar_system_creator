from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox

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

    def delete_permanently_process(self, ask_question=True):
        from ..standard_items import TreeViewItemFromString
        parent: TreeViewItemFromString = self.parent_item.parent()
        if ask_question:
            question = QMessageBox.question(self, 'Delete permanently?', f"Are you sure you want to permanently delete "
                                                                         f"{self.parent_item.ssc_object.name}",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if question == QMessageBox.No:
                return

        for i in range(parent.rowCount()):
            if parent.child(i) == self.parent_item:
                ssc = self.parent_item.ssc_object
                if parent.parent() is None:
                    system = parent.model().parent().ssc_object
                else:
                    system = parent.parent().ssc_object
                system.remove_object(ssc)
                parent.removeRow(i)
