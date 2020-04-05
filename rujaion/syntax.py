import re
from typing import *

from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor


class HighlighterBase(QSyntaxHighlighter):
    colors = [
        QColor(Qt.magenta).lighter(150),
        Qt.cyan,
        Qt.yellow,
        Qt.green,
        Qt.darkCyan,
        Qt.darkYellow,
    ]

    def update_levenshtein(self, words: List[str]):
        self.levensteign_rules.clear()
        if len(words) > len(self.colors):
            return
        for word, color in zip(words, self.colors):
            format = QTextCharFormat()
            format.setBackground(color)
            self.levensteign_rules.append(
                (QRegExp("\\b" + re.escape(word) + "\\b"), format)
            )

    def highlightBlock(self, text: str):
        for pattern, format in self.highlight_rules + self.levensteign_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        self.setCurrentBlockState(0)


class RustHighlighter(HighlighterBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlight_rules = []
        function_format = QTextCharFormat()
        function_format.setFontItalic(True)
        function_format.setForeground(Qt.blue)
        self.highlight_rules.append(
            (QRegExp("\\b[A-Za-z][A-Za-z0-9_:<>\+ ]+(?=\\()"), function_format)
        )

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(Qt.magenta).darker(150))
        keyword_format.setFontWeight(QFont.Bold)

        # fmt: off
        keyword_patterns = ("\\bi16\\b", "\\bi32\\b", "\\bi64\\b", "\\bi128\\b",
                            "\\bu16\\b", "\\bu32\\b", "\\bu64\\b", "\\bu128\\b",
                            "\\bf16\\b", "\\bf32\\b", "\\bf64\\b", "\\bf128\\b",
                            "\\busize\\b", "\\bchar\\b", "\\bbool\\b",
                            "\\blet\\b", "\\bmut\\b",
                            "\\bfn\\b", "\\bstruct\\b", "\\bpub\\b",
                            "\\buse\\b", "\\bimpl\\b",
                            "\\bconst\\b", "\\bstatic\\b", "\\bstr\\b",
                            "\\bString\\b", "\\breturn\\b", "\\bwhere\\b",
                            "\\benum\\b", "\\bmatch\\b", "\\btype\\b",
                            "\\bfor\\b", "\\bwhile\\b", "\\bbreak\\b",
                            "\\bVec\\b", "\\bcontinue\\b", "\\bloop\\b",
                            "\\bin\\b", "\\belse\\b", "\\bif\\b",
                            "\\bas\\b",
                            )
        # fmt: on

        self.highlight_rules += [
            (QRegExp(pattern), keyword_format) for pattern in keyword_patterns
        ]

        const_format = QTextCharFormat()
        const_format.setForeground(Qt.darkYellow)

        # fmt: off
        const_patterns = ("\\btrue\\b", "\\bfalse\\b", "\\bNone\\b",
                          "\\bSome\\b", "\\b[0-9\.\_]+\\b", "\\b[0-9\_]+usize\\b",
                          "\\b[0-9_]+u32\\b", "\\b[0-9_]+u64\\b", "\\b[0-9_]+u128\\b",
                          "\\b[0-9_]+i32\\b", "\\b[0-9_]+i64\\b", "\\b[0-9_]+i128\\b",
                          "\\b[0-9\._]+f32\\b", "\\b[0-9\._]+f64\\b",
                          )
        # fmt: on

        self.highlight_rules += [
            (QRegExp(pattern), const_format) for pattern in const_patterns
        ]

        self_format = QTextCharFormat()
        self_format.setForeground(Qt.darkRed)
        self.highlight_rules.append((QRegExp("\\bself\\b"), self_format))

        quotation_format = QTextCharFormat()
        quotation_format.setForeground(Qt.darkGreen)
        self.highlight_rules.append((QRegExp('".*"'), quotation_format))
        self.highlight_rules.append((QRegExp("'.*'"), quotation_format))

        macro_format = QTextCharFormat()
        macro_format.setFontItalic(True)
        macro_format.setForeground(Qt.darkCyan)
        self.highlight_rules.append((QRegExp("\\b[A-Za-z0-9_]+!"), macro_format))

        attribute_format = QTextCharFormat()
        attribute_format.setForeground(QColor(Qt.green).darker(140))
        self.highlight_rules.append((QRegExp("#[^\n]*"), attribute_format))

        line_comment_format = QTextCharFormat()
        line_comment_format.setForeground(Qt.darkGray)
        self.highlight_rules.append((QRegExp("//[^\n]*"), line_comment_format))

        self.levensteign_rules = []


class CppHighlighter(HighlighterBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlight_rules = []
        function_format = QTextCharFormat()
        function_format.setFontItalic(True)
        function_format.setForeground(Qt.blue)
        self.highlight_rules.append(
            (QRegExp("\\b[A-Za-z][A-Za-z0-9_:<>\+ ]+(?=\\()"), function_format)
        )

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(Qt.magenta).darker(150))
        keyword_format.setFontWeight(QFont.Bold)

        # fmt: off
        keyword_patterns = ("\\bint\\b", "\\blong\\b", "\\bsize_t\\b",
                            "\\bchar\\b", "\\bbool\\b",
                            "\\bdouble\\b", "\\bfloat\\b", "\\bclass\\b",
                            "\\bpublic\\b", "\\bprotected\\b", "\\bprivate\\b",
                            "\\bauto\\b", "\\bstruct\\b", "\\bswitch\\b",
                            "\\bconst\\b", "\\bstatic\\b", "\\bstr\\b",
                            "\\bString\\b", "\\breturn\\b", "\\busing\\b",
                            "\\benum\\b", "\\btypedef\\b", "\\bnamespace\\b",
                            "\\bfor\\b", "\\bwhile\\b", "\\bbreak\\b",
                            "\\bcontinue\\b", "\\belse\\b", "\\bif\\b",
                            "\\btypedef\\b", "\\bconstexpr\\b",
                            )
        # fmt: on

        self.highlight_rules += [
            (QRegExp(pattern), keyword_format) for pattern in keyword_patterns
        ]

        const_format = QTextCharFormat()
        const_format.setForeground(Qt.darkYellow)

        # fmt: off
        const_patterns = ("\\btrue\\b", "\\bfalse\\b", "\\bnullptr\\b",
                          "\\bNULL\\b", "\\bSome\\b", "\\b[0-9\.\_]+\\b",
                          )
        # fmt: on

        self.highlight_rules += [
            (QRegExp(pattern), const_format) for pattern in const_patterns
        ]

        self_format = QTextCharFormat()
        self_format.setForeground(Qt.darkRed)
        self.highlight_rules.append((QRegExp("\\bthis\\b"), self_format))

        quotation_format = QTextCharFormat()
        quotation_format.setForeground(Qt.darkGreen)
        self.highlight_rules.append((QRegExp('".*"'), quotation_format))
        self.highlight_rules.append((QRegExp("'.*'"), quotation_format))

        attribute_format = QTextCharFormat()
        attribute_format.setForeground(QColor(Qt.green).darker(140))
        self.highlight_rules.append((QRegExp("#[^\n]*"), attribute_format))

        line_comment_format = QTextCharFormat()
        line_comment_format.setForeground(Qt.darkGray)
        self.highlight_rules.append((QRegExp("//[^\n]*"), line_comment_format))

        self.levensteign_rules = []


class PyHighlighter(HighlighterBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlight_rules = []
        function_format = QTextCharFormat()
        function_format.setFontItalic(True)
        function_format.setForeground(Qt.blue)
        self.highlight_rules.append((QRegExp("\\b[A-Za-z]+(?=\\()"), function_format))

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(Qt.magenta).darker(150))
        keyword_format.setFontWeight(QFont.Bold)

        # fmt: off
        keyword_patterns = ("\\bdef\\b", "\\bclass\\b",
                            "\\bglobal\\b", "\\breturn\\b", "\\bimport\\b",
                            "\\bfrom\\b",
                            "\\bfor\\b", "\\bwhile\\b", "\\bbreak\\b",
                            "\\bcontinue\\b", "\\belse\\b", "\\bif\\b",
                            "\\belif\\b", "\\btry\\b", "\\bexcept\\b",
                            "\\bfinally\\b", "\\bas\\b", "\\band\\b",
                            "\\bor\\b", "\\bnot\\b", "\\bin\\b",
                            )
        # fmt: on

        self.highlight_rules += [
            (QRegExp(pattern), keyword_format) for pattern in keyword_patterns
        ]

        const_format = QTextCharFormat()
        const_format.setForeground(Qt.darkYellow)

        # fmt: off
        const_patterns = ("\\bTrue\\b", "\\bTalse\\b", "\\bNone\\b",
                          "\\b[0-9\.\_]+\\b",
                          )
        # fmt: on

        self.highlight_rules += [
            (QRegExp(pattern), const_format) for pattern in const_patterns
        ]

        self_format = QTextCharFormat()
        self_format.setForeground(Qt.darkRed)
        self.highlight_rules.append((QRegExp("\\bself\\b"), self_format))

        quotation_format = QTextCharFormat()
        quotation_format.setForeground(Qt.darkGreen)
        self.highlight_rules.append((QRegExp('".*"'), quotation_format))
        self.highlight_rules.append((QRegExp("'.*'"), quotation_format))

        line_comment_format = QTextCharFormat()
        line_comment_format.setForeground(Qt.darkGray)
        self.highlight_rules.append((QRegExp("#[^\n]*"), line_comment_format))

        self.levensteign_rules = []
