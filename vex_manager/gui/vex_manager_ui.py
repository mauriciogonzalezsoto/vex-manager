from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

import hou

import webbrowser
import logging
import json
import os

import vex_manager.core.vex_manager as create_wrangle_node
from vex_manager.gui.file_explorer_widget import FileExplorerWidget
from vex_manager.gui.vex_editor_widget import VEXEditorWidget
from vex_manager.config import WrangleNodes


logger = logging.getLogger(f'vex_manager.{__name__}')


class VEXManagerUI(QtWidgets.QWidget):
    WINDOW_NAME = 'vexmanager'
    WINDOW_TITLE = 'VEX Manager'

    def __init__(self) -> None:
        super().__init__()

        self.current_vex_file_path = ''

        self.resize(800, 600)
        self.setObjectName(VEXManagerUI.WINDOW_NAME)
        self.setWindowTitle(VEXManagerUI.WINDOW_TITLE)

        self._create_widgets()
        self._create_layouts()
        self._create_connections()
        self._get_settings_path()
        self._load_settings()

    def _create_widgets(self) -> None:
        self.menu_bar = QtWidgets.QMenuBar()

        edit_menu = self.menu_bar.addMenu('Edit')
        edit_menu.addAction('Save Settings', self._save_settings)

        help_menu = self.menu_bar.addMenu('Help')
        help_menu.addAction('Help on VEX Manager', self._open_help)

        self.library_path_line_edit = QtWidgets.QLineEdit()
        self.library_path_line_edit.setPlaceholderText('Library path...')

        push_button_size = self.library_path_line_edit.sizeHint().height()

        self.select_library_path_push_button = QtWidgets.QPushButton('...')
        self.select_library_path_push_button.setFixedSize(QtCore.QSize(push_button_size, push_button_size))

        self.file_explorer_widget = FileExplorerWidget()

        self.vex_editor_widget = VEXEditorWidget()

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        main_layout.setMenuBar(self.menu_bar)
        main_layout.setSpacing(3)

        library_path_h_box_layout = QtWidgets.QHBoxLayout()
        library_path_h_box_layout.addWidget(self.library_path_line_edit)
        library_path_h_box_layout.addWidget(self.select_library_path_push_button)
        main_layout.addLayout(library_path_h_box_layout)

        splitter = QtWidgets.QSplitter()
        main_layout.addWidget(splitter)

        left_widget = QtWidgets.QWidget()
        splitter.addWidget(left_widget)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.file_explorer_widget)
        left_layout.setContentsMargins(QtCore.QMargins())
        left_widget.setLayout(left_layout)

        right_widget = QtWidgets.QWidget()
        splitter.addWidget(right_widget)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(self.vex_editor_widget)
        right_layout.setContentsMargins(QtCore.QMargins())
        right_widget.setLayout(right_layout)

        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(1, 1)

    def _create_connections(self) -> None:
        self.library_path_line_edit.editingFinished.connect(self._library_path_editing_finished_line_edit)
        self.select_library_path_push_button.clicked.connect(self._select_library_path_clicked_push_button)

        self.file_explorer_widget.current_item_changed.connect(self._context_explorer_current_item_changed_widget)
        self.file_explorer_widget.current_item_renamed.connect(self._context_explorer_current_item_renamed_widget)

        self.vex_editor_widget.name_editing_finished.connect(self._vex_editor_name_editing_finished_widget)
        self.vex_editor_widget.create_wrangle_node_clicked.connect(self._vex_editor_create_wrangle_node_clicked_widget)
        self.vex_editor_widget.insert_code_clicked.connect(self._vex_editor_insert_code_clicked_widget)

    def _load_settings(self) -> None:
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r') as file_for_read:
                settings = json.load(file_for_read)

            self.library_path_line_edit.setText(settings.get('library_path', ''))

            self._library_path_editing_finished_line_edit()

    def _save_settings(self) -> None:
        settings = {'library_path': self.library_path_line_edit.text()}

        with open(self.settings_path, 'w') as file_for_write:
            json.dump(settings, file_for_write, indent=4)

    @staticmethod
    def _open_help() -> None:
        webbrowser.open('https://github.com/mauriciogonzalezsoto/vex-manager')

    def _library_path_editing_finished_line_edit(self) -> None:
        text = self.library_path_line_edit.text()

        if text:
            if os.path.exists(text):
                self.file_explorer_widget.set_library_path(text)
            else:
                logger.error(f'{text!r} path does not exist.')

    def _select_library_path_clicked_push_button(self) -> None:
        library_path = hou.ui.selectFile(file_type=hou.fileType.Directory, title='Select Folder')

        if library_path:
            self.library_path_line_edit.setText(library_path)

            self.file_explorer_widget.set_library_path(library_path)

    def _context_explorer_current_item_changed_widget(self, file_path: str) -> None:
        self.current_vex_file_path = file_path
        self.vex_editor_widget.set_file_path(self.current_vex_file_path)
        self.vex_editor_widget.display_code()

    def _context_explorer_current_item_renamed_widget(self, file_path: str) -> None:
        self.current_vex_file_path = file_path
        self.vex_editor_widget.set_file_path(self.current_vex_file_path)

    def _vex_editor_name_editing_finished_widget(self, name: str) -> None:
        self.file_explorer_widget.rename_current_item(name)

    def _vex_editor_create_wrangle_node_clicked_widget(self) -> None:
        current_wrangle_node_type = self.file_explorer_widget.get_current_wrangle_node_type()

        wrangle_node = create_wrangle_node.create_wrangle_node(wrangle_type=current_wrangle_node_type)

        if wrangle_node:
            create_wrangle_node.insert_vex_code(node=wrangle_node, vex_file_path=self.current_vex_file_path)

    def _vex_editor_insert_code_clicked_widget(self) -> None:
        selected_nodes = hou.selectedNodes()

        if selected_nodes:
            create_wrangle_node.insert_vex_code(node=selected_nodes[-1], vex_file_path=self.current_vex_file_path)
        else:
            logger.warning('There is no node selected.')

    def _get_settings_path(self) -> None:
        home_path = os.path.expandvars('$HOME')
        houdini_version = hou.applicationVersionString()
        major, minor, patch = houdini_version.split('.')
        houdini_folder_path = os.path.join(home_path, f'houdini{major}.{minor}')

        self.settings_path = os.path.join(
            houdini_folder_path,
            f'{VEXManagerUI.WINDOW_NAME}.json')

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        super().showEvent(event)

        selected_nodes = hou.selectedNodes()

        if selected_nodes:
            selected_node = selected_nodes[-1]

            for wrangle_node in WrangleNodes:
                wrangle_node_name, wrangle_node_type = wrangle_node.value
                if selected_node.type().name() == wrangle_node_type:
                    self.file_explorer_widget.set_current_wrangle_node(
                        wrangle_node_name=wrangle_node_name,
                        wrangle_node_type=wrangle_node_type)

                    break
