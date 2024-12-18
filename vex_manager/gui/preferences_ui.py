from PySide2 import QtWidgets
from PySide2 import QtCore

import logging
import json
import os

import vex_manager.utils as utils


logger = logging.getLogger(f'vex_manager.{__name__}')


class PreferencesUI(QtWidgets.QDialog):
    WINDOW_NAME = 'vexManagerPreferences'
    WINDOW_TITLE = 'Preferences'

    GENERAL = 'General'
    CODE_EDITOR = 'Code Editor'
    TABS_AND_SPACING = 'Tabs and Spacing'

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.preferences_path = utils.get_preferences_path()

        self.resize(400, 200)
        self.setModal(True)
        self.setObjectName(PreferencesUI.WINDOW_NAME)
        self.setWindowTitle(PreferencesUI.WINDOW_TITLE)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self._create_widgets()
        self._create_layouts()
        self._create_connections()
        self._load_preferences()

    def _create_widgets(self) -> None:
        self.preferences_categories_combo_box = QtWidgets.QComboBox()
        self.preferences_categories_combo_box.addItems([
            PreferencesUI.GENERAL,
            PreferencesUI.CODE_EDITOR,
            PreferencesUI.TABS_AND_SPACING
        ])

        self.display_dialog_when_deleting_a_file_check_box = QtWidgets.QCheckBox(
            'Display Confirmation Dialog when Deleting a File')

        self.auto_indent_check_box = QtWidgets.QCheckBox('Auto-indent')

        self.insert_closing_brackets_check_box = QtWidgets.QCheckBox('Insert Closing Brackets')

        self.insert_closing_quotes_check_box = QtWidgets.QCheckBox('Insert Closing Quotes')

        self.backspace_on_tab_stop_check_box = QtWidgets.QCheckBox('Backspace on Tab Stop')

        self.tab_size_spin_box = QtWidgets.QSpinBox()
        self.tab_size_spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.tab_size_spin_box.setRange(1, 12)

        self.apply_push_button = QtWidgets.QPushButton('Apply')

        self.accept_push_button = QtWidgets.QPushButton('Accept')

        self.cancel_push_button = QtWidgets.QPushButton('Cancel')

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setContentsMargins(QtCore.QMargins(6, 6, 6, 6))
        main_layout.setSpacing(6)

        preferences_categories_h_box_layout = QtWidgets.QHBoxLayout()
        preferences_categories_h_box_layout.addWidget(self.preferences_categories_combo_box)
        preferences_categories_h_box_layout.addStretch()
        preferences_categories_h_box_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        main_layout.addLayout(preferences_categories_h_box_layout)

        self.general_group_box = QtWidgets.QGroupBox()
        main_layout.addWidget(self.general_group_box)

        general_form_layout = QtWidgets.QFormLayout()
        general_form_layout.addWidget(self.display_dialog_when_deleting_a_file_check_box)
        general_form_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        general_form_layout.setSpacing(3)
        self.general_group_box.setLayout(general_form_layout)

        self.code_editor_group_box = QtWidgets.QGroupBox()
        self.code_editor_group_box.setVisible(False)
        main_layout.addWidget(self.code_editor_group_box)

        code_editor_form_layout = QtWidgets.QFormLayout()
        code_editor_form_layout.addWidget(self.auto_indent_check_box)
        code_editor_form_layout.addWidget(self.insert_closing_brackets_check_box)
        code_editor_form_layout.addWidget(self.insert_closing_quotes_check_box)
        code_editor_form_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        code_editor_form_layout.setSpacing(3)
        self.code_editor_group_box.setLayout(code_editor_form_layout)

        self.tabs_and_spacing_group_box = QtWidgets.QGroupBox()
        self.tabs_and_spacing_group_box.setVisible(False)
        main_layout.addWidget(self.tabs_and_spacing_group_box)

        tab_and_spacing_form_layout = QtWidgets.QFormLayout()
        tab_and_spacing_form_layout.addWidget(self.backspace_on_tab_stop_check_box)
        tab_and_spacing_form_layout.addRow('Tab Size ', self.tab_size_spin_box)
        tab_and_spacing_form_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        tab_and_spacing_form_layout.setSpacing(3)
        self.tabs_and_spacing_group_box.setLayout(tab_and_spacing_form_layout)

        buttons_h_box_layout = QtWidgets.QHBoxLayout()
        buttons_h_box_layout.addWidget(self.apply_push_button)
        buttons_h_box_layout.addStretch()
        buttons_h_box_layout.addWidget(self.accept_push_button)
        buttons_h_box_layout.addWidget(self.cancel_push_button)
        main_layout.addStretch()
        main_layout.addLayout(buttons_h_box_layout)

    def _create_connections(self) -> None:
        self.preferences_categories_combo_box.currentTextChanged.connect(
            self._preferences_categories_current_text_changed_combo_box)

        self.apply_push_button.clicked.connect(self._apply_clicked_push_button)
        self.accept_push_button.clicked.connect(self._accept_clicked_push_button)
        self.cancel_push_button.clicked.connect(self.close)

    def _load_preferences(self) -> None:
        settings = {}

        if os.path.exists(self.preferences_path):
            with open(self.preferences_path, 'r') as file_for_read:
                settings = json.load(file_for_read)

        self.display_dialog_when_deleting_a_file_check_box.setChecked(
            settings.get('display_dialog_when_deleting_a_file', True))

        self.auto_indent_check_box.setChecked(settings.get('auto_indent', True))
        self.insert_closing_brackets_check_box.setChecked(settings.get('insert_closing_brackets', True))
        self.insert_closing_quotes_check_box.setChecked(settings.get('insert_closing_quotes', True))

        self.backspace_on_tab_stop_check_box.setChecked(settings.get('backspace_on_tab_stop', True))
        self.tab_size_spin_box.setValue(settings.get('tab_size', 4))

    def _save_preferences(self) -> None:
        settings = {
            'display_dialog_when_deleting_a_file': self.display_dialog_when_deleting_a_file_check_box.isChecked(),

            'auto_indent': self.auto_indent_check_box.isChecked(),
            'insert_closing_brackets': self.insert_closing_brackets_check_box.isChecked(),
            'insert_closing_quotes': self.insert_closing_quotes_check_box.isChecked(),

            'backspace_on_tab_stop': self.backspace_on_tab_stop_check_box.isChecked(),
            'tab_size': self.tab_size_spin_box.value(),
        }

        if self.preferences_path:
            with open(self.preferences_path, 'w') as file_for_write:
                json.dump(settings, file_for_write, indent=4)
        else:
            logger.error(f'Preferences path is empty.')

    def _apply_clicked_push_button(self) -> None:
        self._save_preferences()

    def _accept_clicked_push_button(self) -> None:
        self._save_preferences()
        self.close()

    def _preferences_categories_current_text_changed_combo_box(self) -> None:
        self.general_group_box.setVisible(False)
        self.code_editor_group_box.setVisible(False)
        self.tabs_and_spacing_group_box.setVisible(False)

        current_preferences_category = self.preferences_categories_combo_box.currentText()

        if current_preferences_category == PreferencesUI.GENERAL:
            self.general_group_box.setVisible(True)
        elif current_preferences_category == PreferencesUI.CODE_EDITOR:
            self.code_editor_group_box.setVisible(True)
        elif current_preferences_category == PreferencesUI.TABS_AND_SPACING:
            self.tabs_and_spacing_group_box.setVisible(True)
