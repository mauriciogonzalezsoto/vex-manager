from PySide2 import QtCore
from PySide2 import QtGui

import logging

from vex_manager.config import VEXSyntaxis


logger = logging.getLogger(f"vex_manager.{__name__}")


class VEXSyntaxHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)

        keywords = "|".join(VEXSyntaxis.KEYWORDS)
        data_types = "|".join(VEXSyntaxis.DATA_TYPES)
        vex_functions = "|".join(VEXSyntaxis.VEX_FUNCTIONS)

        self.strings_reg_exp = QtCore.QRegExp(r'(["\'])((?:\\.|[^"\\])*)\1')
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
