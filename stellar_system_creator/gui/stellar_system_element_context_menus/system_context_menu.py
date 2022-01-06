from functools import partial

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QDialog, QDialogButtonBox, QVBoxLayout, QWidget, QFormLayout, \
    QLineEdit


class SystemTreeViewItemContextMenu(QMenu):

    def __init__(self, parent_item):
        from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items import \
            TreeViewItemFromStellarSystemElement
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
        self.delete_permanently_action.triggered.connect(partial(self.delete_permanently_process, True))

    def _create_menu_actions(self):
        self.details_action = QAction("&Details...", self)
        self.delete_permanently_action = QAction(f"&Delete Permanently...", self)

    def details_action_process(self):
        pass

    def delete_permanently_process(self, ask_question=True):
        from .standard_items import TreeViewItemFromString
        parent: TreeViewItemFromString = self.parent_item.parent()
        if ask_question:
            question = QMessageBox.question(self, 'Delete permanently?', f"Are you sure you want to permanently delete "
                                                                         f"{self.parent_item.ssc_object.name}?",
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


# class BinarySystemTreeViewItemContextMenu(SystemTreeViewItemContextMenu):
#
#     def __init__(self, parent_item):
#         super().__init__(parent_item)
#
#     def _create_menu(self):
#         super()._create_menu()
#
#     def _connect_actions(self):
#         super()._connect_actions()
#
#     def _create_menu_actions(self):
#         super()._create_menu_actions()


class MultiStellarSystemTreeViewItemContextMenu(SystemTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

    def details_action_process(self):
        self.details_dialog = SystemDetailsDialog(self.parent_item)
        self.details_dialog.show()


class StellarSystemTreeViewItemContextMenu(SystemTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

    def details_action_process(self):
        self.details_dialog = SystemDetailsDialog(self.parent_item)
        self.details_dialog.show()


class PlanetarySystemTreeViewItemContextMenu(SystemTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

    def details_action_process(self):
        self.details_dialog = SystemDetailsDialog(self.parent_item)
        self.details_dialog.show()


class SystemDetailsDialog(QDialog):

    def __init__(self, parent_item):
        from .standard_items import TreeViewItemFromStellarSystemElement
        self.parent_item: TreeViewItemFromStellarSystemElement = parent_item
        super().__init__(self.parent_item.model().parent().parent())
        self.setModal(False)
        self.setWindowTitle(f'{self.parent_item.ssc_object.name} details')

        self._set_button_box()
        self._set_dialog_widget()

        layout = QVBoxLayout()
        layout.addWidget(self.dialog_widget)
        layout.addWidget(self.button_box)
        layout.addStretch()
        self.setLayout(layout)

    def _set_dialog_widget(self):
        self.dialog_widget = QWidget()

        self.name_line_edit = QLineEdit(self.parent_item.ssc_object.name)

        layout = QFormLayout()
        layout.addRow('Name', self.name_line_edit)
        self.dialog_widget.setLayout(layout)

    def _set_button_box(self):
        self.button_box = QDialogButtonBox((QDialogButtonBox.Cancel | QDialogButtonBox.Ok), self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Enter or a0.key() == Qt.Key_Return or a0.key() == Qt.Key_Escape:
            return
        super().keyPressEvent(a0)

    def accept(self) -> None:
        self.parent_item.ssc_object.name = self.name_line_edit.text()
        self.parent_item.update_text()
        super().accept()

    def reject(self) -> None:
        super().reject()




