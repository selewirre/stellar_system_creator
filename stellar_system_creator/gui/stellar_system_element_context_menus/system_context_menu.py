import os
from functools import partial

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QDialog, QDialogButtonBox, QVBoxLayout, QWidget, QFormLayout, \
    QLineEdit, QFileDialog
from stellar_system_creator.filing import save as save_ssc_object, load_ssc_light, save_as_ssc_light, load as load_ssc, \
    export_object_to_pdf, export_object_to_csv, export_object_to_json
from stellar_system_creator.stellar_system_elements.stellar_system import StellarSystem, MultiStellarSystemSType


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
        self.addAction(self.save_to_file_action)
        self.addAction(self.export_to_file_action)

    def _connect_actions(self):
        self.details_action.triggered.connect(self.details_action_process)
        self.delete_permanently_action.triggered.connect(partial(self.delete_permanently_process, True))
        self.replace_from_file_action.triggered.connect(self.replace_from_file_process)
        self.save_to_file_action.triggered.connect(self.save_to_file_process)
        self.export_to_file_action.triggered.connect(self.export_to_file_process)

    def _create_menu_actions(self):
        self.details_action = QAction("&Details...", self)
        self.delete_permanently_action = QAction(f"&Delete Permanently...", self)
        self.replace_from_file_action = QAction(f"&Replace from file...", self)
        self.save_to_file_action = QAction(f"&Save to file...", self)
        self.export_to_file_action = QAction(f"&Export to file...", self)

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

                if parent.model() is not None:
                    from stellar_system_creator.gui.gui_image_rendering import RenderingSettingsDialog
                    from stellar_system_creator.gui.gui_image_rendering import SystemImageWidget
                    rendering_dialog: RenderingSettingsDialog = parent.model().parent().parent().parent(). \
                        findChild(SystemImageWidget).rendering_settings_dialog
                    rendering_dialog.reset_available_systems_drop_down()

    def replace_from_file_process(self):
        pass

    def save_to_file_process(self):
        ssc_object = self.parent_item.ssc_object
        filename: str = QFileDialog.getSaveFileName(self, 'Save Project', '',
                                                    "Stellar System Creator Light Files (*.sscl);;"
                                                    "Stellar System Creator Files (*.ssc);;"
                                                    "All Files (*);;")[0]
        if filename != '':
            if filename.endswith('.ssc'):
                save_ssc_object(ssc_object, filename)
            else:
                save_as_ssc_light(ssc_object, filename)
        else:
            return

    def export_to_file_process(self):
        ssc_object = self.parent_item.ssc_object
        filename: str = QFileDialog.getSaveFileName(self, 'Save Project', '',
                                                    "Portable Document Files (*.pdf);;"
                                                    "Comma-Separated Values (*.csv);;"
                                                    "JavaScript Open Notation (*.json);;"
                                                    "All Files (*)")[0]

        if filename != '':
            if filename.endswith('.pdf'):
                export_object_to_pdf(ssc_object, filename)
            elif filename.endswith('.csv'):
                export_object_to_csv(ssc_object, filename)
            elif filename.endswith('.json'):
                export_object_to_json(ssc_object, filename)
            else:
                message_box = QMessageBox()
                message_box.setIcon(QMessageBox.Information)
                message_box.setWindowTitle("'Export Project As' has failed...")
                message_box.setText(f"File '{filename}' does not end in .pdf, .csv, or .json.")
                message_box.exec()
        else:
            return


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
        self.addSeparator()
        self.addAction(self.replace_from_file_action)

    def _connect_actions(self):
        super()._connect_actions()

    def _create_menu_actions(self):
        super()._create_menu_actions()

    def details_action_process(self):
        self.details_dialog = SystemDetailsDialog(self.parent_item)
        self.details_dialog.show()

    def replace_from_file_process(self):

        filename = QFileDialog.getOpenFileName(self, 'Open Project(s)', '',
                                               "All Files (*);;Stellar System Creator Light Files (*.sscl);;"
                                               "Stellar System Creator Files (*.ssc)")[0]
        if filename == '':
            return
        elif not os.path.exists(filename) and not (filename.endswith('.sscl') or filename.endswith('.ssc')):
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("'Replace from file' has failed...")
            message_box.setText(f"File '{filename}' is not compatible or does not exist.")
            message_box.exec()
            return

        if filename.endswith('ssc'):
            new_stellar_system = load_ssc(filename)
        else:
            new_stellar_system = load_ssc_light(filename, set_new_uuids=True)

        if not isinstance(new_stellar_system, StellarSystem):
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("'Add from file' has failed...")
            message_box.setText(f"The {filename} does not contain a Stellar System. ")
            message_box.exec()
            return

        from stellar_system_creator.gui.stellar_system_element_context_menus.standard_items \
            import TreeViewItemFromStellarSystemElement as tvifsse, TreeViewItemFromString
        # noinspection PyTypeChecker
        tree_view_item: TreeViewItemFromString = self.parent_item.parent()

        parent_multi_stellar_system: MultiStellarSystemSType = tree_view_item.ssc_parent
        parent_binary = parent_multi_stellar_system.parent
        old_stellar_system = self.parent_item.ssc_object

        parent_binary.remove_child(old_stellar_system.parent)
        if parent_binary.primary_body == old_stellar_system.parent:
            parent_binary.primary_body = new_stellar_system.parent
        elif parent_binary.secondary_body == old_stellar_system.parent:
            parent_binary.secondary_body = new_stellar_system.parent
        parent_binary.__post_init__()

        parent_multi_stellar_system.remove_child(old_stellar_system)
        parent_multi_stellar_system.add_child(new_stellar_system)
        new_stellar_system.reset_system_plot()
        parent_multi_stellar_system.reset_system_plot()

        new_tree_view_item = tvifsse(new_stellar_system)
        tree_view_item.appendRow(new_tree_view_item)
        new_tree_view_item.update_text()

        from stellar_system_creator.gui.gui_project_tree_view import set_stellar_system_tree_model_from_ssc_object
        set_stellar_system_tree_model_from_ssc_object(new_tree_view_item, new_stellar_system)

        from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
        tree_view: ProjectTreeView = new_tree_view_item.model().parent()
        tree_view.expandRecursively(new_tree_view_item.index())

        self.delete_permanently_process(False)


class PlanetarySystemTreeViewItemContextMenu(SystemTreeViewItemContextMenu):

    def __init__(self, parent_item):
        super().__init__(parent_item)

    def _create_menu(self):
        super()._create_menu()
        self.addSeparator()
        self.addAction(self.delete_permanently_action)

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
