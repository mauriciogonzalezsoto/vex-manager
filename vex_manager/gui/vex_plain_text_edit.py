from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

import logging
import json
import os

from vex_manager.config import VEXSyntaxis
import vex_manager.utils as utils


logger = logging.getLogger(f'vex_manager.{__name__}')


class VEXPlainTextEdit(QtWidgets.QPlainTextEdit):

    def __init__(self) -> None:
        super().__init__()

        self.preferences_path = utils.get_preferences_path()

        self.auto_indent = True
        self.insert_closing_brackets = True
        self.insert_closing_quotes = True
        self.backspace_on_tab_space = True
        self.tab_size = 4

        self.font = QtGui.QFont()
        self.font.setBold(True)
        self.font.setWordSpacing(5)

        self.setFont(self.font)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)

        VEXSyntaxHighlighter(self.document())

        self.load_preferences()

    def _handle_cursor_behavior(self, char: str) -> bool:
        text_cursor = self.textCursor()
        text_cursor_selected_text = text_cursor.selectedText()

        if not text_cursor_selected_text:
            cursor_position = text_cursor.position()

            if cursor_position:
                plain_text = self.toPlainText()

                if cursor_position < len(plain_text):
                    text_at_cursor = self.toPlainText()[cursor_position]

                    if text_at_cursor == char:
                        text_cursor = self.textCursor()
                        text_cursor.movePosition(text_cursor.NextCharacter)
                        self.setTextCursor(text_cursor)

                        return True

        return False

    def _insert_matching_delimiter(self, delimiter: str) -> None:
        if delimiter == '{':
            matching_delimiter = '}'
        elif delimiter == '(':
            matching_delimiter = ')'
        elif delimiter == '[':
            matching_delimiter = ']'
        elif delimiter == '"':
            matching_delimiter = '"'
        elif delimiter == '\'':
            matching_delimiter = '\''
        else:
            matching_delimiter = ''

        self.insertPlainText(delimiter)
        self.insertPlainText(matching_delimiter)

        text_cursor = self.textCursor()
        text_cursor.movePosition(text_cursor.PreviousCharacter)
        self.setTextCursor(text_cursor)

    def load_preferences(self) -> None:
        settings = {}

        if os.path.exists(self.preferences_path):
            with open(self.preferences_path, 'r') as file_for_read:
                settings = json.load(file_for_read)

        self.auto_indent = settings.get('auto_indent', True)
        self.insert_closing_brackets = settings.get('insert_closing_brackets', True)
        self.insert_closing_quotes = settings.get('insert_closing_quotes', True)
        self.backspace_on_tab_space = settings.get('backspace_on_tab_stop', True)
        self.tab_size = settings.get('tab_size', 4)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()

        text_cursor = self.textCursor()
        text_cursor_selected_text = text_cursor.selectedText()
        text_cursor_block = text_cursor.block()
        current_line_text = text_cursor_block.text()

        if text_cursor_selected_text:
            super().keyPressEvent(event)

            return

        elif key == QtCore.Qt.Key_Tab:
            self.insertPlainText(''.ljust(self.tab_size))

            return

        elif key == QtCore.Qt.Key_Backspace:
            if self.backspace_on_tab_space:
                if current_line_text.strip() == '' and current_line_text and text_cursor.atBlockEnd():
                    delete_block = len(current_line_text) % self.tab_size

                    if delete_block == 0:
                        delete_block = self.tab_size

                    for i in range(delete_block):
                        super().keyPressEvent(event)

                    return

        elif key == QtCore.Qt.Key_Return:
            if self.auto_indent:
                leading_spaces = len(current_line_text) - len(current_line_text.lstrip())
                cursor_position = text_cursor.position() - 1

                if cursor_position >= 0:
                    text_at_cursor = self.toPlainText()[cursor_position]

                    if text_at_cursor in ['{', '(', '[']:
                        self.insertPlainText('\n\n')
                        self.insertPlainText(''.ljust(leading_spaces))

                        text_cursor.movePosition(text_cursor.Up)
                        self.setTextCursor(text_cursor)

                        leading_spaces += self.tab_size

                    else:
                        super().keyPressEvent(event)

                    self.insertPlainText(''.ljust(leading_spaces))

                    return

        elif key == QtCore.Qt.Key_BraceLeft:
            if self.insert_closing_brackets:
                self._insert_matching_delimiter('{')

                return

        elif key == QtCore.Qt.Key_BraceRight:
            if self.insert_closing_brackets:

                if self._handle_cursor_behavior('}'):
                    return

        elif key == QtCore.Qt.Key_ParenLeft:
            if self.insert_closing_brackets:
                self._insert_matching_delimiter('(')

                return

        elif key == QtCore.Qt.Key_ParenRight:
            if self.insert_closing_brackets:
                if self._handle_cursor_behavior(')'):

                    return

        elif key == QtCore.Qt.Key_BracketLeft:
            if self.insert_closing_brackets:
                self._insert_matching_delimiter('[')

                return

        elif key == QtCore.Qt.Key_BracketRight:
            if self.insert_closing_brackets:
                if self._handle_cursor_behavior(']'):

                    return

        elif key == QtCore.Qt.Key_QuoteDbl:
            if self.insert_closing_quotes:
                if self._handle_cursor_behavior('"'):

                    return
                else:
                    self._insert_matching_delimiter('"')

                    return

        elif key == QtCore.Qt.Key_Apostrophe:
            if self.insert_closing_quotes:
                if self._handle_cursor_behavior('\''):

                    return
                else:
                    self._insert_matching_delimiter('\'')

                    return

        super().keyPressEvent(event)


class VEXSyntaxHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)

        keywords = '|'.join(VEXSyntaxis.KEYWORDS)
        data_types = '|'.join(VEXSyntaxis.DATA_TYPES)
        vex_functions = '|'.join(VEXSyntaxis.VEX_FUNCTIONS)

        self.keywords_text_char_format = QtGui.QTextCharFormat()
        self.keywords_text_char_format.setForeground(QtGui.QColor('#1c78c0'))

        self.data_types_text_char_format = QtGui.QTextCharFormat()
        self.data_types_text_char_format.setForeground(QtGui.QColor('#8ed5fa'))

        self.vex_functions_text_char_format = QtGui.QTextCharFormat()
        self.vex_functions_text_char_format.setForeground(QtGui.QColor('#7E94CE'))

        self.attribute_text_char_format = QtGui.QTextCharFormat()
        self.attribute_text_char_format.setForeground(QtGui.QColor('yellow'))

        self.string_literal_text_char_format = QtGui.QTextCharFormat()
        self.string_literal_text_char_format.setForeground(QtGui.QColor('green'))

        self.comment_text_char_format = QtGui.QTextCharFormat()
        self.comment_text_char_format.setForeground(QtGui.QColor('gray'))

        self.keywords_reg_exp = QtCore.QRegExp(rf'\b({keywords})\b')
        self.data_types_reg_exp = QtCore.QRegExp(rf'\b({data_types})\b')
        self.vex_functions_reg_exp = QtCore.QRegExp(rf'\b({vex_functions})\b')
        self.attribute_reg_exp = QtCore.QRegExp(r'[\w]*@[\w-]+')
        self.string_literal_reg_exp = QtCore.QRegExp(r'(["\'].*["\'])')
        self.comment_reg_exp = QtCore.QRegExp(r'//.*')

    def _set_vex_syntax_highlighter(
            self,
            reg_exp: QtCore.QRegExp,
            text: str,
            text_char_format: QtGui.QTextCharFormat
    ) -> None:

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
            reg_exp=self.attribute_reg_exp,
            text=text,
            text_char_format=self.attribute_text_char_format)

        self._set_vex_syntax_highlighter(
            reg_exp=self.string_literal_reg_exp,
            text=text,
            text_char_format=self.string_literal_text_char_format)

        self._set_vex_syntax_highlighter(
            reg_exp=self.comment_reg_exp,
            text=text,
            text_char_format=self.comment_text_char_format)
