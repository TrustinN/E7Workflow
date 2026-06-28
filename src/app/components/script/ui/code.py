from catppuccin import PALETTE
from PyQt5.Qsci import QsciLexerPython, QsciScintilla
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QVBoxLayout, QWidget


def apply_catppuccin_mocha(editor: QsciScintilla, lexer: QsciLexerPython):
    c = PALETTE.mocha.colors

    def q(color):
        return QColor(color.hex)

    # Editor background/text
    editor.setPaper(q(c.base))
    editor.setColor(q(c.text))
    editor.setCaretForegroundColor(q(c.rosewater))

    # Line numbers
    editor.setMarginsBackgroundColor(q(c.mantle))
    editor.setMarginsForegroundColor(q(c.overlay1))

    # Selection
    editor.setSelectionBackgroundColor(q(c.surface2))

    # Current line
    editor.setCaretLineVisible(True)
    editor.setCaretLineBackgroundColor(q(c.surface0))

    # Lexer defaults
    lexer.setDefaultPaper(q(c.base))
    lexer.setDefaultColor(q(c.text))

    # Comments
    lexer.setColor(q(c.overlay1), QsciLexerPython.Comment)
    lexer.setColor(q(c.overlay1), QsciLexerPython.CommentBlock)

    # Numbers
    lexer.setColor(q(c.peach), QsciLexerPython.Number)

    # Strings
    lexer.setColor(q(c.green), QsciLexerPython.SingleQuotedString)
    lexer.setColor(q(c.green), QsciLexerPython.DoubleQuotedString)
    lexer.setColor(q(c.green), QsciLexerPython.TripleSingleQuotedString)
    lexer.setColor(q(c.green), QsciLexerPython.TripleDoubleQuotedString)

    # Keywords
    lexer.setColor(q(c.mauve), QsciLexerPython.Keyword)

    # Class names
    lexer.setColor(q(c.yellow), QsciLexerPython.ClassName)

    # Function names
    lexer.setColor(q(c.blue), QsciLexerPython.FunctionMethodName)

    # Operators
    lexer.setColor(q(c.sky), QsciLexerPython.Operator)

    # Decorators
    lexer.setColor(q(c.flamingo), QsciLexerPython.Decorator)

    # Identifiers
    lexer.setColor(q(c.text), QsciLexerPython.Identifier)

    # Highlighted identifiers
    lexer.setColor(q(c.lavender), QsciLexerPython.HighlightedIdentifier)


class CodeEditor(QWidget):
    textChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.editor = QsciScintilla()
        lexer = QsciLexerPython()

        self.editor.setLexer(lexer)
        self.editor.setUtf8(True)
        self.editor.setMarginType(0, QsciScintilla.NumberMargin)
        self.editor.setMarginWidth(0, "000")
        self.editor.setMarginWidth(1, 0)
        self.editor.setAutoIndent(True)
        self.editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.editor.setFolding(QsciScintilla.NoFoldStyle)
        self.editor.setIndentationGuides(True)
        self.editor.setIndentationsUseTabs(False)
        self.editor.setIndentationWidth(4)
        self.editor.setTabWidth(4)
        self.editor.textChanged.connect(self.textChanged.emit)

        apply_catppuccin_mocha(self.editor, lexer)

        self.layout.addWidget(self.editor)

    def text(self):
        return self.editor.text()

    def setText(self, text):
        self.editor.setText(text)
