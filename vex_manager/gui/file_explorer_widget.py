from PySide2 import QtWidgets
from PySide2 import QtCore
import shiboken2

import hou

from pathlib import Path
import logging
import json
import os

from vex_manager.gui.file_explorer_tree_widget import FileExplorerTreeWidget
from vex_manager.config import WrangleNodes
import vex_manager.utils as utils
import vex_manager.core as core


logger = logging.getLogger(f'vex_manager.{__name__}')


class FileExplorerWidget(QtWidgets.QWidget):
    current_item_changed = QtCore.Signal(str)
    current_item_renamed = QtCore.Signal(str)
    current_wrangle_node_text_changed = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()

        self.preferences_path = utils.get_preferences_path()

        self.display_dialog_when_deleting_a_file = True

        self.library_path = ''
        self.current_item_path = ''

        self.file_system_watcher = QtCore.QFileSystemWatcher()
        self.number_of_files = -1

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
        self.file_system_watcher.directoryChanged.connect(self._directory_changed_file_system_watcher)

        self.wrangle_nodes_combo_box.currentTextChanged.connect(self._wrangle_nodes_current_text_changed_combo_box)
        self.search_line_edit.textChanged.connect(self._search_text_changed_line_edit)
        self.file_explorer_tree_widget.currentItemChanged.connect(self._file_explorer_current_item_changed_tree_widget)
        self.file_explorer_tree_widget.item_renamed.connect(self._file_explorer_item_renamed_tree_widget)
        self.new_push_button.clicked.connect(self._new_clicked_push_button)
        self.delete_push_button.clicked.connect(self._delete_clicked_push_button)

    def _load_preferences(self) -> None:
        settings = {}

        if os.path.exists(self.preferences_path):
            with open(self.preferences_path, 'r') as file_for_read:
                settings = json.load(file_for_read)

        self.display_dialog_when_deleting_a_file = settings.get('display_dialog_when_deleting_a_file', True)

    def _directory_changed_file_system_watcher(self) -> None:
        folder_path = os.path.join(self.library_path, self.wrangle_nodes_combo_box.currentData())
        vex_files = core.get_vex_files(folder_path)

        if self.number_of_files != len(vex_files):
            self._create_tree_widget_items()
            self.select_current_item()

            logger.debug('File system watcher updated files.')

    def _wrangle_nodes_current_text_changed_combo_box(self) -> None:
        self._set_file_system_watcher()
        self._create_tree_widget_items()

        self.current_wrangle_node_text_changed.emit()

    def _search_text_changed_line_edit(self, text: str) -> None:
        text = text.lower()

        for i in range(self.file_explorer_tree_widget.topLevelItemCount()):
            item = self.file_explorer_tree_widget.topLevelItem(i)
            item_text = item.text(0)
            item.setHidden(text not in item_text.lower())

    def _file_explorer_current_item_changed_tree_widget(self, current: QtWidgets.QTreeWidgetItem) -> None:
        data = current.data(0, QtCore.Qt.UserRole) if current else ''

        self.current_item_changed.emit(data)

    def _file_explorer_item_renamed_tree_widget(self, file_path: str) -> None:
        self.current_item_renamed.emit(file_path)

    def _new_clicked_push_button(self) -> None:

        if self.library_path:
            if os.path.exists(self.library_path):
                folder_path = os.path.join(
                    self.library_path,
                    self.wrangle_nodes_combo_box.currentData(QtCore.Qt.UserRole)
                )

                self.current_item_path, base_name = core.create_new_vex_file(folder_path)
            else:
                logger.error(f'Library path {self.library_path!r} does not exist.')
        else:
            logger.error('Library path not set.')

        self._set_file_system_watcher()
        self.select_current_item()

    def _delete_clicked_push_button(self) -> None:
        selected_items = self.file_explorer_tree_widget.selectedItems()

        if selected_items:
            self._load_preferences()

            result = 0  # Result = 0 means that the user selected 'Yes'.

            if self.display_dialog_when_deleting_a_file:
                result = hou.ui.displayCustomConfirmation(
                    'Delete selected VEX file?',
                    buttons=('Yes', 'No'),
                    close_choice=1,
                    default_choice=0,
                    suppress=hou.confirmType.NoConfirmType,
                    title='Delete'
                )

            if not result:
                item = selected_items[0]
                file_path = item.data(0, QtCore.Qt.UserRole)
                shiboken2.delete(item)
                core.delete_file(file_path)
        else:
            logger.debug('No VEX file selected to delete.')

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
            vex_files = core.get_vex_files(folder_path)

            self.number_of_files = len(vex_files)

            for file_path, base_name in vex_files:
                tree_widget_item = QtWidgets.QTreeWidgetItem()
                tree_widget_item.setText(0, base_name)
                tree_widget_item.setData(0, QtCore.Qt.UserRole, file_path)
                self.file_explorer_tree_widget.addTopLevelItem(tree_widget_item)

    def clear_file_system_watcher(self) -> None:
        file_system_watcher_directories = self.file_system_watcher.directories()

        if file_system_watcher_directories:
            self.file_system_watcher.removePaths(file_system_watcher_directories)

    def select_current_item(self) -> None:
        base_name = Path(self.current_item_path).stem
        items = self.file_explorer_tree_widget.findItems(base_name, QtCore.Qt.MatchExactly, 0)

        if items:
            item = items[0]
            item_data = item.data(0, QtCore.Qt.UserRole)

            if os.path.normpath(item_data) == os.path.normpath(self.current_item_path):
                self.file_explorer_tree_widget.setCurrentItem(item)

                logger.debug(f'{item.text(0)!r} item selected.')

    def _set_file_system_watcher(self) -> None:
        self.clear_file_system_watcher()

        file_system_watcher_path = os.path.join(self.library_path, self.wrangle_nodes_combo_box.currentData())

        if os.path.exists(self.library_path):
            self.file_system_watcher.addPath(self.library_path)

        if os.path.exists(file_system_watcher_path):
            self.file_system_watcher.addPath(file_system_watcher_path)

            logger.debug(f'File system watcher set to {file_system_watcher_path!r}')

    def get_current_wrangle_node_type(self) -> str:
        return self.wrangle_nodes_combo_box.currentData()

    def rename_current_item(self, new_name: str) -> None:
        current_item = self.file_explorer_tree_widget.currentItem()
        self.file_explorer_tree_widget.rename_item(column=0, item=current_item, new_name=new_name)

    def set_current_path(self, file_path: str) -> None:
        self.current_item_path = file_path

    def set_current_wrangle_node(self, wrangle_node_name: str, wrangle_node_type: str) -> None:
        self.wrangle_nodes_combo_box.setCurrentText(f'{wrangle_node_name} ({wrangle_node_type})')

    def set_library_path(self, library_path: str) -> None:
        self.library_path = library_path

        self._set_file_system_watcher()
        self._create_tree_widget_items()
