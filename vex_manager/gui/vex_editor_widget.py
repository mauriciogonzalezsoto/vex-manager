from PySide2 import QtWidgets
from PySide2 import QtCore

from pathlib import Path
import logging
import os

from vex_manager.gui.vex_plain_text_edit import VEXPlainTextEdit
import vex_manager.utils as utils
import vex_manager.core as core


logger = logging.getLogger(f'vex_manager.{__name__}')


class VEXEditorWidget(QtWidgets.QWidget):
    name_editing_finished = QtCore.Signal(str)
    save_clicked = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()

        self.file_path = ''
        self.base_name = ''
        self.library_path = ''
        self.wrangle_node_type = ''

        self._create_widgets()
        self._create_layouts()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.name_line_edit = QtWidgets.QLineEdit()

        self.vex_plain_text_editor = VEXPlainTextEdit()

        self.save_changed_push_button = QtWidgets.QPushButton('Save Changes')

        self.replace_code_push_button = QtWidgets.QPushButton('Replace Code')

        self.insert_code_push_button = QtWidgets.QPushButton('Insert Code')

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.name_line_edit)
        main_layout.addWidget(self.vex_plain_text_editor)
        main_layout.addWidget(self.save_changed_push_button)
        main_layout.setContentsMargins(QtCore.QMargins())
        main_layout.setSpacing(3)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.replace_code_push_button)
        layout.addWidget(self.insert_code_push_button)
        main_layout.addLayout(layout)

    def _create_connections(self) -> None:
        self.name_line_edit.editingFinished.connect(self._name_editing_finished_line_edit)
        self.save_changed_push_button.clicked.connect(self._save_changed_clicked_push_button)
        self.replace_code_push_button.clicked.connect(self._replace_code_clicked_push_button)
        self.insert_code_push_button.clicked.connect(self._insert_code_clicked_push_button)

    def _name_editing_finished_line_edit(self) -> None:
        name = self.name_line_edit.text()

        if utils.is_valid_file_name(name):
            if os.path.exists(self.library_path):
                self.name_editing_finished.emit(name)
        else:
            logger.error(f'Invalid file name {name!r}')

    def _save_changed_clicked_push_button(self) -> None:
        if self.file_path:
            self._save_file()
        else:
            if os.path.exists(self.library_path):
                folder_path = os.path.join(self.library_path, self.wrangle_node_type)
                name = self.name_line_edit.text()

                if not utils.is_valid_file_name(name):
                    name = ''

                self.file_path, self.base_name = core.create_new_vex_file(folder_path=folder_path, name=name)

                self._save_file()

                self.save_clicked.emit()
            else:
                logger.error(f'Library path {self.library_path} does not exist')

    def _replace_code_clicked_push_button(self) -> None:
        core.set_vex_code_in_selected_wrangle_node(vex_code=self.vex_plain_text_editor.toPlainText())

    def _insert_code_clicked_push_button(self) -> None:
        core.set_vex_code_in_selected_wrangle_node(vex_code=self.vex_plain_text_editor.toPlainText(), insert=True)

    def _save_file(self) -> None:
        with open(self.file_path, 'w') as file_to_write:
            content = self.vex_plain_text_editor.toPlainText()
            file_to_write.write(content)

        self.name_line_edit.setText(self.base_name)

        logger.debug(f'{self.file_path!r} saved.')

    def display_code(self) -> None:
        if os.path.exists(self.file_path):
            with open(self.file_path) as file_for_read:
                self.vex_plain_text_editor.setPlainText(file_for_read.read())
        else:
            self.vex_plain_text_editor.setPlainText('')

    def get_current_file_path(self) -> str:
        return self.file_path

    def set_file_path(self, file_path: str) -> None:
        self.file_path = file_path

        if os.path.exists(file_path):
            self.base_name = Path(self.file_path).stem
            self.name_line_edit.setText(self.base_name)
        else:
            self.name_line_edit.setText('')

    def set_library_path(self, library_path: str) -> None:
        self.library_path = library_path

    def set_wrangle_node_type(self, wrangle_node_type: str) -> None:
        self.wrangle_node_type = wrangle_node_type
