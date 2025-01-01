from PySide2 import QtWidgets

import sys

from vex_manager.gui.file_explorer_tree_widget import FileExplorerTreeWidget


def main():
    app = QtWidgets.QApplication(sys.argv)

    texture_settings_widget = FileExplorerTreeWidget()
    texture_settings_widget.show()

    for i in range(10):
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, f"Item {i}")
        texture_settings_widget.addTopLevelItem(item)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
