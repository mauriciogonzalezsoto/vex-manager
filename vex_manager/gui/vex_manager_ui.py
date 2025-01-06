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
import vex_manager.utils as utils


logger = logging.getLogger(f"vex_manager.{__name__}")


class VEXManagerUI(QtWidgets.QWidget):
    WINDOW_NAME = "vexManager"
    WINDOW_TITLE = "VEX Manager"

    PREFERENCES_PATH = utils.get_preferences_path()

    def __init__(self) -> None:
        super().__init__()

        self.preferences_ui = PreferencesUI(self, QtCore.Qt.Dialog)

        self.library_path = ""
        self.current_vex_file_path = ""

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

        edit_menu = self.menu_bar.addMenu("Edit")
        edit_menu.addAction("Preferences", self._open_preferences)

        help_menu = self.menu_bar.addMenu("Help")
        help_menu.addAction("Help on VEX Manager", self._open_help)

        self.file_explorer_widget = FileExplorerWidget()

        self.vex_editor_widget = VEXEditorWidget()

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(6, 3, 6, 6)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.setSpacing(6)

        splitter = QtWidgets.QSplitter()
        main_layout.addWidget(splitter)

        left_widget = QtWidgets.QWidget()
        splitter.addWidget(left_widget)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.file_explorer_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        left_widget.setLayout(left_layout)

        right_widget = QtWidgets.QWidget()
        splitter.addWidget(right_widget)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(self.vex_editor_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        right_widget.setLayout(right_layout)

        splitter.setCollapsible(0, True)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(1, 1)

    def _create_connections(self) -> None:
        self.preferences_ui.on_save_clicked.connect(
            self._on_save_clicked_preferences_ui
        )

        self.file_explorer_widget.current_item_changed.connect(
            self._file_explorer_current_item_changed_widget
        )
        self.file_explorer_widget.current_item_renamed.connect(
            self._file_explorer_current_item_renamed_widget
        )

        self.vex_editor_widget.name_editing_finished.connect(
            self._vex_editor_name_editing_finished_widget
        )
        self.vex_editor_widget.save_clicked.connect(
            self._vex_editor_saved_clicked_widget
        )

    def _load_preferences(self) -> None:
        preferences = {}

        if os.path.exists(VEXManagerUI.PREFERENCES_PATH):
            with open(VEXManagerUI.PREFERENCES_PATH, "r") as file_for_read:
                preferences = json.load(file_for_read)

        self.library_path = preferences.get("library_path", "")

    def _open_preferences(self) -> None:
        self.preferences_ui.show()

    @staticmethod
    def _open_help() -> None:
        webbrowser.open("https://github.com/mauriciogonzalezsoto/vex-manager")

    def _on_save_clicked_preferences_ui(self) -> None:
        self._load_preferences()
        self._update()

        self.vex_editor_widget.vex_plain_text_editor.set_font_and_colors()

    def _file_explorer_current_item_changed_widget(self, file_path: str) -> None:
        self.current_vex_file_path = file_path
        self.vex_editor_widget.set_file_path(self.current_vex_file_path)
        self.vex_editor_widget.display_code()

    def _file_explorer_current_item_renamed_widget(self, file_path: str) -> None:
        self.current_vex_file_path = file_path
        self.vex_editor_widget.set_file_path(self.current_vex_file_path)

    def _vex_editor_name_editing_finished_widget(self, new_name: str) -> None:
        self.file_explorer_widget.rename_current_item(new_name)

    def _vex_editor_saved_clicked_widget(self) -> None:
        self.file_explorer_widget.set_current_path(
            self.vex_editor_widget.get_current_file_path()
        )

    def _update(self) -> None:
        if self.file_explorer_widget.get_library_path() != self.library_path:
            self.file_explorer_widget.set_library_path(self.library_path)

        if self.vex_editor_widget.get_library_path() != self.library_path:
            self.vex_editor_widget.set_library_path(self.library_path)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        super().closeEvent(event)

        self.file_explorer_widget.clear_file_system_watcher()

        self.preferences_ui.close()
