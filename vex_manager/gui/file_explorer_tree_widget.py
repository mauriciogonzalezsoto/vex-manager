from __future__ import annotations

from PySide2 import QtWidgets
from PySide2 import QtCore

from pathlib import Path
import logging
import os

import vex_manager.core as core


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

    def find_item_by_path(self, path: str) -> QtWidgets.QTreeWidgetItem | None:
        base_name = Path(path).stem
        items = self.findItems(base_name, QtCore.Qt.MatchExactly, 0)

        if items:
            item = items[0]
            item_data = item.data(0, QtCore.Qt.UserRole)

            if item_data == os.path.normpath(path):
                return item

        return

    def get_top_level_items(self) -> list[QtWidgets.QTreeWidgetItem]:
        items = []

        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            items.append(item)

        return items

    def rename_item(self, column: int, item: QtWidgets.QTreeWidgetItem, new_name: str) -> None:
        if item:
            file_path = item.data(0, QtCore.Qt.UserRole)
            new_file_path, new_base_name = core.rename_vex_file(file_path, new_name)

            if file_path != new_file_path:
                item.setText(column, new_base_name)
                item.setData(column, QtCore.Qt.UserRole, new_file_path)

                self.item_renamed.emit(new_file_path)

    def editItem(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
        line_edit = QtWidgets.QLineEdit(self)
        line_edit.setText(item.text(column))

        self.setItemWidget(item, column, line_edit)

        line_edit.editingFinished.connect(lambda: self._rename_item(column=column, item=item, line_edit=line_edit))
