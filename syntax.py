from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat


class RustHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(RustHighlighter, self).__init__(parent)

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(Qt.darkBlue)
        keyword_format.setFontWeight(QFont.Bold)

        keyword_patterns = ("\\bi32\\b", "\\bi64\\b", "\\bi16\\b",
                            "\\bf16\\b", "\\bf32\\b", "\\bf64\\b",
                            "\\busize\\b", "\\blet\\b", "\\bmut\\b",
                            "\\bfn\\b", "\\bstruct\\b", "\\bpub\\b",
                            "\\buse\\b", "\\bimpl\\b", "\\bmatch\\b",
                            "\\buse\\b", "\\bconst\\b", "\\bstatic\\b",
                            "\\bfor\\b", "\\bwhile\\b", "\\bbreak\\b",
                            "\\bVec\\b", "\\bcontinue\\b", "\\bloop\\b",
                            "\\bin\\b")

        self.highlight_rules = [(QRegExp(pattern), keyword_format)
                                for pattern in keyword_patterns]

        line_comment_format = QTextCharFormat()
        line_comment_format.setForeground(Qt.red)
        self.highlight_rules.append((QRegExp("//[^\n]*"),
                                     line_comment_format))

        attribute_format = QTextCharFormat()
        attribute_format.setForeground(Qt.green)
        self.highlight_rules.append((QRegExp("#[^\n]*"),
                                     attribute_format))

        quotation_format = QTextCharFormat()
        quotation_format.setForeground(Qt.darkGreen)
        self.highlight_rules.append((QRegExp("\".*\""), quotation_format))

        function_format = QTextCharFormat()
        function_format.setFontItalic(True)
        function_format.setForeground(Qt.blue)
        self.highlight_rules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\(){}[]"),
                                     function_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlight_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
