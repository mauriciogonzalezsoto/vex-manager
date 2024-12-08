from PySide2 import QtWidgets
from PySide2 import QtCore

import logging
import os
import re


logger = logging.getLogger(f'vex_manager.{__name__}')


class FileExplorerTreeWidget(QtWidgets.QTreeWidget):
    item_renamed = QtCore.Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.setHeaderHidden(True)

        self._create_connections()

    def _create_connections(self) -> None:
        self.itemDoubleClicked.connect(self.editItem)

    @staticmethod
    def _is_valid_file_name(file_name: str) -> bool:
        pattern = r'^[A-Za-z_][A-Za-z0-9_]*$'
        match = re.match(pattern, file_name)

        return bool(match)

    def get_top_level_items(self) -> list[QtWidgets.QTreeWidgetItem]:
        top_level_items = []

        for i in range(self.topLevelItemCount()):
            top_level_items.append(self.topLevelItem(i))

        return top_level_items

    def _rename_item(self, column: int, item: QtWidgets.QTreeWidgetItem, line_edit: QtWidgets.QLineEdit) -> None:
        file_path = item.data(0, QtCore.Qt.UserRole)
        new_file_name = line_edit.text()

        if os.path.isfile(file_path):
            if new_file_name in [item.text(0) for item in self.get_top_level_items()]:
                logger.error(f'File {new_file_name!r} already exists.')
            elif not self._is_valid_file_name(new_file_name):
                logger.error(f'{new_file_name!r} is not a valid file name.')
            else:
                dir_name = os.path.dirname(file_path)
                new_file_path = os.path.join(dir_name, f'{new_file_name}.vex')

                item.setText(column, new_file_name)
                item.setData(column, QtCore.Qt.UserRole, new_file_path)

                if os.path.normpath(file_path) != os.path.normpath(new_file_path):
                    os.rename(file_path, new_file_path)

                    self.item_renamed.emit(new_file_name)

                    logger.debug(f'Renamed file {file_path!r} -> {new_file_path!r}')

            self.removeItemWidget(item, column)

    def editItem(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
        line_edit = QtWidgets.QLineEdit(self)
        line_edit.setText(item.text(column))

        self.setItemWidget(item, column, line_edit)

        line_edit.editingFinished.connect(lambda: self._rename_item(column=column, item=item, line_edit=line_edit))
