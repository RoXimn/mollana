# ******************************************************************************
# Copyright (C) 2026. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      Roximn <roximn148@gmail.com> Mar 2026
# ******************************************************************************
import sys
from collections import Counter
from pathlib import Path

import spacy
import unicodedataplus as ud
from symspellpy import SymSpell, Verbosity
from PySide6.QtCore import (
    QMetaObject, QPoint, QRect, QSize, Qt, QRegularExpression, QEvent, Signal
)
from PySide6.QtGui import QFont, QTextOption, QSyntaxHighlighter, QTextCharFormat, QColor, QMouseEvent, QTextCursor, \
    QAction
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMenuBar,
    QPlainTextEdit, QPushButton, QStatusBar, QTabWidget, QVBoxLayout, QWidget,
    QMainWindow, QFileDialog, QAbstractItemView, QMenu
)
from PySide6.QtWidgets import (
    QFrame, QLayout
)


# ******************************************************************************
def scriptScore(token, targetScript: str = 'ARABIC'):
    """
    Returns a score from 0.0 to 1.0 representing the proportion
    of characters in 'token' belonging to 'targetScript'.
    """
    if not token:
        return 0.0

    matchCount = 0
    # Normalize target script to uppercase for comparison
    targetScript = targetScript.upper()

    for ch in token:
        if targetScript == ud.script(ch).upper():
            matchCount += 1

    return matchCount / len(token)


# ******************************************************************************
def tokenize(text: str):
    nlp = spacy.blank('ur')

    # Spacy based tokenization
    doc = nlp(text)
    return  doc


# ******************************************************************************
def tokens2Vocab(doc, isAlpha: bool = True, scoreThreshold: float = 0.9) -> tuple[Counter, int]:

    words = [token.text for token in doc if (isAlpha and token.is_alpha) and scriptScore(token.text) >= scoreThreshold]
    wordCount = len(words)

    vocab = Counter(words)

    return vocab, wordCount


# ******************************************************************************
class SpellAction(QAction):
    """A special QAction that returns the text in a signal."""

    correct = Signal(str)

    def __init__(self, *args):
        QAction.__init__(self, *args)
        self.triggered.connect(lambda x: self.correct.emit(str(self.text())))


# ******************************************************************************
class SpellTextEdit(QPlainTextEdit):
    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)

        # Default dictionary based on the current locale.
        self.dict = SymSpell()
        dictionaryPath = "Urdu5k.sym"
        self.dict.load_dictionary(dictionaryPath, 0, 1, separator="$", encoding='utf8')

        doc = self.document()
        option = doc.defaultTextOption()
        option.setTextDirection(Qt.RightToLeft)
        option.setAlignment(Qt.AlignRight)
        option.setFlags(QTextOption.ShowTabsAndSpaces)
        doc.setDefaultTextOption(option)
        self.sourceHighlighter = WordsHighlighter(doc)
        self.sourceHighlighter.setDict(self.dict)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            event = QMouseEvent(
                QEvent.Type.MouseButtonPress,
                event.position(),
                event.globalPosition(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButtons(Qt.MouseButton.LeftButton),
                event.modifiers()
            )
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        mnuPopup = self.createStandardContextMenu()

        # Select the word under the cursor.
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        self.setTextCursor(cursor)

        # Check if the selected word is misspelled and offer spelling
        # suggestions if it is.
        if self.textCursor().hasSelection():
            text = self.textCursor().selectedText()
            suggestions = self.dict.lookup(text, Verbosity.CLOSEST, max_edit_distance=2)
            if suggestions:
                mnuSpellings = QMenu('Spelling Suggestions')
                for suggestion in suggestions:
                    action = SpellAction(suggestion.term, mnuSpellings)
                    action.correct.connect(self.correctWord)
                    mnuSpellings.addAction(action)
                # Only add the spelling suggests to the menu if there are
                # suggestions.
                if len(mnuSpellings.actions()) != 0:
                    mnuPopup.insertSeparator(mnuPopup.actions()[0])
                    mnuPopup.insertMenu(mnuPopup.actions()[0], mnuSpellings)

        mnuPopup.exec(event.globalPos())

    def correctWord(self, word):
        """Replaces the selected text with word."""
        cursor = self.textCursor()
        cursor.beginEditBlock()

        cursor.removeSelectedText()
        cursor.insertText(word)

        cursor.endEditBlock()


# ******************************************************************************
LINE_COLORS = [
    "#e68a8a",
    "#8ae6c7",
    "#e6a88a",
    "#8ab9e6",
]

# ******************************************************************************
class WordsHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.whiteSpceFormat = QTextCharFormat()
        self.whiteSpceFormat.setForeground(QColor("#888"))
        self.whitespacePattern = QRegularExpression(r"\s")

        self.errorFormat = QTextCharFormat()
        # self.errorFormat.setUnderlineStyle(QTextCharFormat.WaveUnderline)
        self.errorFormat.setUnderlineColor(Qt.red)
        self.errorFormat.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

        self.symSpell = SymSpell()

        self.dict = None

    def setDict(self, dict):
        self.dict = dict

    def highlightBlock(self, text):
        # Match and apply color to the visible whitespace symbols
        matches = self.whitespacePattern.globalMatch(text)
        while matches.hasNext():
            match = matches.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.whiteSpceFormat)

        if not self.dict:
            return

        tokens = tokenize(text)
        # n = 0
        for token in tokens:
            # if not token.is_alpha:
            #     continue
            suggestions = self.dict.lookup(token.text, Verbosity.CLOSEST, max_edit_distance=0)
            if not suggestions:
            # if token.is_alpha:
            #     self.errorFormat.setUnderlineColor(QColor("red"))
            # else:
            #     self.errorFormat.setUnderlineColor(QColor(LINE_COLORS[n]))
            #     n = (n + 1) % len(LINE_COLORS)
                self.setFormat(token.idx, len(token), self.errorFormat)

# ******************************************************************************
class Ui_MainWindow(object):
    # --------------------------------------------------------------------------
    def setupUi(self, parentWindow):
        parentWindow.setObjectName(u"VocabMainWindow")
        parentWindow.setWindowTitle("Vocabulary Editor")
        parentWindow.resize(800, 600)

        self.centralwidget = QWidget(parentWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tbNew = QWidget()
        self.tbNew.setObjectName(u"tbNew")
        self.verticalLayout = QVBoxLayout(self.tbNew)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.tbNew)
        self.label.setObjectName(u"label")
        self.label.setText("Source")

        self.horizontalLayout.addWidget(self.label)

        self.leSourceFile = QLineEdit(self.tbNew)
        self.leSourceFile.setObjectName(u"leSourceFile")
        self.leSourceFile.setReadOnly(True)

        self.horizontalLayout.addWidget(self.leSourceFile)

        self.btnSelectSource = QPushButton(self.tbNew)
        self.btnSelectSource.setObjectName(u"btnSelectSource")
        self.btnSelectSource.setText("Open...")
        self.btnSelectSource.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self.horizontalLayout.addWidget(self.btnSelectSource)

        self.btnSave = QPushButton(self.tbNew)
        self.btnSave.setObjectName(u"btnSave")
        self.btnSave.setText("Save...")
        self.btnSave.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self.horizontalLayout.addWidget(self.btnSave)

        self.btnSaveAs = QPushButton(self.tbNew)
        self.btnSaveAs.setObjectName(u"btnSaveAs")
        self.btnSaveAs.setText("Save As...")
        self.btnSaveAs.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.horizontalLayout.addWidget(self.btnSaveAs)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tbxSourceText = SpellTextEdit(self.tbNew)
        self.tbxSourceText.setObjectName(u"tbxSourceText")
        self.tbxSourceText.setReadOnly(True)
        self.tbxSourceText.setStyleSheet("background-color: #f0f0f0;")
        urduFont = QFont()
        urduFont.setFamilies([u"Noto Naskh Arabic"])
        urduFont.setPointSize(32)
        self.tbxSourceText.setFont(urduFont)

        self.verticalLayout.addWidget(self.tbxSourceText)

        self.lstWords = QListWidget(self.tbNew)
        self.lstWords.setObjectName(u"lstWords")
        self.lstWords.setFont(urduFont)
        self.lstWords.setLayoutDirection(Qt.RightToLeft)
        self.lstWords.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lstWords.setAlternatingRowColors(True)
        self.lstWords.setStyleSheet("""
            QListWidget { outline: 0; }
            QListWidget::item:selected {
                background-color: #888;
            }
            QListWidget::item:hover {
                background-color: #CCC;
                color: #fff;
            }
        """)

        self.verticalLayout.addWidget(self.lstWords)

        self.tcWordComposition = TagCloud(self.tbNew)
        self.tcWordComposition.setObjectName(u"tcWordComposition")

        self.verticalLayout.addWidget(self.tcWordComposition)

        self.tabWidget.addTab(self.tbNew, "New")
        self.tbMerge = QWidget()
        self.tbMerge.setObjectName(u"tbMerge")
        self.tabWidget.addTab(self.tbMerge, "Merge")

        self.verticalLayout_2.addWidget(self.tabWidget)

        parentWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(parentWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        parentWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(parentWindow)
        self.statusbar.setObjectName(u"statusbar")
        parentWindow.setStatusBar(self.statusbar)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(parentWindow)

# ******************************************************************************
class MainWindow(QMainWindow):
    # --------------------------------------------------------------------------
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setStyleSheet("""
            #Tag { background-color: #e1e4e8; border-radius: 4px; border: 1px solid #ccc; }
            #Tag:hover { background-color: #d1d5da; }
        """)

        self.ui.btnSelectSource.clicked.connect(self.onOpenFile)
        self.ui.lstWords.currentItemChanged.connect(self.onSelectionChanged)

    # ******************************************************************************
    def onOpenFile(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            caption="Open Text File",
            dir="",
            filter="Text Files (*.txt);;All Files (*)"
        )

        if filePath:
            self.loadInputFile(filePath)

    # ******************************************************************************
    def onSelectionChanged(self, current, previous):
        if current:
            self.ui.tcWordComposition.inputField.setText(current.text())

    # ******************************************************************************
    def loadInputFile(self, filePath):
        assert filePath is not None
        assert type(filePath) == str
        sourceFilePath = Path(filePath)
        assert sourceFilePath.exists(), "Source file does not exist"

        # Load source text and trim to tokenizer limit
        sourceTxt = sourceFilePath.read_text(encoding='utf8')
        if len(sourceTxt) > 1_000_000:
            sourceTxt = sourceTxt[:1_000_000]
            print("Trimming input text size to 1,000,000")
        else:
            print(f"Input text size: {len(sourceTxt):,}")

        doc = tokenize(sourceTxt)
        tokenCount = len(doc)
        vocabulary, wordCount = tokens2Vocab(doc)
        vocabCount = len(vocabulary)
        print(f"Totals:: {tokenCount=:,} {wordCount=:,} {vocabCount=:,}")

        # Update UI
        self.ui.leSourceFile.setText(filePath)
        self.ui.tbxSourceText.setPlainText(sourceTxt)
        self.ui.lstWords.clear()
        self.ui.lstWords.addItems([w for w, f in vocabulary.most_common()])
        self.ui.tcWordComposition.inputField.clear()

# Read a text file.
# Tokenize the contents.
# Extract all Urdu the words.
# Optionally use a dictionary to screen new words.
# Allow the to edit the new words.
# Reparse the input document for word frequency.
# Save the new vocabulary

# ******************************************************************************
# Unicode Character Category Color Assignment
COLORS = {
    'L': "#c7e68a",     # Letter
    'M': "#e6a88a",     # Mark
    'N': "#e6c78a",     # Number
    'P': "#e68a8a",     # Punctuation
    'S': "#e6e68a",     # Symbol
    'Z': "#8ae6c7",     # Seperator
    'C': "#8ab9e6",     # Control
}


# ******************************************************************************
class FlowLayout(QLayout):
    """Custom layout that wraps widgets horizontally."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._itemsList = []

    def addItem(self, item): self._itemsList.append(item)
    def count(self): return len(self._itemsList)
    def itemAt(self, index): return self._itemsList[index] if 0 <= index < len(self._itemsList) else None
    def takeAt(self, index): return self._itemsList.pop(index) if 0 <= index < len(self._itemsList) else None
    def expandingDirections(self): return Qt.Orientations(0)
    def hasHeightForWidth(self): return True

    def heightForWidth(self, width):
        return self.layoutItems(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.layoutItems(rect, False)

    def sizeHint(self): return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._itemsList:
            size = size.expandedTo(item.minimumSize())
        return size + QSize(10, 10)

    def layoutItems(self, rect, test_only):
        # Check current layout direction
        isRtl = self.parentWidget().layoutDirection() == Qt.RightToLeft

        # Start at the right edge for RTL, or the left edge for LTR
        xStart = rect.right() if isRtl else rect.x()
        x, y, lineHeight = xStart, rect.y(), 0
        spacing = 2

        for item in self._itemsList:
            itemW = item.sizeHint().width()
            itemH = item.sizeHint().height()

            if isRtl:
                # RTL Logic: Check if there's enough space to the LEFT
                if x - itemW < rect.left() and lineHeight > 0:
                    x = xStart
                    y = y + lineHeight + spacing
                    lineHeight = 0

                if not test_only:
                    # Top-left point is (current x - width)
                    item.setGeometry(QRect(QPoint(x - itemW, y), item.sizeHint()))

                # Move cursor left for next item
                x = x - itemW - spacing
            else:
                # LTR Logic: Check if there's enough space to the RIGHT
                if x + itemW > rect.right() and lineHeight > 0:
                    x = xStart
                    y = y + lineHeight + spacing
                    lineHeight = 0

                if not test_only:
                    item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

                # Move cursor right for next item
                x = x + itemW + spacing

            lineHeight = max(lineHeight, itemH)
        return y + lineHeight - rect.y()

        # x, y, lineHeight = rect.x(), rect.y(), 0
        # spacing = 2
        # for item in self._itemsList:
        #     next_x = x + item.sizeHint().width() + spacing
        #     if next_x - spacing > rect.right() and lineHeight > 0:
        #         x, y, lineHeight = rect.x(), y + lineHeight + spacing, 0
        #     if not test_only:
        #         item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
        #     x = x + item.sizeHint().width() + spacing
        #     lineHeight = max(lineHeight, item.sizeHint().height())
        # return y + lineHeight - rect.y()

# ******************************************************************************
class TagWidget(QFrame):
    """Single tag bubble with a remove button."""
    # --------------------------------------------------------------------------
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setObjectName("Tag")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)

        self.label = QLabel(text)
        # self.btnClose = QPushButton("×")
        # self.btnClose.setFixedSize(16, 16)
        # self.btnClose.setCursor(Qt.PointingHandCursor)
        # self.btnClose.setStyleSheet("border: none; font-weight: bold; background: transparent;")

        layout.addWidget(self.label)
        # layout.addWidget(self.btnClose)
        # self.btnClose.clicked.connect(self.deleteLater)

# ******************************************************************************
class TagCloud(QWidget):
    """Main container with input and cloud."""
    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        mainLayout = QVBoxLayout(self)
        self.inputField = QLineEdit()
        urduFont = QFont()
        urduFont.setFamilies([u"Noto Naskh Arabic"])
        urduFont.setPointSize(18)
        self.inputField.setFont(urduFont)
        self.inputField.setReadOnly(True)
        self.inputField.setLayoutDirection(Qt.RightToLeft)
        self.inputField.textChanged.connect(self.onTextChanged)

        self.container = QWidget()
        self.container.setLayoutDirection(Qt.RightToLeft)
        self.flowLayout = FlowLayout(self.container)
        self.flowLayout.setSpacing(8)

        mainLayout.addWidget(self.inputField)
        mainLayout.addWidget(self.container)
        mainLayout.addStretch()

    # --------------------------------------------------------------------------
    def addTags(self, text):
        if text:
            self.clearTags(self.flowLayout)
            for ch in text:
                widget = TagWidget(f"U+{ord(ch):04X}")
                widget.setToolTip(ud.name(ch, "NDEF"))
                uniCategory = ud.category(ch)
                # Use major category for color selection
                bgColor = COLORS[uniCategory[0]]
                widget.setStyleSheet(f"background-color : {bgColor};")

                self.flowLayout.addWidget(widget)

    # --------------------------------------------------------------------------
    def clearTags(self, layout=None):
        if layout is not None:
            while self.flowLayout.count():
                item = self.flowLayout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearTags(item.layout())

    # --------------------------------------------------------------------------
    def onTextChanged(self, newText):
        self.addTags(newText)


# ******************************************************************************
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


# ******************************************************************************
if __name__ == '__main__':
    main()


# ******************************************************************************
