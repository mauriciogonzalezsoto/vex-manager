from PySide2 import QtWidgets

import sys

from vex_manager.gui.preferences_ui import PreferencesUI


def main():
    app = QtWidgets.QApplication(sys.argv)

    texture_settings_widget = PreferencesUI()
    texture_settings_widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
