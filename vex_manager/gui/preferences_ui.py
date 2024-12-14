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
    TAB_AND_SPACING = 'Tab and Spacing'
    DELIMITERS = 'Delimiters'

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)

        self.preferences_path = utils.get_preferences_path()

        self.resize(400, 200)
        self.setObjectName(PreferencesUI.WINDOW_NAME)
        self.setWindowTitle(PreferencesUI.WINDOW_TITLE)
        self.setModal(True)

        self._create_widgets()
        self._create_layouts()
        self._create_connections()
        self._load_preferences()

    def _create_widgets(self) -> None:
        self.preferences_categories_combo_box = QtWidgets.QComboBox(self)
        self.preferences_categories_combo_box.addItems([
            PreferencesUI.GENERAL,
            PreferencesUI.TAB_AND_SPACING,
            PreferencesUI.DELIMITERS
        ])

        self.auto_save_on_changes_check_box = QtWidgets.QCheckBox('Auto-save on Changes')

        self.display_dialog_when_deleting_a_file_check_box = QtWidgets.QCheckBox(
            'Display Confirmation Dialog when Deleting a File')

        self.backspace_on_tab_stop_check_box = QtWidgets.QCheckBox('Backspace on Tab Stop')

        self.auto_indent_check_box = QtWidgets.QCheckBox('Auto-indent')

        self.tab_size_spin_box = QtWidgets.QSpinBox()
        self.tab_size_spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.tab_size_spin_box.setRange(1, 12)

        self.insert_matching_delimiter_check_box = QtWidgets.QCheckBox('Insert Matching Delimiter')

        self.apply_push_button = QtWidgets.QPushButton('Apply')

        self.accept_push_button = QtWidgets.QPushButton('Accept')

        self.cancel_push_button = QtWidgets.QPushButton('Cancel')

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.preferences_categories_combo_box)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setContentsMargins(QtCore.QMargins(6, 3, 6, 6))
        main_layout.setSpacing(3)

        self.general_group_box = QtWidgets.QGroupBox()
        main_layout.addWidget(self.general_group_box)

        general_form_layout = QtWidgets.QFormLayout()
        general_form_layout.addWidget(self.auto_save_on_changes_check_box)
        general_form_layout.addWidget(self.display_dialog_when_deleting_a_file_check_box)
        general_form_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        general_form_layout.setSpacing(3)
        self.general_group_box.setLayout(general_form_layout)

        self.tab_and_spacing_group_box = QtWidgets.QGroupBox()
        self.tab_and_spacing_group_box.setVisible(False)
        main_layout.addWidget(self.tab_and_spacing_group_box)

        tab_and_spacing_form_layout = QtWidgets.QFormLayout()
        tab_and_spacing_form_layout.addWidget(self.backspace_on_tab_stop_check_box)
        tab_and_spacing_form_layout.addWidget(self.auto_indent_check_box)
        tab_and_spacing_form_layout.addRow('Tab Size ', self.tab_size_spin_box)
        tab_and_spacing_form_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        tab_and_spacing_form_layout.setSpacing(3)
        self.tab_and_spacing_group_box.setLayout(tab_and_spacing_form_layout)

        self.delimiters_group_box = QtWidgets.QGroupBox()
        self.delimiters_group_box.setVisible(False)
        main_layout.addWidget(self.delimiters_group_box)
        
        delimiters_form_layout = QtWidgets.QFormLayout()
        delimiters_form_layout.addWidget(self.insert_matching_delimiter_check_box)
        delimiters_form_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        delimiters_form_layout.setSpacing(3)
        self.delimiters_group_box.setLayout(delimiters_form_layout)

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

        self.auto_save_on_changes_check_box.setChecked(settings.get('auto_save_on_changes', True))
        self.display_dialog_when_deleting_a_file_check_box.setChecked(
            settings.get('display_dialog_when_deleting_a_file', True))

        self.backspace_on_tab_stop_check_box.setChecked(settings.get('backspace_on_tab_stop', True))
        self.auto_indent_check_box.setChecked(settings.get('auto_indent', True))
        self.tab_size_spin_box.setValue(settings.get('tab_size', 4))

        self.insert_matching_delimiter_check_box.setChecked(settings.get('insert_matching_delimiter', True))

    def _save_preferences(self) -> None:
        settings = {
            'auto_save_on_changes': self.auto_save_on_changes_check_box.isChecked(),
            'display_dialog_when_deleting_a_file': self.display_dialog_when_deleting_a_file_check_box.isChecked(),
            'backspace_on_tab_stop': self.backspace_on_tab_stop_check_box.isChecked(),
            'auto_indent': self.auto_indent_check_box.isChecked(),
            'tab_size': self.tab_size_spin_box.value(),
            'insert_matching_delimiter': self.insert_matching_delimiter_check_box.isChecked()
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
        self.tab_and_spacing_group_box.setVisible(False)
        self.delimiters_group_box.setVisible(False)

        current_preferences_category = self.preferences_categories_combo_box.currentText()

        if current_preferences_category == PreferencesUI.GENERAL:
            self.general_group_box.setVisible(True)
        elif current_preferences_category == PreferencesUI.TAB_AND_SPACING:
            self.tab_and_spacing_group_box.setVisible(True)
        elif current_preferences_category == PreferencesUI.DELIMITERS:
            self.delimiters_group_box.setVisible(True)
