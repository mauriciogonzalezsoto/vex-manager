from PySide2 import QtWidgets
from PySide2 import QtCore
import shiboken2

import logging
import os

from vex_manager.gui.file_explorer_tree_widget import FileExplorerTreeWidget
from vex_manager.config import WrangleNodes
import vex_manager.core as core


logger = logging.getLogger(f'vex_manager.{__name__}')


class FileExplorerWidget(QtWidgets.QWidget):
    current_item_changed = QtCore.Signal(str)
    current_item_renamed = QtCore.Signal(str)
    current_wrangle_node_text_changed = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()

        self.library_path = ''

        self._create_widgets()
        self._create_layouts()
        self._create_connections()
        self._create_combo_box_items()

    def _create_widgets(self) -> None:
        self.wrangle_nodes_combo_box = QtWidgets.QComboBox()

        self.search_line_edit = QtWidgets.QLineEdit()
        self.search_line_edit.setPlaceholderText('Search...')

        self.file_explorer_tree_widget = FileExplorerTreeWidget()

        self.new_push_button = QtWidgets.QPushButton('New')

        self.delete_push_button = QtWidgets.QPushButton('Delete')

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.wrangle_nodes_combo_box)
        main_layout.addWidget(self.search_line_edit)
        main_layout.addWidget(self.file_explorer_tree_widget)
        main_layout.setContentsMargins(QtCore.QMargins())
        main_layout.setSpacing(3)

        edit_h_box_layout = QtWidgets.QHBoxLayout()
        edit_h_box_layout.addWidget(self.new_push_button)
        edit_h_box_layout.addWidget(self.delete_push_button)
        main_layout.addLayout(edit_h_box_layout)

    def _create_connections(self) -> None:
        self.wrangle_nodes_combo_box.currentTextChanged.connect(self._wrangle_nodes_current_text_changed_combo_box)
        self.search_line_edit.textChanged.connect(self._search_text_changed_line_edit)
        self.file_explorer_tree_widget.currentItemChanged.connect(self._file_explorer_current_item_changed_tree_widget)
        self.file_explorer_tree_widget.item_renamed.connect(self._file_explorer_item_renamed_tree_widget)
        self.new_push_button.clicked.connect(self._new_clicked_push_button)
        self.delete_push_button.clicked.connect(self._delete_clicked_push_button)

    def _wrangle_nodes_current_text_changed_combo_box(self) -> None:
        self._create_tree_widget_items()

        self.current_wrangle_node_text_changed.emit()

    def _search_text_changed_line_edit(self, text: str) -> None:
        text = text.lower()

        for i in range(self.file_explorer_tree_widget.topLevelItemCount()):
            item = self.file_explorer_tree_widget.topLevelItem(i)
            item.setHidden(text in item.text(0))

    def _file_explorer_current_item_changed_tree_widget(self, current: QtWidgets.QTreeWidgetItem) -> None:
        data = current.data(0, QtCore.Qt.UserRole) if current else ''

        self.current_item_changed.emit(data)

    def _file_explorer_item_renamed_tree_widget(self, file_path: str) -> None:
        self.current_item_renamed.emit(file_path)

    def _new_clicked_push_button(self) -> None:
        if self.library_path:
            folder_path = os.path.join(self.library_path, self.wrangle_nodes_combo_box.currentData(QtCore.Qt.UserRole))
            new_vex_file_path, base_name = core.create_new_vex_file(folder_path)

            tree_widget_item = QtWidgets.QTreeWidgetItem()
            tree_widget_item.setData(0, QtCore.Qt.UserRole, new_vex_file_path)
            tree_widget_item.setSelected(True)
            tree_widget_item.setText(0, base_name)
            self.file_explorer_tree_widget.addTopLevelItem(tree_widget_item)

        else:
            logger.warning('Library path not set.')

    def _delete_clicked_push_button(self) -> None:
        for item in self.file_explorer_tree_widget.selectedItems():
            file_path = item.data(0, QtCore.Qt.UserRole)
            shiboken2.delete(item)
            core.delete_file(file_path)

    def _create_combo_box_items(self) -> None:
        for wrangle_node in WrangleNodes:
            wrangle_node_name, wrangle_node_type = wrangle_node.value

            self.wrangle_nodes_combo_box.addItem(f'{wrangle_node_name} ({wrangle_node_type})', wrangle_node_type)

        self.wrangle_nodes_combo_box.insertSeparator(4)
        self.wrangle_nodes_combo_box.insertSeparator(7)
        self.wrangle_nodes_combo_box.insertSeparator(9)

    def _create_tree_widget_items(self) -> None:
        if self.library_path:
            self.file_explorer_tree_widget.clear()

            folder_path = os.path.join(self.library_path, self.wrangle_nodes_combo_box.currentData())

            for file_path, base_name in core.get_vex_files(folder_path):
                tree_widget_item = QtWidgets.QTreeWidgetItem()
                tree_widget_item.setText(0, base_name)
                tree_widget_item.setData(0, QtCore.Qt.UserRole, file_path)
                self.file_explorer_tree_widget.addTopLevelItem(tree_widget_item)

    def get_current_wrangle_node_type(self) -> str:
        return self.wrangle_nodes_combo_box.currentData()

    def rename_current_item(self, name: str) -> None:
        current_item = self.file_explorer_tree_widget.currentItem()
        self.file_explorer_tree_widget.rename_item(column=0, item=current_item, new_name=name)

    def set_current_wrangle_node(self, wrangle_node_name: str, wrangle_node_type: str) -> None:
        self.wrangle_nodes_combo_box.setCurrentText(f'{wrangle_node_name} ({wrangle_node_type})')

    def set_library_path(self, library_path: str) -> None:
        self.library_path = library_path

        self._create_tree_widget_items()
