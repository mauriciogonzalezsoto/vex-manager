from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

import hou

import logging
import json
import os

from vex_manager.config import ColorScheme
import vex_manager.utils as utils

logger = logging.getLogger(f"vex_manager.{__name__}")


class PreferencesUI(QtWidgets.QWidget):
    WINDOW_NAME = "vexManagerPreferences"
    WINDOW_TITLE = "Preferences"

    GENERAL = "General"
    CODE_EDITOR = "Code Editor"
    TABS_AND_SPACING = "Tabs and Spacing"
    FONTS_AND_COLORS = "Fonts and Colors"

    PREFERENCES_PATH = utils.get_preferences_path()

    on_save_clicked = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget, f: QtCore.Qt.WindowFlags) -> None:
        super().__init__(parent, f)

        self.color_scheme = {}

        self.resize(400, 600)
        self.setObjectName(PreferencesUI.WINDOW_NAME)
        self.setWindowTitle(PreferencesUI.WINDOW_TITLE)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self._create_widgets()
        self._create_layouts()
        self._create_connections()
        self._load_preferences()

    def _create_widgets(self) -> None:
        self.preferences_categories_combo_box = QtWidgets.QComboBox()
        self.preferences_categories_combo_box.addItems(
            [
                PreferencesUI.GENERAL,
                PreferencesUI.CODE_EDITOR,
                PreferencesUI.FONTS_AND_COLORS,
                PreferencesUI.TABS_AND_SPACING,
            ]
        )

        self.library_path_line_edit = QtWidgets.QLineEdit()

        push_button_size = self.library_path_line_edit.sizeHint().height()

        self.select_library_path_push_button = QtWidgets.QPushButton("...")
        self.select_library_path_push_button.setFixedSize(
            QtCore.QSize(push_button_size, push_button_size)
        )

        self.warn_before_deleting_a_file_check_box = QtWidgets.QCheckBox(
            "Warn Before Deleting a File"
        )

        self.backspace_on_tab_stop_check_box = QtWidgets.QCheckBox(
            "Backspace on Tab Stop"
        )

        self.insert_closing_brackets_check_box = QtWidgets.QCheckBox(
            "Insert Closing Brackets"
        )

        self.insert_closing_quotes_check_box = QtWidgets.QCheckBox(
            "Insert Closing Quotes"
        )

        self.revert_to_default = QtWidgets.QPushButton("Revert to Default")
        self.revert_to_default.setVisible(False)

        self.font_combo_box = QtWidgets.QFontComboBox()

        self.font_size_spin_box = QtWidgets.QSpinBox()
        self.font_size_spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.font_size_spin_box.setFixedWidth(75)
        self.font_size_spin_box.setRange(6, 20)

        self.font_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.font_size_slider.setRange(6, 20)
        self.font_size_slider.setSingleStep(1)

        self.color_scheme_list_widget = QtWidgets.QListWidget()
        self.color_scheme_list_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum
        )

        self.tab_size_spin_box = QtWidgets.QSpinBox()
        self.tab_size_spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.tab_size_spin_box.setFixedWidth(75)
        self.tab_size_spin_box.setRange(1, 12)

        self.tab_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.tab_size_slider.setRange(1, 12)
        self.tab_size_slider.setSingleStep(1)

        self.auto_indent_check_box = QtWidgets.QCheckBox("Auto-indent")

        self.apply_push_button = QtWidgets.QPushButton("Apply")

        self.accept_push_button = QtWidgets.QPushButton("Accept")

        self.cancel_push_button = QtWidgets.QPushButton("Cancel")

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        preferences_categories_h_box_layout = QtWidgets.QHBoxLayout()
        preferences_categories_h_box_layout.addWidget(
            self.preferences_categories_combo_box
        )
        preferences_categories_h_box_layout.addStretch()
        preferences_categories_h_box_layout.addWidget(self.revert_to_default)
        main_layout.addLayout(preferences_categories_h_box_layout)

        self.general_widget = QtWidgets.QWidget()
        main_layout.addWidget(self.general_widget)

        general_v_box_layout = QtWidgets.QVBoxLayout()
        general_v_box_layout.setContentsMargins(6, 6, 6, 6)
        general_v_box_layout.setSpacing(6)
        self.general_widget.setLayout(general_v_box_layout)

        library_path_group_box = QtWidgets.QGroupBox("Library Path")
        general_v_box_layout.addWidget(library_path_group_box)

        library_path_h_box_layout = QtWidgets.QHBoxLayout()
        library_path_h_box_layout.addWidget(self.library_path_line_edit)
        library_path_h_box_layout.addWidget(self.select_library_path_push_button)
        library_path_h_box_layout.setContentsMargins(6, 6, 6, 6)
        library_path_h_box_layout.setSpacing(6)
        library_path_group_box.setLayout(library_path_h_box_layout)

        warning_dialogs_group_box = QtWidgets.QGroupBox("Main Window")
        general_v_box_layout.addWidget(warning_dialogs_group_box)

        warning_dialogs_v_box_layout = QtWidgets.QVBoxLayout()
        warning_dialogs_v_box_layout.addWidget(
            self.warn_before_deleting_a_file_check_box
        )
        warning_dialogs_v_box_layout.setContentsMargins(6, 6, 6, 6)
        warning_dialogs_v_box_layout.setSpacing(6)
        warning_dialogs_group_box.setLayout(warning_dialogs_v_box_layout)

        self.code_editor_widget = QtWidgets.QWidget()
        self.code_editor_widget.setVisible(False)
        main_layout.addWidget(self.code_editor_widget)

        code_editor_v_box_layout = QtWidgets.QVBoxLayout()
        code_editor_v_box_layout.setContentsMargins(6, 6, 6, 6)
        code_editor_v_box_layout.setSpacing(6)
        self.code_editor_widget.setLayout(code_editor_v_box_layout)

        code_editor_group_box = QtWidgets.QGroupBox("Options")
        code_editor_v_box_layout.addWidget(code_editor_group_box)

        code_editor_form_layout = QtWidgets.QFormLayout()
        code_editor_form_layout.addWidget(self.backspace_on_tab_stop_check_box)
        code_editor_form_layout.addWidget(self.insert_closing_brackets_check_box)
        code_editor_form_layout.addWidget(self.insert_closing_quotes_check_box)
        code_editor_form_layout.setContentsMargins(6, 6, 6, 6)
        code_editor_form_layout.setSpacing(6)
        code_editor_group_box.setLayout(code_editor_form_layout)

        self.fonts_and_colors_widget = QtWidgets.QWidget()
        self.fonts_and_colors_widget.setVisible(False)
        main_layout.addWidget(self.fonts_and_colors_widget)

        fonts_and_colors_v_box_layout = QtWidgets.QVBoxLayout()
        fonts_and_colors_v_box_layout.setContentsMargins(6, 6, 6, 6)
        fonts_and_colors_v_box_layout.setSpacing(6)
        self.fonts_and_colors_widget.setLayout(fonts_and_colors_v_box_layout)

        font_group_box = QtWidgets.QGroupBox("Font")
        fonts_and_colors_v_box_layout.addWidget(font_group_box)

        font_size_h_box_layout = QtWidgets.QHBoxLayout()
        font_size_h_box_layout.addWidget(self.font_size_spin_box)
        font_size_h_box_layout.addWidget(self.font_size_slider)

        font_form_layout = QtWidgets.QFormLayout()
        font_form_layout.addRow("Font ", self.font_combo_box)
        font_form_layout.addRow("Size ", font_size_h_box_layout)
        font_form_layout.setContentsMargins(6, 6, 6, 6)
        font_form_layout.setSpacing(6)
        font_group_box.setLayout(font_form_layout)

        color_group_box = QtWidgets.QGroupBox("Color")
        fonts_and_colors_v_box_layout.addWidget(color_group_box)

        color_h_box_layout = QtWidgets.QHBoxLayout()
        color_h_box_layout.addWidget(self.color_scheme_list_widget)
        color_h_box_layout.setContentsMargins(6, 6, 6, 6)
        color_h_box_layout.setSpacing(6)
        color_group_box.setLayout(color_h_box_layout)

        self.tabs_and_spacing_widget = QtWidgets.QWidget()
        self.tabs_and_spacing_widget.setVisible(False)
        main_layout.addWidget(self.tabs_and_spacing_widget)

        tab_and_spacing_v_box_layout = QtWidgets.QVBoxLayout()
        tab_and_spacing_v_box_layout.setContentsMargins(6, 6, 6, 6)
        tab_and_spacing_v_box_layout.setSpacing(6)
        self.tabs_and_spacing_widget.setLayout(tab_and_spacing_v_box_layout)

        tab_group_box = QtWidgets.QGroupBox("Tab")
        tab_and_spacing_v_box_layout.addWidget(tab_group_box)

        tab_size_h_box_layout = QtWidgets.QHBoxLayout()
        tab_size_h_box_layout.addWidget(self.tab_size_spin_box)
        tab_size_h_box_layout.addWidget(self.tab_size_slider)

        tab_form_layout = QtWidgets.QFormLayout()
        tab_form_layout.addRow("Tab Size ", tab_size_h_box_layout)
        tab_form_layout.setContentsMargins(6, 6, 6, 6)
        tab_form_layout.setSpacing(6)
        tab_group_box.setLayout(tab_form_layout)

        indenting_group_box = QtWidgets.QGroupBox("Indenting")
        tab_and_spacing_v_box_layout.addWidget(indenting_group_box)

        indenting_v_box_layout = QtWidgets.QVBoxLayout()
        indenting_v_box_layout.addWidget(self.auto_indent_check_box)
        indenting_v_box_layout.setContentsMargins(6, 6, 6, 6)
        indenting_v_box_layout.setSpacing(6)
        indenting_group_box.setLayout(indenting_v_box_layout)

        buttons_h_box_layout = QtWidgets.QHBoxLayout()
        buttons_h_box_layout.addWidget(self.apply_push_button)
        buttons_h_box_layout.addStretch()
        buttons_h_box_layout.addWidget(self.accept_push_button)
        buttons_h_box_layout.addWidget(self.cancel_push_button)
        main_layout.addStretch()
        main_layout.addLayout(buttons_h_box_layout)

    def _create_connections(self) -> None:
        self.preferences_categories_combo_box.currentTextChanged.connect(
            self._preferences_categories_current_text_changed_combo_box
        )

        self.library_path_line_edit.editingFinished.connect(
            self._library_path_editing_finished_line_edit
        )
        self.select_library_path_push_button.clicked.connect(
            self._select_library_path_clicked_push_button
        )

        self.font_size_spin_box.valueChanged.connect(
            self._font_size_value_changed_spin_box
        )
        self.font_size_slider.valueChanged.connect(self._font_size_value_changed_slider)

        self.revert_to_default.clicked.connect(
            self._revert_to_default_clicked_push_button
        )
        self.tab_size_spin_box.valueChanged.connect(
            self._tab_size_value_changed_spin_box
        )
        self.tab_size_slider.valueChanged.connect(self._tab_size_value_changed_slider)
        self.color_scheme_list_widget.itemClicked.connect(
            self._color_scheme_item_clicked_list_widget
        )

        self.apply_push_button.clicked.connect(self._apply_clicked_push_button)
        self.accept_push_button.clicked.connect(self._accept_clicked_push_button)
        self.cancel_push_button.clicked.connect(self.close)

    def _load_preferences(self) -> None:
        settings = {}

        if os.path.exists(PreferencesUI.PREFERENCES_PATH):
            with open(PreferencesUI.PREFERENCES_PATH, "r") as file_for_read:
                settings = json.load(file_for_read)

        self.library_path_line_edit.setText(settings.get("library_path", ""))
        self.warn_before_deleting_a_file_check_box.setChecked(
            settings.get("warn_before_deleting_a_file", True)
        )

        self.backspace_on_tab_stop_check_box.setChecked(
            settings.get("backspace_on_tab_stop", True)
        )
        self.insert_closing_brackets_check_box.setChecked(
            settings.get("insert_closing_brackets", True)
        )
        self.insert_closing_quotes_check_box.setChecked(
            settings.get("insert_closing_quotes", True)
        )

        self.font_combo_box.setCurrentText(settings.get("font", "Source Sans Pro"))
        self.font_size_spin_box.setValue(settings.get("font_size", 8))
        self.color_scheme = settings.get("color_scheme", {})

        if not self.color_scheme:
            for color_scheme in ColorScheme:
                color_scheme = color_scheme.value

                self.color_scheme[color_scheme["name"]] = color_scheme["color"]

        self.tab_size_spin_box.setValue(settings.get("tab_size", 4))
        self.auto_indent_check_box.setChecked(settings.get("auto_indent", True))

    def _save_preferences(self) -> None:
        settings = {
            "library_path": self.library_path_line_edit.text(),
            "warn_before_deleting_a_file": self.warn_before_deleting_a_file_check_box.isChecked(),
            "backspace_on_tab_stop": self.backspace_on_tab_stop_check_box.isChecked(),
            "insert_closing_brackets": self.insert_closing_brackets_check_box.isChecked(),
            "insert_closing_quotes": self.insert_closing_quotes_check_box.isChecked(),
            "font": self.font_combo_box.currentText(),
            "font_size": self.font_size_spin_box.value(),
            "color_scheme": self.color_scheme,
            "tab_size": self.tab_size_spin_box.value(),
            "auto_indent": self.auto_indent_check_box.isChecked(),
        }

        if PreferencesUI.PREFERENCES_PATH:
            with open(PreferencesUI.PREFERENCES_PATH, "w") as file_for_write:
                json.dump(settings, file_for_write, indent=4)
        else:
            logger.error(f"No preferences path.")

    def _preferences_categories_current_text_changed_combo_box(self) -> None:
        self.revert_to_default.setVisible(False)

        self.general_widget.setVisible(False)
        self.code_editor_widget.setVisible(False)
        self.fonts_and_colors_widget.setVisible(False)
        self.tabs_and_spacing_widget.setVisible(False)

        current_preferences_category = (
            self.preferences_categories_combo_box.currentText()
        )

        if current_preferences_category == PreferencesUI.GENERAL:
            self.general_widget.setVisible(True)
        elif current_preferences_category == PreferencesUI.CODE_EDITOR:
            self.code_editor_widget.setVisible(True)
        elif current_preferences_category == PreferencesUI.FONTS_AND_COLORS:
            self.revert_to_default.setVisible(True)
            self.fonts_and_colors_widget.setVisible(True)
        elif current_preferences_category == PreferencesUI.TABS_AND_SPACING:
            self.tabs_and_spacing_widget.setVisible(True)

    def _library_path_editing_finished_line_edit(self) -> None:
        library_path = self.library_path_line_edit.text()
        library_path = hou.text.expandString(library_path)

        if library_path:
            if not os.path.exists(library_path):
                logger.error(f"Library path {library_path!r} does not exist.")

    def _select_library_path_clicked_push_button(self) -> None:
        library_path = hou.ui.selectFile(
            file_type=hou.fileType.Directory, title="Select Folder"
        )
        library_path = hou.text.expandString(library_path)

        if library_path:
            self.library_path_line_edit.setText(library_path)

    def _font_size_value_changed_spin_box(self) -> None:
        self.font_size_slider.blockSignals(True)
        self.font_size_slider.setValue(self.font_size_spin_box.value())
        self.font_size_slider.blockSignals(False)

    def _font_size_value_changed_slider(self) -> None:
        self.font_size_spin_box.blockSignals(True)
        self.font_size_spin_box.setValue(self.font_size_slider.value())
        self.font_size_spin_box.blockSignals(False)

    def _revert_to_default_clicked_push_button(self) -> None:
        self.font_combo_box.setCurrentText("Source Sans Pro")
        self.font_size_spin_box.setValue(8)

        for color_scheme in ColorScheme:
            color_scheme = color_scheme.value

            self.color_scheme[color_scheme["name"]] = color_scheme["color"]

        self._add_color_scheme_items()

    def _tab_size_value_changed_spin_box(self) -> None:
        self.tab_size_slider.blockSignals(True)
        self.tab_size_slider.setValue(self.tab_size_spin_box.value())
        self.tab_size_slider.blockSignals(False)

    def _tab_size_value_changed_slider(self) -> None:
        self.tab_size_spin_box.blockSignals(True)
        self.tab_size_spin_box.setValue(self.tab_size_slider.value())
        self.tab_size_spin_box.blockSignals(False)

    def _color_scheme_item_clicked_list_widget(
        self, item: QtWidgets.QListWidgetItem
    ) -> None:

        if item:
            color = QtWidgets.QColorDialog.getColor()

            if color:
                color = color.getRgb()

                pixmap = QtGui.QPixmap(50, 50)
                pixmap.fill(QtGui.QColor(*color))

                icon = QtGui.QIcon(pixmap)

                item.setIcon(icon)

                item_data = item.data(QtCore.Qt.UserRole)

                self.color_scheme[item_data] = color

    def _apply_clicked_push_button(self) -> None:
        self._save_preferences()

        self.on_save_clicked.emit()

    def _accept_clicked_push_button(self) -> None:
        self._save_preferences()
        self.close()

        self.on_save_clicked.emit()

    def _add_color_scheme_items(self) -> None:
        self.color_scheme_list_widget.clear()

        for color_scheme in ColorScheme:
            color_scheme = color_scheme.value
            color = self.color_scheme[color_scheme["name"]]

            pixmap = QtGui.QPixmap(50, 50)
            pixmap.fill(QtGui.QColor(*color))

            icon = QtGui.QIcon(pixmap)

            item = QtWidgets.QListWidgetItem()
            item.setText(color_scheme["name"].capitalize())
            item.setData(QtCore.Qt.UserRole, color_scheme["name"])
            item.setIcon(icon)
            self.color_scheme_list_widget.addItem(item)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        self._load_preferences()
        self._add_color_scheme_items()
