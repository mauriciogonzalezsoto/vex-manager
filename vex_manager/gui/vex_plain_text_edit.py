from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

import logging
import json
import os

from vex_manager.config import VEXSyntaxis
from vex_manager.config import ColorScheme
import vex_manager.utils as utils


logger = logging.getLogger(f"vex_manager.{__name__}")


class VEXPlainTextEdit(QtWidgets.QPlainTextEdit):
    PREFERENCES_PATH = utils.get_preferences_path()

    def __init__(self) -> None:
        super().__init__()

        self.font = QtGui.QFont()

        self.auto_indent = True
        self.insert_closing_brackets = True
        self.insert_closing_quotes = True

        self.backspace_on_tab_space = True
        self.tab_size = 4

        self.font_family = ""
        self.font_size = 8

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)

        self.vex_syntax_highlighter = VEXSyntaxHighlighter(self.document())

        self._load_preferences()
        self.set_font_and_colors()

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
        if delimiter == "{":
            matching_delimiter = "}"
        elif delimiter == "(":
            matching_delimiter = ")"
        elif delimiter == "[":
            matching_delimiter = "]"
        elif delimiter == '"':
            matching_delimiter = '"'
        elif delimiter == "'":
            matching_delimiter = "'"
        else:
            matching_delimiter = ""

        self.insertPlainText(delimiter)
        self.insertPlainText(matching_delimiter)

        text_cursor = self.textCursor()
        text_cursor.movePosition(text_cursor.PreviousCharacter)
        self.setTextCursor(text_cursor)

    def _load_preferences(self) -> None:
        settings = {}

        if os.path.exists(VEXPlainTextEdit.PREFERENCES_PATH):
            with open(VEXPlainTextEdit.PREFERENCES_PATH, "r") as file_for_read:
                settings = json.load(file_for_read)

        self.auto_indent = settings.get("auto_indent", True)
        self.insert_closing_brackets = settings.get("insert_closing_brackets", True)
        self.insert_closing_quotes = settings.get("insert_closing_quotes", True)

        self.backspace_on_tab_space = settings.get("backspace_on_tab_stop", True)
        self.tab_size = settings.get("tab_size", 4)
        self.color_scheme = settings.get("color_scheme", {})

        if not self.color_scheme:
            for color_scheme in ColorScheme:
                color_scheme = color_scheme.value

                self.color_scheme[color_scheme["name"]] = color_scheme["color"]

        self.font_family = settings.get("font", "Source Sans Pro")
        self.font_size = settings.get("font_size", 8)

    def set_font_and_colors(self) -> None:
        self._load_preferences()

        self.font.setBold(True)
        self.font.setFamily(self.font_family)
        self.font.setPointSize(self.font_size)
        self.font.setWordSpacing(5)
        self.setFont(self.font)

        self.vex_syntax_highlighter.set_vex_systax_highlighter_colors(self.color_scheme)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()
        modifiers = event.modifiers()

        ctrl = modifiers & QtCore.Qt.ControlModifier != 0

        if key == QtCore.Qt.Key_Plus:
            if ctrl:
                point_size = self.font.pointSize()

                if point_size < 30:
                    self.font.setPointSize(point_size + 1)
                    self.setFont(self.font)

                return
        elif key == QtCore.Qt.Key_Minus:
            if ctrl:
                point_size = self.font.pointSize()

                if point_size > 6:
                    self.font.setPointSize(point_size - 1)
                    self.setFont(self.font)

                return

        text_cursor = self.textCursor()
        text_cursor_selected_text = text_cursor.selectedText()
        text_cursor_block = text_cursor.block()
        current_line_text = text_cursor_block.text()

        if text_cursor_selected_text:
            super().keyPressEvent(event)

            return

        elif key == QtCore.Qt.Key_Tab:
            self.insertPlainText("".ljust(self.tab_size))

            return

        elif key == QtCore.Qt.Key_Backspace:
            if self.backspace_on_tab_space:
                if current_line_text.strip() == "":
                    if current_line_text and text_cursor.atBlockEnd():
                        delete_block = len(current_line_text) % self.tab_size

                        if delete_block == 0:
                            delete_block = self.tab_size

                        for i in range(delete_block):
                            super().keyPressEvent(event)

                        return

        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            if self.auto_indent:
                leading_space = len(current_line_text) - len(current_line_text.lstrip())
                cursor_position = text_cursor.position() - 1

                if cursor_position >= 0:
                    text_at_cursor = self.toPlainText()[cursor_position]

                    if text_at_cursor in ["{", "(", "["]:
                        self.insertPlainText("\n\n")
                        self.insertPlainText("".ljust(leading_space))

                        text_cursor.movePosition(text_cursor.Up)
                        self.setTextCursor(text_cursor)

                        leading_space += self.tab_size

                    else:
                        super().keyPressEvent(event)

                    self.insertPlainText("".ljust(leading_space))

                    return

        elif key == QtCore.Qt.Key_BraceLeft:
            if self.insert_closing_brackets:
                self._insert_matching_delimiter("{")

                return

        elif key == QtCore.Qt.Key_BraceRight:
            if self.insert_closing_brackets:

                if self._handle_cursor_behavior("}"):
                    return

        elif key == QtCore.Qt.Key_ParenLeft:
            if self.insert_closing_brackets:
                self._insert_matching_delimiter("(")

                return

        elif key == QtCore.Qt.Key_ParenRight:
            if self.insert_closing_brackets:
                if self._handle_cursor_behavior(")"):

                    return

        elif key == QtCore.Qt.Key_BracketLeft:
            if self.insert_closing_brackets:
                self._insert_matching_delimiter("[")

                return

        elif key == QtCore.Qt.Key_BracketRight:
            if self.insert_closing_brackets:
                if self._handle_cursor_behavior("]"):

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
                if self._handle_cursor_behavior("'"):

                    return
                else:
                    self._insert_matching_delimiter("'")

                    return

        super().keyPressEvent(event)


class VEXSyntaxHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)

        keywords = "|".join(VEXSyntaxis.KEYWORDS)
        data_types = "|".join(VEXSyntaxis.DATA_TYPES)
        vex_functions = "|".join(VEXSyntaxis.VEX_FUNCTIONS)

        self.strings_reg_exp = QtCore.QRegExp(r'(["\'].*["\'])')
        self.numbers_reg_exp = QtCore.QRegExp(r"\b\d+(\.\d+)?\b")
        self.comments_reg_exp = QtCore.QRegExp(r"//.*")
        self.functions_reg_exp = QtCore.QRegExp(rf"\b({vex_functions})\b")
        self.keywords_reg_exp = QtCore.QRegExp(rf"\b({keywords})\b")
        self.types_reg_exp = QtCore.QRegExp(rf"\b({data_types})\b")
        self.references_reg_exp = QtCore.QRegExp(r"[\w]*@[\w-]+")

        self.plain_text_char_format = QtGui.QTextCharFormat()
        self.strings_text_char_format = QtGui.QTextCharFormat()
        self.numbers_text_char_format = QtGui.QTextCharFormat()
        self.comments_text_char_format = QtGui.QTextCharFormat()
        self.functions_text_char_format = QtGui.QTextCharFormat()
        self.keywords_text_char_format = QtGui.QTextCharFormat()
        self.types_text_char_format = QtGui.QTextCharFormat()
        self.references_text_char_format = QtGui.QTextCharFormat()

    def set_vex_systax_highlighter_colors(
        self, color_scheme: dict[str, tuple[float, float, float]]
    ) -> None:
        self.plain_text_char_format.setForeground(QtGui.QColor(*color_scheme["plain"]))
        self.strings_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["strings"])
        )
        self.numbers_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["numbers"])
        )
        self.comments_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["comments"])
        )
        self.functions_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["functions"])
        )
        self.keywords_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["keywords"])
        )
        self.types_text_char_format.setForeground(QtGui.QColor(*color_scheme["types"]))
        self.references_text_char_format.setForeground(
            QtGui.QColor(*color_scheme["references"])
        )

        self.rehighlight()

    def _set_vex_syntax_highlighter(
        self,
        reg_exp: QtCore.QRegExp,
        text: str,
        text_char_format: QtGui.QTextCharFormat,
    ) -> None:

        index = reg_exp.indexIn(text)

        while index >= 0:
            length = reg_exp.matchedLength()
            self.setFormat(index, length, text_char_format)
            index = reg_exp.indexIn(text, index + length)

    def highlightBlock(self, text: str) -> None:
        self.setFormat(0, len(text), self.plain_text_char_format)

        self._set_vex_syntax_highlighter(
            reg_exp=self.numbers_reg_exp,
            text=text,
            text_char_format=self.numbers_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.functions_reg_exp,
            text=text,
            text_char_format=self.functions_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.keywords_reg_exp,
            text=text,
            text_char_format=self.keywords_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.types_reg_exp,
            text=text,
            text_char_format=self.types_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.references_reg_exp,
            text=text,
            text_char_format=self.references_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.comments_reg_exp,
            text=text,
            text_char_format=self.comments_text_char_format,
        )

        self._set_vex_syntax_highlighter(
            reg_exp=self.strings_reg_exp,
            text=text,
            text_char_format=self.strings_text_char_format,
        )
