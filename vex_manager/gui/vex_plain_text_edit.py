from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

from vex_manager.config import VEXSyntaxis


class VEXPlainTextEdit(QtWidgets.QPlainTextEdit):

    def __init__(self) -> None:
        super(VEXPlainTextEdit, self).__init__()

        self.font = QtGui.QFont()
        self.font.setBold(True)

        self.setFont(self.font)

        VEXSyntaxHighlighter(self.document())

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Tab:
            self.insertPlainText('    ')
        else:
            super(VEXPlainTextEdit, self).keyPressEvent(event)


class VEXSyntaxHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, parent: QtCore.QObject) -> None:
        super(VEXSyntaxHighlighter, self).__init__(parent)

        keywords = '|'.join(VEXSyntaxis.KEYWORDS)
        data_types = '|'.join(VEXSyntaxis.DATA_TYPES)
        vex_functions = '|'.join(VEXSyntaxis.VEX_FUNCTIONS)

        self.keywords_text_char_format = QtGui.QTextCharFormat()
        self.keywords_text_char_format.setForeground(QtGui.QColor('#1c78c0'))

        self.data_types_text_char_format = QtGui.QTextCharFormat()
        self.data_types_text_char_format.setForeground(QtGui.QColor('#8ed5fa'))

        self.vex_functions_text_char_format = QtGui.QTextCharFormat()
        self.vex_functions_text_char_format.setForeground(QtGui.QColor('#7E94CE'))

        self.comment_text_char_format = QtGui.QTextCharFormat()
        self.comment_text_char_format.setForeground(QtGui.QColor('gray'))

        self.keywords_reg_exp = QtCore.QRegExp(rf'\b({keywords})\b')
        self.data_types_reg_exp = QtCore.QRegExp(rf'\b({data_types})\b')
        self.vex_functions_reg_exp = QtCore.QRegExp(rf'\b({vex_functions})\b')
        self.comment_reg_exp = QtCore.QRegExp(r'//.*')

    def _set_vex_syntax_highlighter(self, reg_exp: QtCore.QRegExp, text: str,
                                    text_char_format: QtGui.QTextCharFormat) -> None:
        index = reg_exp.indexIn(text)

        while index >= 0:
            length = reg_exp.matchedLength()
            self.setFormat(index, length, text_char_format)
            index = reg_exp.indexIn(text, index + length)

    def highlightBlock(self, text: str) -> None:
        self._set_vex_syntax_highlighter(
            reg_exp=self.keywords_reg_exp,
            text=text,
            text_char_format=self.keywords_text_char_format)

        self._set_vex_syntax_highlighter(
            reg_exp=self.data_types_reg_exp,
            text=text,
            text_char_format=self.data_types_text_char_format)

        self._set_vex_syntax_highlighter(
            reg_exp=self.vex_functions_reg_exp,
            text=text,
            text_char_format=self.vex_functions_text_char_format)

        self._set_vex_syntax_highlighter(
            reg_exp=self.comment_reg_exp,
            text=text,
            text_char_format=self.comment_text_char_format)


