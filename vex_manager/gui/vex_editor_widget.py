from PySide2 import QtWidgets
from PySide2 import QtCore

import logging
import os

from vex_manager.gui.vex_plain_text_edit import VEXPlainTextEdit


logger = logging.getLogger(f'vex_manager.{__name__}')


class VEXEditorWidget(QtWidgets.QDialog):
    create_wrangle_node_clicked = QtCore.Signal()
    insert_code_clicked = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()

        self.file_path = ''
        self.wrangle_node_type = ''

        self._create_widgets()
        self._create_layouts()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.name_line_edit = QtWidgets.QLineEdit()
        self.name_line_edit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.name_line_edit.setReadOnly(True)

        self.vex_code_plain_text_edit = VEXPlainTextEdit()

        self.save_changed_push_button = QtWidgets.QPushButton('Save Changes')

        self.create_wrangle_node_push_button = QtWidgets.QPushButton('Create Wrangle Node')

        self.insert_code_push_button = QtWidgets.QPushButton('Insert Code')

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.name_line_edit)
        main_layout.addWidget(self.vex_code_plain_text_edit)
        main_layout.addWidget(self.save_changed_push_button)
        main_layout.setContentsMargins(QtCore.QMargins())
        main_layout.setSpacing(3)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.create_wrangle_node_push_button)
        layout.addWidget(self.insert_code_push_button)
        main_layout.addLayout(layout)

    def _create_connections(self) -> None:
        self.save_changed_push_button.clicked.connect(self._save_changed_clicked_push_button)
        self.create_wrangle_node_push_button.clicked.connect(self._create_wrangle_node_clicked_push_button)
        self.insert_code_push_button.clicked.connect(self._insert_code_clicked_push_button)

    def _save_changed_clicked_push_button(self) -> None:
        if self.file_path:
            with open(self.file_path, 'w') as file_to_write:
                content = self.vex_code_plain_text_edit.toPlainText()
                file_to_write.write(content)

            logger.debug(f'{self.file_path!r} saved.')
        else:
            logger.warning(f'No file selected.')

    def _create_wrangle_node_clicked_push_button(self) -> None:
        self.create_wrangle_node_clicked.emit()

    def _insert_code_clicked_push_button(self) -> None:
        self.insert_code_clicked.emit()

    def set_file_name(self, file_name: str) -> None:
        self.name_line_edit.setText(file_name.replace('\\', '/'))

    def set_file_path(self, file_path: str) -> None:
        self.file_path = file_path

        if os.path.exists(self.file_path):
            with open(self.file_path) as file_for_read:
                self.vex_code_plain_text_edit.setPlainText(file_for_read.read())
        else:
            self.vex_code_plain_text_edit.setPlainText('')

    def set_wrangle_node_type(self, wrangle_node_type: str) -> None:
        self.wrangle_node_type = wrangle_node_type
