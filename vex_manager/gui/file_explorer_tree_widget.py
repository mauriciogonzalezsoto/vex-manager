from __future__ import annotations

from PySide2 import QtWidgets
from PySide2 import QtCore

from pathlib import Path
import logging
import os

import vex_manager.core as core


logger = logging.getLogger(f"vex_manager.{__name__}")


class FileExplorerTreeWidget(QtWidgets.QTreeWidget):
    item_renamed = QtCore.Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self.setHeaderHidden(True)

        self._create_connections()

    def _create_connections(self) -> None:
        self.itemChanged.connect(self.rename_item)

    def find_item_by_path(self, path: str) -> QtWidgets.QTreeWidgetItem | None:
        base_name = Path(path).stem
        items = self.findItems(base_name, QtCore.Qt.MatchExactly, 0)

        if items:
            item = items[0]
            item_data = item.data(0, QtCore.Qt.UserRole)

            if item_data == os.path.normpath(path):
                return item

        return

    def get_top_level_items(self) -> tuple[QtWidgets.QTreeWidgetItem, ...]:
        items = []

        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            items.append(item)

        return tuple(items)

    def rename_item(self, item: QtWidgets.QTreeWidgetItem, new_name: str = "") -> None:
        if not new_name:
            new_name = item.text(0)

        file_path = item.data(0, QtCore.Qt.UserRole)
        new_file_path, new_base_name = core.rename_vex_file(
            file_path=file_path, new_name=new_name
        )

        self.blockSignals(True)
        item.setData(0, QtCore.Qt.UserRole, new_file_path)
        item.setText(0, new_base_name)
        self.blockSignals(False)

        self.item_renamed.emit(new_file_path)
