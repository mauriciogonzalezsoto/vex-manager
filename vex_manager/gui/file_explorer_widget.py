from PySide2 import QtWidgets
from PySide2 import QtCore

import shiboken2
import logging
import glob
import os
import re

from vex_manager.gui.file_explorer_tree_widget import FileExplorerTreeWidget
from vex_manager.config import WrangleNodes


logger = logging.getLogger(f'vex_manager.{__name__}')


class FileExplorerWidget(QtWidgets.QWidget):
    current_item_changed = QtCore.Signal(str)

    def __init__(self) -> None:
        super(FileExplorerWidget, self).__init__()

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
        self.new_push_button.clicked.connect(self._new_clicked_push_button)
        self.delete_push_button.clicked.connect(self._delete_clicked_push_button)

    def _wrangle_nodes_current_text_changed_combo_box(self) -> None:
        self._create_tree_widget_items()

    def _search_text_changed_line_edit(self, text: str) -> None:
        text = text.lower()

        for i in range(self.file_explorer_tree_widget.topLevelItemCount()):
            item = self.file_explorer_tree_widget.topLevelItem(i)

            if text in item.text(0):
                item.setHidden(False)
            else:
                item.setHidden(True)

    def _file_explorer_current_item_changed_tree_widget(self, current: QtWidgets.QTreeWidgetItem) -> None:
        self.current_item_changed.emit(current.data(0, QtCore.Qt.UserRole) if current else '')

    def _new_clicked_push_button(self) -> None:
        if self.library_path:
            is_new_vex_file_name_exists = False
            new_vex_file_name = 'VEX01'
            value = 1

            top_level_items = self.file_explorer_tree_widget.get_top_level_items()
            top_level_items.sort(reverse=True)

            for item in top_level_items:
                if item.text(0) == new_vex_file_name:
                    is_new_vex_file_name_exists = True
                    break

            if is_new_vex_file_name_exists:
                for item in top_level_items:
                    match = re.search(r'VEX(\d{2})', item.text(0))

                    if match:
                        current_value = int(match.group(1))

                        if value <= current_value:
                            value = current_value + 1

            new_vex_file_name = f'VEX{value:02d}'
            vex_file_folder_path = os.path.join(self.library_path, self.wrangle_nodes_combo_box.currentData())

            new_vex_file_path = os.path.join(vex_file_folder_path, f'{new_vex_file_name}.vex')
            new_vex_file_path = new_vex_file_path.replace('\\', '/')

            tree_widget_item = QtWidgets.QTreeWidgetItem()
            tree_widget_item.setData(0, QtCore.Qt.UserRole, new_vex_file_path)
            tree_widget_item.setSelected(True)
            tree_widget_item.setText(0, new_vex_file_name)
            self.file_explorer_tree_widget.addTopLevelItem(tree_widget_item)

            if not os.path.exists(vex_file_folder_path):
                os.mkdir(vex_file_folder_path)

                logger.info(f'\'{vex_file_folder_path}\' folder created.')

            if not os.path.exists(new_vex_file_path):
                open(new_vex_file_path, 'w').close()
        else:
            logger.warning('Library path not set.')

    def _delete_clicked_push_button(self) -> None:
        for item in self.file_explorer_tree_widget.selectedItems():
            file_path = item.data(0, QtCore.Qt.UserRole)
            shiboken2.delete(item)

            if os.path.exists(file_path):
                os.remove(file_path)

                logger.info(f'\'{file_path}\' deleted.')
            else:
                logger.warning(f'\'{file_path}\' does not exit.')

    def _create_combo_box_items(self) -> None:
        for wrangle_node in WrangleNodes:
            wrangle_node_name, wrangle_node = wrangle_node.value

            self.wrangle_nodes_combo_box.addItem(f'{wrangle_node_name} ({wrangle_node})', wrangle_node)

        self.wrangle_nodes_combo_box.insertSeparator(4)
        self.wrangle_nodes_combo_box.insertSeparator(7)
        self.wrangle_nodes_combo_box.insertSeparator(9)

    def _create_tree_widget_items(self) -> None:
        if self.library_path:
            self.file_explorer_tree_widget.clear()

            current_folder_path = os.path.join(
                self.library_path,
                self.wrangle_nodes_combo_box.currentData(QtCore.Qt.UserRole))

            if os.path.exists(current_folder_path):
                for vex_file_path in glob.glob(os.path.join(current_folder_path, '*.vex')):
                    base_name = os.path.basename(vex_file_path)
                    base_name = base_name.removesuffix('.vex')

                    vex_file_path = vex_file_path.replace('\\', '/')

                    tree_widget_item = QtWidgets.QTreeWidgetItem()
                    tree_widget_item.setText(0, base_name)
                    tree_widget_item.setData(0, QtCore.Qt.UserRole, vex_file_path)
                    self.file_explorer_tree_widget.addTopLevelItem(tree_widget_item)

    def get_wrangle_node_type(self) -> str:
        return self.wrangle_nodes_combo_box.currentData()

    def set_library_path(self, library_path: str) -> None:
        self.library_path = library_path

        self._create_tree_widget_items()
