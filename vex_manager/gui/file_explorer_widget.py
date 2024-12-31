from PySide2 import QtWidgets
from PySide2 import QtCore
import shiboken2

import hou

from pathlib import Path
import logging
import json
import os

from vex_manager.gui.file_explorer_tree_widget import FileExplorerTreeWidget
import vex_manager.utils as utils
import vex_manager.core as core


logger = logging.getLogger(f'vex_manager.{__name__}')


class FileExplorerWidget(QtWidgets.QWidget):
    current_item_changed = QtCore.Signal(str)
    current_item_renamed = QtCore.Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.preferences_path = utils.get_preferences_path()

        self.warn_before_deleting_a_file = True

        self.library_path = ''
        self.current_item_path = ''

        self.file_system_watcher = QtCore.QFileSystemWatcher()
        self.number_of_files = -1

        self._create_widgets()
        self._create_layouts()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.search_line_edit = QtWidgets.QLineEdit()
        self.search_line_edit.setPlaceholderText('Search...')

        self.file_explorer_tree_widget = FileExplorerTreeWidget()

        self.new_push_button = QtWidgets.QPushButton('New')

        self.delete_push_button = QtWidgets.QPushButton('Delete')

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
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

        self.warn_before_deleting_a_file = settings.get('warn_before_deleting_a_file', True)

    def _directory_changed_file_system_watcher(self) -> None:
        vex_files = core.get_vex_files(self.library_path)

        if self.number_of_files != len(vex_files):
            self._create_tree_widget_items()
            self.select_current_item()
        else:
            item_paths = []
            item_path_renamed = ''
            file_path_renamed = ''

            items = self.file_explorer_tree_widget.get_top_level_items()

            for item in items:
                data = item.data(0, QtCore.Qt.UserRole)
                item_paths.append(data)

            for item_path in item_paths:
                if item_path not in vex_files:
                    item_path_renamed = item_path

            for file_path in vex_files:
                if file_path not in item_paths:
                    file_path_renamed = file_path

            item = self.file_explorer_tree_widget.find_item_by_path(item_path_renamed)

            if item:
                base_name = Path(file_path_renamed).stem

                item.setText(0, base_name)
                item.setData(0, QtCore.Qt.UserRole, file_path_renamed)

                self.current_item_renamed.emit(file_path_renamed)

        logger.debug('File system watcher updated files.')

    def _search_text_changed_line_edit(self, text: str) -> None:
        text = text.lower()
        items = self.file_explorer_tree_widget.get_top_level_items()

        for item in items:
            item_text = item.text(0)
            item.setHidden(text not in item_text.lower())

    def _file_explorer_current_item_changed_tree_widget(self, current: QtWidgets.QTreeWidgetItem) -> None:
        data = current.data(0, QtCore.Qt.UserRole) if current else ''

        self.current_item_changed.emit(data)

    def _file_explorer_item_renamed_tree_widget(self, file_path: str) -> None:
        self.current_item_renamed.emit(file_path)

    def _new_clicked_push_button(self) -> None:
        self.current_item_path, base_name = core.create_new_vex_file(self.library_path)

        self._set_file_system_watcher()
        self.select_current_item()

    def _delete_clicked_push_button(self) -> None:
        selected_items = self.file_explorer_tree_widget.selectedItems()

        if selected_items:
            self._load_preferences()

            result = 0  # Result = 0 means that the user selected 'Yes'.

            if self.warn_before_deleting_a_file:
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

    def _create_tree_widget_items(self) -> None:
        self.file_explorer_tree_widget.clear()

        if self.library_path:
            vex_files = core.get_vex_files(self.library_path)
            self.number_of_files = len(vex_files)

            for file_path in vex_files:
                tree_widget_item = QtWidgets.QTreeWidgetItem()
                tree_widget_item.setText(0, Path(file_path).stem)
                tree_widget_item.setData(0, QtCore.Qt.UserRole, file_path)
                self.file_explorer_tree_widget.addTopLevelItem(tree_widget_item)

    def _set_file_system_watcher(self) -> None:
        self.clear_file_system_watcher()

        if os.path.exists(self.library_path):
            self.file_system_watcher.addPath(self.library_path)

        if os.path.exists(self.library_path):
            self.file_system_watcher.addPath(self.library_path)

            logger.debug(f'File system watcher set to {self.library_path!r}')

    def clear_file_system_watcher(self) -> None:
        file_system_watcher_directories = self.file_system_watcher.directories()

        if file_system_watcher_directories:
            self.file_system_watcher.removePaths(file_system_watcher_directories)

    def get_library_path(self) -> str:
        return self.library_path

    def select_current_item(self) -> None:
        item = self.file_explorer_tree_widget.find_item_by_path(self.current_item_path)

        if item:
            self.file_explorer_tree_widget.setCurrentItem(item)

            logger.debug(f'{item.text(0)!r} item selected.')

    def rename_current_item(self, new_name: str) -> None:
        current_item = self.file_explorer_tree_widget.currentItem()
        self.file_explorer_tree_widget.rename_item(column=0, item=current_item, new_name=new_name)

    def set_current_path(self, file_path: str) -> None:
        self.current_item_path = file_path

    def set_library_path(self, library_path: str) -> None:
        self.library_path = library_path

        self._set_file_system_watcher()
        self._create_tree_widget_items()
