from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QMenu, QAction

from .stellar_body_details_dialog import StellarBodyDetailsDialog


class StellarBodyTreeViewItemContextMenu(QMenu):

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
        details_dialog = StellarBodyDetailsDialog(self.parent_item)
        details_dialog.exec()

