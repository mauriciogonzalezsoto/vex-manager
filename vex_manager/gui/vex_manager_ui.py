from PySide2 import QtWidgets
from PySide2 import QtCore

import hou

import logging
import os

import vex_manager.core.vex_manager as create_wrangle_node
from vex_manager.gui.file_explorer_widget import FileExplorerWidget
from vex_manager.gui.vex_editor_widget import VEXEditorWidget
from vex_manager.config import WrangleNodes


logger = logging.getLogger(f'vex_manager.{__name__}')


class VEXManagerUI(QtWidgets.QWidget):
    WINDOW_NAME = 'vexManager'
    WINDOW_TITLE = 'VEX Manager'

    def __init__(self) -> None:
        super(VEXManagerUI, self).__init__()

        self.current_vex_file_path = ''

        self.resize(800, 600)
        self.setObjectName(VEXManagerUI.WINDOW_NAME)
        self.setWindowTitle(VEXManagerUI.WINDOW_TITLE)

        self._create_widgets()
        self._create_layouts()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.library_path_line_edit = QtWidgets.QLineEdit()
        self.library_path_line_edit.setPlaceholderText('Library path...')

        push_button_size = self.library_path_line_edit.sizeHint().height()

        self.select_library_path_push_button = QtWidgets.QPushButton('...')
        self.select_library_path_push_button.setFixedSize(QtCore.QSize(push_button_size, push_button_size))

        self.context_explorer_widget = FileExplorerWidget()

        self.vex_editor_widget = VEXEditorWidget()

    def _create_layouts(self) -> None:
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(QtCore.QMargins(3, 3, 3, 3))
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
        left_layout.addWidget(self.context_explorer_widget)
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
        self.library_path_line_edit.returnPressed.connect(self._library_path_return_pressed_line_edit)
        self.select_library_path_push_button.clicked.connect(self._select_library_path_clicked__push_button)

        self.context_explorer_widget.current_item_changed.connect(self._context_explorer_current_item_changed_widget)

        self.vex_editor_widget.create_wrangle_node_clicked.connect(self._vex_editor_create_wrangle_node_clicked_widget)
        self.vex_editor_widget.insert_code_clicked.connect(self._vex_editor_insert_code_clicked_widget)

    def _library_path_return_pressed_line_edit(self) -> None:
        text = self.library_path_line_edit.text()

        if os.path.exists(text):
            self.context_explorer_widget.set_library_path(text)

            logger.info(f'Library path set to \'{text}\'')
        else:
            logger.error(f'\'{text}\' path does not exist.')

    def _select_library_path_clicked__push_button(self) -> None:
        # library_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')

        library_path = hou.ui.selectFile(file_type=hou.fileType.Directory, title='Select Folder')

        if library_path:
            self.library_path_line_edit.setText(library_path)

            self.context_explorer_widget.set_library_path(library_path)

    def _context_explorer_current_item_changed_widget(self, file_path: str) -> None:
        self.current_vex_file_path = file_path

        wrangle_node_type = self.context_explorer_widget.get_current_wrangle_node_type()
        file_base_name = os.path.basename(self.current_vex_file_path)
        file_base_name = file_base_name.removesuffix('.vex')

        self.vex_editor_widget.set_file_name(file_base_name)
        self.vex_editor_widget.set_file_path(self.current_vex_file_path)
        self.vex_editor_widget.set_wrangle_node_type(wrangle_node_type)

    def _vex_editor_create_wrangle_node_clicked_widget(self) -> None:
        current_wrangle_node_type = self.context_explorer_widget.get_current_wrangle_node_type()

        wrangle_node = create_wrangle_node.create_wrangle_node(wrangle_type=current_wrangle_node_type)

        if wrangle_node:
            create_wrangle_node.insert_vex_code(node=wrangle_node, vex_file_path=self.current_vex_file_path)

    def _vex_editor_insert_code_clicked_widget(self) -> None:
        selected_nodes = hou.selectedNodes()

        if selected_nodes:
            selected_node = selected_nodes[-1]

            create_wrangle_node.insert_vex_code(node=selected_node, vex_file_path=self.current_vex_file_path)
        else:
            logger.warning('There is no node selected.')

    def showEvent(self, e: any) -> None:
        super(VEXManagerUI, self).showEvent(e)

        selected_nodes = hou.selectedNodes()

        if selected_nodes:
            selected_node = selected_nodes[-1]

            for wrangle_node in WrangleNodes:
                wrangle_node_name, wrangle_node_type = wrangle_node.value
                if selected_node.type().name() == wrangle_node_type:
                    self.context_explorer_widget.set_current_wrangle_node(
                        wrangle_node_name=wrangle_node_name,
                        wrangle_node_type=wrangle_node_type)

                    break
