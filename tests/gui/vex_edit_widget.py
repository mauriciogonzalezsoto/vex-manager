from PySide2 import QtWidgets

import sys

from vex_manager.gui.vex_editor_widget import VEXEditorWidget


def main():
    app = QtWidgets.QApplication(sys.argv)

    texture_settings_widget = VEXEditorWidget()
    texture_settings_widget.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
