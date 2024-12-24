from PySide2 import QtWidgets
from PySide2 import QtCore

import hou

import logging
import json
import os

import vex_manager.utils as utils

logger = logging.getLogger(f'vex_manager.{__name__}')


class PreferencesUI(QtWidgets.QWidget):
    WINDOW_NAME = 'vexManagerPreferences'
    WINDOW_TITLE = 'Preferences'

    GENERAL = 'General'
    CODE_EDITOR = 'Code Editor'
    TABS_AND_SPACING = 'Tabs and Spacing'
    WARNING_DIALOGS = 'Warning Dialogs'

    on_save_clicked = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget, f: QtCore.Qt.WindowFlags) -> None:
        super().__init__(parent, f)

        self.preferences_path = utils.get_preferences_path()

        self.resize(400, 200)
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
            PreferencesUI.TABS_AND_SPACING,
            PreferencesUI.WARNING_DIALOGS
        ])

        self.library_path_line_edit = QtWidgets.QLineEdit()

        push_button_size = self.library_path_line_edit.sizeHint().height()

        self.select_library_path_push_button = QtWidgets.QPushButton('...')
        self.select_library_path_push_button.setFixedSize(QtCore.QSize(push_button_size, push_button_size))

        self.auto_indent_check_box = QtWidgets.QCheckBox('Auto-indent')

        self.insert_closing_brackets_check_box = QtWidgets.QCheckBox('Insert Closing Brackets')

        self.insert_closing_quotes_check_box = QtWidgets.QCheckBox('Insert Closing Quotes')

        self.backspace_on_tab_stop_check_box = QtWidgets.QCheckBox('Backspace on Tab Stop')

        self.tab_size_spin_box = QtWidgets.QSpinBox()
        self.tab_size_spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.tab_size_spin_box.setFixedWidth(75)
        self.tab_size_spin_box.setRange(1, 12)

        self.tab_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.tab_size_slider.setRange(1, 12)
        self.tab_size_slider.setSingleStep(1)

        self.warm_before_deleting_a_file_check_box = QtWidgets.QCheckBox('Warm Before Deleting a File')

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

        self.general_widget = QtWidgets.QWidget()
        main_layout.addWidget(self.general_widget)

        library_path_h_box_layout = QtWidgets.QHBoxLayout()
        library_path_h_box_layout.addWidget(self.library_path_line_edit)
        library_path_h_box_layout.addWidget(self.select_library_path_push_button)

        general_form_layout = QtWidgets.QFormLayout()
        general_form_layout.addRow('Library Path ', library_path_h_box_layout)
        general_form_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        general_form_layout.setSpacing(3)
        self.general_widget.setLayout(general_form_layout)

        self.code_editor_widget = QtWidgets.QWidget()
        self.code_editor_widget.setVisible(False)
        main_layout.addWidget(self.code_editor_widget)

        code_editor_form_layout = QtWidgets.QFormLayout()
        code_editor_form_layout.addWidget(self.auto_indent_check_box)
        code_editor_form_layout.addWidget(self.insert_closing_brackets_check_box)
        code_editor_form_layout.addWidget(self.insert_closing_quotes_check_box)
        general_form_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        general_form_layout.setSpacing(3)
        self.code_editor_widget.setLayout(code_editor_form_layout)

        self.tabs_and_spacing_widget = QtWidgets.QWidget()
        self.tabs_and_spacing_widget.setVisible(False)
        main_layout.addWidget(self.tabs_and_spacing_widget)

        tab_and_spacing_v_box_layout = QtWidgets.QVBoxLayout()
        tab_and_spacing_v_box_layout.addWidget(self.backspace_on_tab_stop_check_box)
        tab_and_spacing_v_box_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        tab_and_spacing_v_box_layout.setSpacing(15)
        self.tabs_and_spacing_widget.setLayout(tab_and_spacing_v_box_layout)

        tab_size_h_box_layout = QtWidgets.QHBoxLayout()
        tab_size_h_box_layout.addWidget(self.tab_size_spin_box)
        tab_size_h_box_layout.addWidget(self.tab_size_slider)

        tab_and_spacing_form_layout = QtWidgets.QFormLayout()
        tab_and_spacing_form_layout.addRow('Tab Size ', tab_size_h_box_layout)
        tab_and_spacing_form_layout.setSpacing(3)
        tab_and_spacing_v_box_layout.addLayout(tab_and_spacing_form_layout)

        self.warning_dialog_widget = QtWidgets.QWidget()
        self.warning_dialog_widget.setVisible(False)
        main_layout.addWidget(self.warning_dialog_widget)

        warning_dialogs_form_layout = QtWidgets.QFormLayout()
        warning_dialogs_form_layout.addWidget(self.warm_before_deleting_a_file_check_box)
        warning_dialogs_form_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
        warning_dialogs_form_layout.setSpacing(3)
        self.warning_dialog_widget.setLayout(warning_dialogs_form_layout)

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

        self.library_path_line_edit.editingFinished.connect(self._library_path_editing_finished_line_edit)
        self.select_library_path_push_button.clicked.connect(self._select_library_path_clicked_push_button)

        self.tab_size_spin_box.valueChanged.connect(self._tab_size_value_changed_spin_box)
        self.tab_size_slider.valueChanged.connect(self._tab_size_value_changed_slider)

        self.apply_push_button.clicked.connect(self._apply_clicked_push_button)
        self.accept_push_button.clicked.connect(self._accept_clicked_push_button)
        self.cancel_push_button.clicked.connect(self.close)

    def _load_preferences(self) -> None:
        settings = {}

        if os.path.exists(self.preferences_path):
            with open(self.preferences_path, 'r') as file_for_read:
                settings = json.load(file_for_read)

        self.library_path_line_edit.setText(settings.get('library_path', ''))

        self.auto_indent_check_box.setChecked(settings.get('auto_indent', True))
        self.insert_closing_brackets_check_box.setChecked(settings.get('insert_closing_brackets', True))
        self.insert_closing_quotes_check_box.setChecked(settings.get('insert_closing_quotes', True))

        self.backspace_on_tab_stop_check_box.setChecked(settings.get('backspace_on_tab_stop', True))
        self.tab_size_spin_box.setValue(settings.get('tab_size', 4))

        self.warm_before_deleting_a_file_check_box.setChecked(settings.get('warm_before_deleting_a_file', True))

    def _save_preferences(self) -> None:
        settings = {
            'library_path': self.library_path_line_edit.text(),

            'auto_indent': self.auto_indent_check_box.isChecked(),
            'insert_closing_brackets': self.insert_closing_brackets_check_box.isChecked(),
            'insert_closing_quotes': self.insert_closing_quotes_check_box.isChecked(),

            'backspace_on_tab_stop': self.backspace_on_tab_stop_check_box.isChecked(),
            'tab_size': self.tab_size_spin_box.value(),

            'warm_before_deleting_a_file': self.warm_before_deleting_a_file_check_box.isChecked()
        }

        if self.preferences_path:
            with open(self.preferences_path, 'w') as file_for_write:
                json.dump(settings, file_for_write, indent=4)
        else:
            logger.error(f'No preferences path.')

    def _library_path_editing_finished_line_edit(self) -> None:
        library_path = self.library_path_line_edit.text()
        library_path = hou.text.expandString(library_path)

        if library_path:
            if not os.path.exists(library_path):
                logger.error(f'Library path {library_path!r} does not exist.')

    def _select_library_path_clicked_push_button(self) -> None:
        library_path = hou.ui.selectFile(file_type=hou.fileType.Directory, title='Select Folder')
        library_path = hou.text.expandString(library_path)

        if library_path:
            self.library_path_line_edit.setText(library_path)

    def _tab_size_value_changed_spin_box(self):
        self.tab_size_slider.blockSignals(True)
        self.tab_size_slider.setValue(self.tab_size_spin_box.value())
        self.tab_size_slider.blockSignals(False)

    def _tab_size_value_changed_slider(self):
        self.tab_size_spin_box.blockSignals(True)
        self.tab_size_spin_box.setValue(self.tab_size_slider.value())
        self.tab_size_spin_box.blockSignals(False)

    def _apply_clicked_push_button(self) -> None:
        self._save_preferences()

        self.on_save_clicked.emit()

    def _accept_clicked_push_button(self) -> None:
        self._save_preferences()
        self.close()

        self.on_save_clicked.emit()

    def _preferences_categories_current_text_changed_combo_box(self) -> None:
        self.general_widget.setVisible(False)
        self.code_editor_widget.setVisible(False)
        self.tabs_and_spacing_widget.setVisible(False)
        self.warning_dialog_widget.setVisible(False)

        current_preferences_category = self.preferences_categories_combo_box.currentText()

        if current_preferences_category == PreferencesUI.GENERAL:
            self.general_widget.setVisible(True)
        elif current_preferences_category == PreferencesUI.CODE_EDITOR:
            self.code_editor_widget.setVisible(True)
        elif current_preferences_category == PreferencesUI.TABS_AND_SPACING:
            self.tabs_and_spacing_widget.setVisible(True)
        elif current_preferences_category == PreferencesUI.WARNING_DIALOGS:
            self.warning_dialog_widget.setVisible(True)
