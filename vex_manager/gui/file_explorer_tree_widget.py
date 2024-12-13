from PySide2 import QtWidgets
from PySide2 import QtCore

import logging
import os

import vex_manager.utils as utils


logger = logging.getLogger(f'vex_manager.{__name__}')


class FileExplorerTreeWidget(QtWidgets.QTreeWidget):
    item_renamed = QtCore.Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.setHeaderHidden(True)

        self._create_connections()

    def _create_connections(self) -> None:
        self.itemDoubleClicked.connect(self.editItem)

    def _rename_item(self, column: int, item: QtWidgets.QTreeWidgetItem, line_edit: QtWidgets.QLineEdit) -> None:
        new_name = line_edit.text()

        self.rename_item(column=column, item=item, new_name=new_name)
        self.removeItemWidget(item, column)

    def get_top_level_items(self) -> list[QtWidgets.QTreeWidgetItem]:
        top_level_items = []

        for i in range(self.topLevelItemCount()):
            top_level_items.append(self.topLevelItem(i))

        return top_level_items

    def rename_item(self, column: int, item: QtWidgets.QTreeWidgetItem, new_name: str) -> None:
        file_path = item.data(0, QtCore.Qt.UserRole)

        if new_name != item.text(0):
            if new_name in [item.text(0) for item in self.get_top_level_items()]:
                logger.error(f'File {new_name!r} already exists.')
            elif not utils.is_valid_file_name(new_name):
                logger.error(f'{new_name!r} is not a valid file name.')
            else:
                dir_name = os.path.dirname(file_path)
                new_file_path = os.path.join(dir_name, f'{new_name}.vex')

                item.setText(column, new_name)
                item.setData(column, QtCore.Qt.UserRole, new_file_path)

                os.rename(file_path, new_file_path)

                self.item_renamed.emit(new_file_path)

                logger.debug(f'Renamed file {file_path!r} -> {new_file_path!r}')
        else:
            logger.debug(f'{new_name!r} is the same name.')

    def editItem(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
        line_edit = QtWidgets.QLineEdit(self)
        line_edit.setText(item.text(column))

        self.setItemWidget(item, column, line_edit)

        line_edit.editingFinished.connect(lambda: self._rename_item(column=column, item=item, line_edit=line_edit))
