from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

import hou

import webbrowser
import logging
import json
import os

from vex_manager.gui.file_explorer_widget import FileExplorerWidget
from vex_manager.gui.vex_editor_widget import VEXEditorWidget
from vex_manager.gui.preferences_ui import PreferencesUI
from vex_manager.config import WrangleNodes
import vex_manager.utils as utils
import vex_manager.core as core


logger = logging.getLogger(f'vex_manager.{__name__}')


class VEXManagerUI(QtWidgets.QWidget):
    WINDOW_NAME = 'vexManager'
    WINDOW_TITLE = 'VEX Manager'

    def __init__(self) -> None:
        super().__init__()

        self.preferences_path = utils.get_preferences_path()
        self.preferences_ui = PreferencesUI(self, QtCore.Qt.Dialog)

        self.library_path = ''
        self.current_vex_file_path = ''

        self.resize(800, 600)
        self.setObjectName(VEXManagerUI.WINDOW_NAME)
        self.setParent(hou.qt.mainWindow(), QtCore.Qt.Dialog)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(VEXManagerUI.WINDOW_TITLE)

        self._create_widgets()
        self._create_layouts()
        self._create_connections()
        self._load_preferences()
        self._update()

    def _create_widgets(self) -> None:
        self.menu_bar = QtWidgets.QMenuBar()

        edit_menu = self.menu_bar.addMenu('Edit')
        edit_menu.addAction('Preferences', self._open_preferences)

        help_menu = self.menu_bar.addMenu('Help')
        help_menu.addAction('Help on VEX Manager', self._open_help)

        self.file_explorer_widget = FileExplorerWidget()

        self.vex_editor_widget = VEXEditorWidget()

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(QtCore.QMargins(6, 3, 6, 6))
        main_layout.setMenuBar(self.menu_bar)
        main_layout.setSpacing(3)

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

        splitter.setCollapsible(0, True)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(1, 1)

    def _create_connections(self) -> None:
        self.preferences_ui.on_save_clicked.connect(self._on_save_clicked_preferences_ui)

        self.file_explorer_widget.current_wrangle_node_text_changed.connect(
            self._file_explorer_current_wrangle_node_text_changed)
        self.file_explorer_widget.current_item_changed.connect(self._context_explorer_current_item_changed_widget)
        self.file_explorer_widget.current_item_renamed.connect(self._context_explorer_current_item_renamed_widget)

        self.vex_editor_widget.name_editing_finished.connect(self._vex_editor_name_editing_finished_widget)
        self.vex_editor_widget.save_clicked.connect(self._vex_editor_saved_clicked_widget)
        self.vex_editor_widget.create_wrangle_node_clicked.connect(self._vex_editor_create_wrangle_node_clicked_widget)
        self.vex_editor_widget.insert_code_clicked.connect(self._vex_editor_insert_code_clicked_widget)

    def _load_preferences(self) -> None:
        preferences = {}

        if os.path.exists(self.preferences_path):
            with open(self.preferences_path, 'r') as file_for_read:
                preferences = json.load(file_for_read)

        self.library_path = preferences.get('library_path', '')

    def _open_preferences(self) -> None:
        self.preferences_ui.show()

    @staticmethod
    def _open_help() -> None:
        webbrowser.open('https://github.com/mauriciogonzalezsoto/vex-manager')

    def _on_save_clicked_preferences_ui(self) -> None:
        self._load_preferences()
        self._update()

    def _file_explorer_current_wrangle_node_text_changed(self) -> None:
        self.vex_editor_widget.set_wrangle_node_type(self.file_explorer_widget.get_current_wrangle_node_type())
        self.vex_editor_widget.set_file_path(self.current_vex_file_path)
        self.vex_editor_widget.display_code()

    def _context_explorer_current_item_changed_widget(self, file_path: str) -> None:
        self.current_vex_file_path = file_path
        self.vex_editor_widget.set_file_path(self.current_vex_file_path)
        self.vex_editor_widget.display_code()

    def _context_explorer_current_item_renamed_widget(self, file_path: str) -> None:
        self.current_vex_file_path = file_path
        self.vex_editor_widget.set_file_path(self.current_vex_file_path)

    def _vex_editor_name_editing_finished_widget(self, new_name: str) -> None:
        self.file_explorer_widget.rename_current_item(new_name)

    def _vex_editor_saved_clicked_widget(self) -> None:
        self.file_explorer_widget.set_current_path(self.vex_editor_widget.get_current_file_path())

    def _vex_editor_create_wrangle_node_clicked_widget(self) -> None:
        current_wrangle_node_type = self.file_explorer_widget.get_current_wrangle_node_type()

        wrangle_node = core.create_wrangle_node(wrangle_type=current_wrangle_node_type)

        if wrangle_node:
            core.insert_vex_code(node=wrangle_node, vex_code=self.vex_editor_widget.get_vex_code())

    def _vex_editor_insert_code_clicked_widget(self) -> None:
        selected_nodes = hou.selectedNodes()

        if selected_nodes:
            core.insert_vex_code(node=selected_nodes[-1], vex_code=self.vex_editor_widget.get_vex_code())
        else:
            logger.warning('There is no node selected.')

    def _update(self) -> None:
        self.file_explorer_widget.set_library_path(self.library_path)

        self.vex_editor_widget.set_library_path(self.library_path)
        self.vex_editor_widget.set_wrangle_node_type(self.file_explorer_widget.get_current_wrangle_node_type())

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        super().closeEvent(event)

        self.file_explorer_widget.clear_file_system_watcher()

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
