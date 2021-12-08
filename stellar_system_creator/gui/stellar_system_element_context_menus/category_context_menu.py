from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.Qt import QStandardItem
from stellar_system_creator.stellar_system_elements.stellar_body import MainSequenceStar, Planet, AsteroidBelt, \
    Satellite, Trojan, TrojanSatellite


class CategoryBasedTreeViewItemContextMenu(QMenu):

    def __init__(self, parent_item):
        self.parent_item: QStandardItem = parent_item
        super().__init__(self.parent_item.parent())

        self._create_menu_actions()
        self._connect_actions()
        self._create_menu()

    def _create_menu(self):
        self.addSection(self.parent_item.text())
        self.addAction(self.add_element_action)
        self.addSeparator()
        self.addAction(self.expand_all_action)
        self.addAction(self.collapse_all_action)

    def _connect_actions(self):
        self.expand_all_action.triggered.connect(self.expand_all_process)
        self.collapse_all_action.triggered.connect(self.collapse_all_process)

    def _create_menu_actions(self):
        self.add_element_action = QAction(f"&Add {self.parent_item.text()[:-1]}...", self)
        self.expand_all_action = QAction(f"&Expand all", self)
        self.collapse_all_action = QAction(f"&Collapse all", self)

    def expand_all_process(self):
        from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
        tree_view: ProjectTreeView = self.parent_item.model().parent()
        tree_view.expandRecursively(self.parent_item.index())

    def collapse_all_process(self):
        from stellar_system_creator.gui.gui_project_tree_view import ProjectTreeView
        tree_view: ProjectTreeView = self.parent_item.model().parent()
        tree_view.collapse_recursively(self.parent_item)
