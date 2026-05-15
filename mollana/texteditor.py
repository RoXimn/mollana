# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from collections import namedtuple

from PySide6.QtCore import QSize, Qt, QRegularExpression
from PySide6.QtGui import (
    QPaintEvent, QResizeEvent, QSyntaxHighlighter, QTextCharFormat, QTextOption,
    QColor, QTextFormat, QPainter, QTextCursor, QFont
)
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit, QListWidget

from mollana.mapping import loadDictionaries, processRomanToken

# ******************************************************************************
HighlightingRule = namedtuple('HighlightingRule',
                              ['pattern', 'format'])


# ******************************************************************************
class Highlighter(QSyntaxHighlighter):
    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules: list[HighlightingRule] = []

        whiteSpaceFormat = QTextCharFormat()
        whiteSpaceFormat.setForeground(Qt.gray)
        rule = HighlightingRule(pattern=QRegularExpression("\\s+"),
                                format=whiteSpaceFormat)
        self.highlightingRules.append(rule)

        numericFormat = QTextCharFormat()
        numericFormat.setForeground(Qt.red)
        rule = HighlightingRule(pattern=QRegularExpression("\\d+"),
                                format=numericFormat)
        self.highlightingRules.append(rule)

        punctuationFormat = QTextCharFormat()
        punctuationFormat.setForeground(Qt.darkGreen)
        rule = HighlightingRule(pattern=QRegularExpression("(\\.\\.)+"),
                                format=punctuationFormat)
        self.highlightingRules.append(rule)
        rule = HighlightingRule(pattern=QRegularExpression("(\\-\\-)+"),
                                format=punctuationFormat)
        self.highlightingRules.append(rule)
        rule = HighlightingRule(pattern=QRegularExpression("(?=\\d)\\.(?=\\d)"),
                                format=punctuationFormat)
        self.highlightingRules.append(rule)
        rule = HighlightingRule(pattern=QRegularExpression("[\\?\\|;%\\*\\(\\)\\{\\}\\[\\]\\!\\@\\#\\$\\&\\-\\+\\=]+"),
                                format=punctuationFormat)
        self.highlightingRules.append(rule)

    # --------------------------------------------------------------------------
    def highlightBlock(self, text: str):
        for (pattern, fmt) in self.highlightingRules:
            matchIter = pattern.globalMatch(text)
            while matchIter.hasNext():
                match = matchIter.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


# ******************************************************************************
class LineNumberArea(QWidget):
    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.textEditor = parent

    # --------------------------------------------------------------------------
    def sizeHint(self) -> QSize:
        return QSize(self.textEditor.lineNumberAreaWidth(), 0)

    # --------------------------------------------------------------------------
    def paintEvent(self, event: QPaintEvent):
        self.textEditor.lineNumberAreaPaintEvent(event)


# ******************************************************************************
class SuggestionPopup(QListWidget):
    # --------------------------------------------------------------------------
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setFixedWidth(150)
        self.setFont(QFont('Calibri', 16))
        self.setLayoutDirection(Qt.RightToLeft)
        self.hide()

    # --------------------------------------------------------------------------
    def showSuggestions(self, suggestions, pos):
        self.clear()
        self.addItems(suggestions)
        self.setCurrentRow(0)
        # Move popup to the global screen position of the cursor
        self.move(pos.x() - self.width(), pos.y())
        self.show()


# ******************************************************************************
class TextEditor(QPlainTextEdit):
    # --------------------------------------------------------------------------
    def __init__(self, /, parent=None):
        super(TextEditor, self).__init__(parent)
        self.parent = parent

        self.RomanUrduDict, self.DeromanizerMapping = (
            loadDictionaries("RomanizedUrduWords150k.dict",
                               "RomanizedUrduWords150k.csv"))

        doc = self.document()
        self.highlighter = Highlighter(doc)
        self.lineNumberArea = LineNumberArea(self)

        option = doc.defaultTextOption()
        option.setFlags(option.flags() | QTextOption.ShowTabsAndSpaces)
        option.setTextDirection(Qt.LayoutDirection.RightToLeft)
        option.setAlignment(Qt.AlignmentFlag.AlignRight)
        doc.setDefaultTextOption(option)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth()
        self.highlightCurrentLine()

        self.popup = SuggestionPopup(self)
        self.popup.itemClicked.connect(self.insertSuggestion)
        self.textChanged.connect(self.onTextChanged)

    # --------------------------------------------------------------------------
    def onTextChanged(self):
        # Logic to get the current word being typed
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        word = cursor.selectedText()

        if len(word) >= 1:
            u0, u1, u2 = processRomanToken(word, self.RomanUrduDict, self.DeromanizerMapping)
            uX = u0 if u0 else (u1 if u1 else u2)
            # print(f"'{word}' -> [{len(uX):2d}] {uX}")
            suggestions = [w for w, r, f in uX] if uX else []
            if suggestions:
                # Calculate cursor screen position
                rect = self.cursorRect()
                globalPos = self.viewport().mapToGlobal(rect.bottomLeft())
                self.popup.showSuggestions(suggestions, globalPos)
                self.setFocus()  # Keep focus on editor to continue typing
            else:
                self.popup.hide()
        else:
            self.popup.hide()

    # --------------------------------------------------------------------------
    def insertSuggestion(self, item, terminalChar = " "):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        cursor.insertText(item.text() + terminalChar)
        self.popup.hide()

    # --------------------------------------------------------------------------
    def keyPressEvent(self, event):
        # Allow navigating the popup with arrow keys without losing focus
        EndOfWord = " ~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        if self.popup.isVisible():
            if event.key() == Qt.Key_Down:
                self.popup.setCurrentRow((self.popup.currentRow() + 1) % self.popup.count())
                return
            elif event.key() == Qt.Key_Up:
                self.popup.setCurrentRow((self.popup.currentRow() - 1) % self.popup.count())
                return
            elif event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab) or event.text() in EndOfWord:
                if event.text() in EndOfWord:
                    trChar = event.text()
                elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    trChar = '\n'
                else:
                    trChar = '\t'
                self.insertSuggestion(self.popup.currentItem(), trChar)
                return
            elif event.key() == Qt.Key_Escape:
                self.popup.hide()
                return
        super().keyPressEvent(event)

        # self.completer = QCompleter([""], self)
        # self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        # self.completer.setWidget(self)
        # self.completer.setCompletionMode(QCompleter.PopupCompletion)
        # self.completer.activated.connect(self.insertCompletion)

    # def insertCompletion(self, completion):
    #     tc = self.textCursor()
    #     extra = len(completion) - len(self.completer.completionPrefix())
    #     tc.movePosition(QTextCursor.Left)
    #     tc.movePosition(QTextCursor.EndOfWord)
    #     tc.insertText(completion[-extra:])
    #     self.setTextCursor(tc)

    # def textUnderCursor(self):
    #     tc = self.textCursor()
    #     tc.select(QTextCursor.WordUnderCursor)
    #     return tc.selectedText()


    # def updateSuggestions(self, prefix):
    #     """Simulate fetching dynamic data based on the prefix."""
    #     # Replace this logic with your API call or database query
    #     u0, u1, u2 = processRomanToken(prefix, self.RomanUrduDict, self.DeromanizerMapping)
    #
    #     uX = u0 if u0 else u1 if u1 else u2
    #     print(f"'{prefix}' -> [{len(uX):2d}] {uX}")
    #     dynamicSuggestions = [r for w, r, f in uX] if uX else []
    #     print(f"'\t -> [{len(dynamicSuggestions):2d}] {dynamicSuggestions}")
    #
    #     # Update the model with new data
    #     model = self.completer.model()
    #     if isinstance(model, QStringListModel):
    #         model.setStringList(dynamicSuggestions)

    # def keyPressEvent(self, event):
    #     if self.completer and self.completer.popup().isVisible():
    #         if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab):
    #             event.ignore()
    #             return
    #         elif event.key() in (Qt.Key_Space,):
    #             popup = self.completer.popup()
    #             currentIndex = popup.currentIndex()
    #             if currentIndex.isValid():
    #                 model = self.completer.completionModel()
    #                 selectedText = model.data(currentIndex)
    #                 print(f"Space key pressed over '{selectedText}'")
    #                 popup.hide()
    #                 self.insertCompletion(selectedText + ' ')
    #                 popup.hide()
    #                 return
    #     eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
    #     super().keyPressEvent(event)
    #
    #     # Identify the prefix under the cursor
    #     prefix = self.textUnderCursor()
    #
    #     popup = self.completer.popup()
    #     # Trigger dynamic model update if the prefix is long enough
    #     if prefix:  # Set your minimum character threshold
    #         self.updateSuggestions(prefix)
    #
    #         # Synchronize completer with the new prefix
    #         self.completer.setCompletionPrefix(prefix)
    #
    #         # Select the first item
    #         firstIndex = self.completer.completionModel().index(0, 0)
    #         if firstIndex.isValid():
    #             popup.setCurrentIndex(firstIndex)
    #
    #         # Show the popup at the cursor position
    #         cr = self.cursorRect()
    #         cr.setWidth(popup.sizeHintForColumn(0) +
    #                     popup.verticalScrollBar().sizeHint().width())
    #         self.completer.complete(cr)
    #     else:
    #         popup.hide()

    # --------------------------------------------------------------------------
    def lineNumberAreaPaintEvent(self, event: QPaintEvent):
        painter = QPainter(self.lineNumberArea)
        painter.setFont(self.font())

        # graygd = QLinearGradient(0, 0, event.rect().width(), 0)
        # graygd.setColorAt(0.0, Qt.gray)
        # graygd.setColorAt(0.5, Qt.lightGray)
        # graygd.setColorAt(1.0, Qt.gray)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        # ----------------------------------------------------------------------
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(Qt.black)
                painter.drawText(3, top, self.lineNumberArea.width() - 3,
                                 self.fontMetrics().height(),
                                 Qt.AlignLeft, f"{blockNumber + 1}")

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    # --------------------------------------------------------------------------
    def lineNumberAreaWidth(self) -> int:
        digits: int = 2
        maxDigits: int = max(2, self.blockCount())
        while maxDigits >= 10:
            maxDigits /= 10
            digits += 1

        width: int = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return width

    # --------------------------------------------------------------------------
    def resizeEvent(self, e: QResizeEvent):
        super().resizeEvent(e)

        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            cr.right() - self.lineNumberAreaWidth(), cr.top(),
            self.lineNumberAreaWidth(), cr.height()
        )

    # --------------------------------------------------------------------------
    def updateLineNumberAreaWidth(self):
        self.setViewportMargins(0, 0, self.lineNumberAreaWidth(), 0)

    # --------------------------------------------------------------------------
    def highlightCurrentLine(self):
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            self.setExtraSelections([selection])

    # --------------------------------------------------------------------------
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth()

# ******************************************************************************
