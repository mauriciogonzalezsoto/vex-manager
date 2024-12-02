from PySide2 import QtWidgets
from PySide2 import QtCore

import logging
import os
import re


logger = logging.getLogger(f'vex_manager.{__name__}')


class FileExplorerTreeWidget(QtWidgets.QTreeWidget):

    def __init__(self) -> None:
        super(FileExplorerTreeWidget, self).__init__()

        self.setHeaderHidden(True)

        self._create_connections()

    def _create_connections(self) -> None:
        self.itemDoubleClicked.connect(self.editItem)

    @staticmethod
    def _is_valid_file_name(file_name: str) -> bool:
        pattern = r'^[A-Za-z_][A-Za-z0-9_]*\.'
        match = re.match(pattern, file_name)

        return bool(match)

    def _rename_item(self, item: QtWidgets.QTreeWidgetItem, column: int, line_edit: QtWidgets.QLineEdit) -> None:
        new_file_name = line_edit.text()

        file_name = item.text(0)
        file_path = item.data(0, QtCore.Qt.UserRole)

        if os.path.isfile(file_path):
            if not self._is_valid_file_name(new_file_name):
                logger.error(f'\'{new_file_name}\' is not a valid file name.')
            elif not new_file_name.endswith('.vex'):
                logger.error('The file name must have the extension \'.vex\'')
            else:
                dir_name = os.path.dirname(file_path)
                new_file_path = os.path.join(dir_name, new_file_name)

                item.setText(column, new_file_name)
                item.setData(column, QtCore.Qt.UserRole, new_file_path)

                if os.path.normpath(file_path) != os.path.normpath(new_file_path):
                    os.rename(file_path, new_file_path)

                    logger.debug(f'Renamed file {file_path} -> {new_file_path}')

            self.removeItemWidget(item, column)

    def editItem(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
        line_edit = QtWidgets.QLineEdit(self)
        line_edit.setText(item.text(column))

        self.setItemWidget(item, column, line_edit)

        line_edit.editingFinished.connect(lambda: self._rename_item(item, column, line_edit))
