# ******************************************************************************
# Copyright (C) 2026. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      Roximn <roximn148@gmail.com> Mar 2026
# ******************************************************************************
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import spacy
import unicodedataplus as ud
from pylatexenc.latex2text import LatexNodes2Text
from selectolax.parser import HTMLParser
from symspellpy import SymSpell, Verbosity
from PySide6.QtCore import (
    QMetaObject, QPoint, QRect, QSize, Qt, QRegularExpression, QEvent, Signal
)
from PySide6.QtGui import (
    QFont, QTextOption, QSyntaxHighlighter, QTextCharFormat, QColor,
    QMouseEvent, QTextCursor, QAction, QKeyEvent
)
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QLineEdit, QMenuBar,
    QPlainTextEdit, QPushButton, QStatusBar, QTabWidget, QVBoxLayout, QWidget,
    QMainWindow, QFileDialog, QMenu, QFrame, QLayout, QScrollArea, QGridLayout, QDockWidget
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

    ArabicVowels = "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652"
    for ch in token:
        script = ud.script(ch).upper() if ch not in ArabicVowels else 'ARABIC'
        if script in (targetScript, "INHERITED"):
            matchCount += 1

    return matchCount / len(token)


# ******************************************************************************
def preprocessXml(xmlContent):
    root = ET.fromstring(xmlContent)
    texts = [elem.text for elem in root.iter() if elem.text]
    print(len(texts))
    return " ".join(texts)


# ******************************************************************************
def preprocessHtml(htmlContent):
    tree = HTMLParser(htmlContent)
    for tag in tree.css('script, style'):
        tag.decompose()
    return tree.body.text(separator=' ', strip=True)


# ******************************************************************************
def preprocessLatex(latexContent):
    textCleaner = LatexNodes2Text()
    return textCleaner.latex_to_text(latexContent)


# ******************************************************************************
URDU_VARIANT_MAP = {
    # ALIF (ا)
    '\u0627': [
        '\u0627',  # ARABIC LETTER ALIF
        '\uFE8D',  # ARABIC LETTER ALIF ISOLATED FORM
        '\uFE8E',  # ARABIC LETTER ALIF FINAL FORM
    ],
    # ALEF MADDA (آ)
    '\u0622': [
        '\u0622',  # ARABIC LETTER ALEF WITH MADDA ABOVE
        '\uFE81',  # ALEF WITH MADDA ABOVE ISOLATED FORM
        '\uFE82',  # ALEF WITH MADDA ABOVE FINAL FORM
    ],
    # BE (ب)
    '\u0628': [
        '\u0628',  # ARABIC LETTER BE
        '\uFE8F',  # ARABIC LETTER BE ISOLATED FORM
        '\uFE90',  # ARABIC LETTER BE FINAL FORM
        '\uFE91',  # ARABIC LETTER BE INITIAL FORM
        '\uFE92',  # ARABIC LETTER BE MEDIAL FORM
    ],
    # PE (پ)
    '\u067E': [
        '\u067E',  # ARABIC LETTER PE
        '\uFB56',  # ARABIC LETTER PE ISOLATED FORM
        '\uFB57',  # ARABIC LETTER PE FINAL FORM
        '\uFB58',  # ARABIC LETTER PE INITIAL FORM
        '\uFB59',  # ARABIC LETTER PE MEDIAL FORM
    ],
    # TE (ت)
    '\u062A': [
        '\u062A',  # ARABIC LETTER TE
        '\uFE95',  # ARABIC LETTER TE ISOLATED FORM
        '\uFE96',  # ARABIC LETTER TE FINAL FORM
        '\uFE97',  # ARABIC LETTER TE INITIAL FORM
        '\uFE98',  # ARABIC LETTER TE MEDIAL FORM
    ],
    # TTE (ٹ)
    '\u0679': [
        '\u0679',  # ARABIC LETTER TTE
        '\uFB66',  # ARABIC LETTER TTE ISOLATED FORM
        '\uFB67',  # ARABIC LETTER TTE FINAL FORM
        '\uFB68',  # ARABIC LETTER TTE INITIAL FORM
        '\uFB69',  # ARABIC LETTER TTE MEDIAL FORM
    ],
    # SE (ث)
    '\u062B': [
        '\u062B',  # ARABIC LETTER THE
        '\uFE99',  # ARABIC LETTER THE ISOLATED FORM
        '\uFE9A',  # ARABIC LETTER THE FINAL FORM
        '\uFE9B',  # ARABIC LETTER THE INITIAL FORM
        '\uFE9C',  # ARABIC LETTER THE MEDIAL FORM
    ],
    # JEEM (ج)
    '\u062C': [
        '\u062C',  # ARABIC LETTER JEEM
        '\uFE9D',  # ARABIC LETTER JEEM ISOLATED FORM
        '\uFE9E',  # ARABIC LETTER JEEM FINAL FORM
        '\uFE9F',  # ARABIC LETTER JEEM INITIAL FORM
        '\uFEA0',  # ARABIC LETTER JEEM MEDIAL FORM
    ],
    # CHE (چ)
    '\u0686': [
        '\u0686',  # ARABIC LETTER CHE
        '\uFB7A',  # ARABIC LETTER CHE ISOLATED FORM
        '\uFB7B',  # ARABIC LETTER CHE FINAL FORM
        '\uFB7C',  # ARABIC LETTER CHE INITIAL FORM
        '\uFB7D',  # ARABIC LETTER CHE MEDIAL FORM
    ],
    # BARI HE (ح)
    '\u062D': [
        '\u062D',  # ARABIC LETTER HAA
        '\uFEA1',  # ARABIC LETTER HAA ISOLATED FORM
        '\uFEA2',  # ARABIC LETTER HAA FINAL FORM
        '\uFEA3',  # ARABIC LETTER HAA INITIAL FORM
        '\uFEA4',  # ARABIC LETTER HAA MEDIAL FORM
    ],
    # KHE (خ)
    '\u062E': [
        '\u062E',  # ARABIC LETTER KHAA
        '\uFEA5',  # ARABIC LETTER KHAA ISOLATED FORM
        '\uFEA6',  # ARABIC LETTER KHAA FINAL FORM
        '\uFEA7',  # ARABIC LETTER KHAA INITIAL FORM
        '\uFEA8',  # ARABIC LETTER KHAA MEDIAL FORM
    ],
    # DAL (د)
    '\u062F': [
        '\u062F',  # ARABIC LETTER DAL
        '\uFEA9',  # ARABIC LETTER DAL ISOLATED FORM
        '\uFEAA',  # ARABIC LETTER DAL FINAL FORM
    ],
    # DDAL (ڈ)
    '\u0688': [
        '\u0688',  # ARABIC LETTER DDAL
        '\uFB88',  # ARABIC LETTER DDAL ISOLATED FORM
        '\uFB89',  # ARABIC LETTER DDAL FINAL FORM
    ],
    # ZAL (ذ)
    '\u0630': [
        '\u0630',  # ARABIC LETTER THAL
        '\uFEAB',  # ARABIC LETTER THAL ISOLATED FORM
        '\uFEAC',  # ARABIC LETTER THAL FINAL FORM
    ],
    # RE (ر)
    '\u0631': [
        '\u0631',  # ARABIC LETTER REH
        '\uFEAD',  # ARABIC LETTER REH ISOLATED FORM
        '\uFEAE',  # ARABIC LETTER REH FINAL FORM
    ],
    # RRE (ڑ)
    '\u0691': [
        '\u0691',  # ARABIC LETTER RREH
        '\uFB8C',  # ARABIC LETTER RREH ISOLATED FORM
        '\uFB8D',  # ARABIC LETTER RREH FINAL FORM
    ],
    # ZE (ز)
    '\u0632': [
        '\u0632',  # ARABIC LETTER ZAIN
        '\uFEAF',  # ARABIC LETTER ZAIN ISOLATED FORM
        '\uFEB0',  # ARABIC LETTER ZAIN FINAL FORM
    ],
    # ZHE (ژ)
    '\u0698': [
        '\u0698',  # ARABIC LETTER JEH
        '\uFB8A',  # ARABIC LETTER JEH ISOLATED FORM
        '\uFB8B',  # ARABIC LETTER JEH FINAL FORM
    ],
    # SEEN (س)
    '\u0633': [
        '\u0633',  # ARABIC LETTER SEEN
        '\uFEB1',  # ARABIC LETTER SEEN ISOLATED FORM
        '\uFEB2',  # ARABIC LETTER SEEN FINAL FORM
        '\uFEB3',  # ARABIC LETTER SEEN INITIAL FORM
        '\uFEB4',  # ARABIC LETTER SEEN MEDIAL FORM
    ],
    # SHEEN (ش)
    '\u0634': [
        '\u0634',  # ARABIC LETTER SHEEN
        '\uFEB5',  # ARABIC LETTER SHEEN ISOLATED FORM
        '\uFEB6',  # ARABIC LETTER SHEEN FINAL FORM
        '\uFEB7',  # ARABIC LETTER SHEEN INITIAL FORM
        '\uFEB8',  # ARABIC LETTER SHEEN MEDIAL FORM
    ],
    # SUAD (ص)
    '\u0635': [
        '\u0635',  # ARABIC LETTER SAD
        '\uFEB9',  # ARABIC LETTER SAD ISOLATED FORM
        '\uFEBA',  # ARABIC LETTER SAD FINAL FORM
        '\uFEBB',  # ARABIC LETTER SAD INITIAL FORM
        '\uFEBC',  # ARABIC LETTER SAD MEDIAL FORM
    ],
    # ZUAD (ض)
    '\u0636': [
        '\u0636',  # ARABIC LETTER DAD
        '\uFEBD',  # ARABIC LETTER DAD ISOLATED FORM
        '\uFEBE',  # ARABIC LETTER DAD FINAL FORM
        '\uFEBF',  # ARABIC LETTER DAD INITIAL FORM
        '\uFEC0',  # ARABIC LETTER DAD MEDIAL FORM
    ],
    # TO'E (ط)
    '\u0637': [
        '\u0637',  # ARABIC LETTER TAH
        '\uFEC1',  # ARABIC LETTER TAH ISOLATED FORM
        '\uFEC2',  # ARABIC LETTER TAH FINAL FORM
        '\uFEC3',  # ARABIC LETTER TAH INITIAL FORM
        '\uFEC4',  # ARABIC LETTER TAH MEDIAL FORM
    ],
    # ZO'E (ظ)
    '\u0638': [
        '\u0638',  # ARABIC LETTER ZAH
        '\uFEC5',  # ARABIC LETTER ZAH ISOLATED FORM
        '\uFEC6',  # ARABIC LETTER ZAH FINAL FORM
        '\uFEC7',  # ARABIC LETTER ZAH INITIAL FORM
        '\uFEC8',  # ARABIC LETTER ZAH MEDIAL FORM
    ],
    # AIN (ع)
    '\u0639': [
        '\u0639',  # ARABIC LETTER AIN
        '\uFEC9',  # ARABIC LETTER AIN ISOLATED FORM
        '\uFECA',  # ARABIC LETTER AIN FINAL FORM
        '\uFECB',  # ARABIC LETTER AIN INITIAL FORM
        '\uFECC',  # ARABIC LETTER AIN MEDIAL FORM
    ],
    # GHAIN (غ)
    '\u063A': [
        '\u063A',  # ARABIC LETTER GHAIN
        '\uFECD',  # ARABIC LETTER GHAIN ISOLATED FORM
        '\uFECE',  # ARABIC LETTER GHAIN FINAL FORM
        '\uFECF',  # ARABIC LETTER GHAIN INITIAL FORM
        '\uFED0',  # ARABIC LETTER GHAIN MEDIAL FORM
    ],
    # FE (ف)
    '\u0641': [
        '\u0641',  # ARABIC LETTER FE
        '\uFED1',  # ARABIC LETTER FE ISOLATED FORM
        '\uFED2',  # ARABIC LETTER FE FINAL FORM
        '\uFED3',  # ARABIC LETTER FE INITIAL FORM
        '\uFED4',  # ARABIC LETTER FE MEDIAL FORM
    ],
    # QAF (ق)
    '\u0642': [
        '\u0642',  # ARABIC LETTER QAF
        '\uFED5',  # ARABIC LETTER QAF ISOLATED FORM
        '\uFED6',  # ARABIC LETTER QAF FINAL FORM
        '\uFED7',  # ARABIC LETTER QAF INITIAL FORM
        '\uFED8',  # ARABIC LETTER QAF MEDIAL FORM
    ],
    # URDU KAF (ک)
    '\u06A9': [
        # Urdu/Persian Keheh (ک)
        '\u06A9',  # ARABIC LETTER KEHEH
        '\uFB8E',  # ARABIC LETTER KEHEH ISOLATED FORM
        '\uFB8F',  # ARABIC LETTER KEHEH FINAL FORM
        '\uFB90',  # ARABIC LETTER KEHEH INITIAL FORM
        '\uFB91',  # ARABIC LETTER KEHEH MEDIAL FORM
        # Arabic Kaf (ك)
        '\u0643',  # ARABIC LETTER KAF
        '\uFED9',  # ARABIC LETTER KAF ISOLATED FORM
        '\uFEDA',  # ARABIC LETTER KAF FINAL FORM
        '\uFEDB',  # ARABIC LETTER KAF INITIAL FORM
        '\uFEDC',  # ARABIC LETTER KAF MEDIAL FORM
        # Old Persian / Swash Kaf (ݢ)
        '\u06A8',  # ARABIC LETTER KAF WITH TWO DOTS ABOVE
        '\uFB96',  # ARABIC LETTER KAF WITH TWO DOTS ABOVE ISOLATED FORM
        '\uFB97',  # ARABIC LETTER KAF WITH TWO DOTS ABOVE FINAL FORM
        '\uFB98',  # ARABIC LETTER KAF WITH TWO DOTS ABOVE INITIAL FORM
        '\uFB99',  # ARABIC LETTER KAF WITH TWO DOTS ABOVE MEDIAL FORM
    ],
    # GAF (گ)
    '\u06AF': [
        '\u06AF',  # ARABIC LETTER GAF
        '\uFB92',  # ARABIC LETTER GAF ISOLATED FORM
        '\uFB93',  # ARABIC LETTER GAF FINAL FORM
        '\uFB94',  # ARABIC LETTER GAF INITIAL FORM
        '\uFB95',  # ARABIC LETTER GAF MEDIAL FORM
    ],
    # LAM (ل)
    '\u0644': [
        '\u0644',  # ARABIC LETTER LAM
        '\uFEDD',  # ARABIC LETTER LAM ISOLATED FORM
        '\uFEDE',  # ARABIC LETTER LAM FINAL FORM
        '\uFEDF',  # ARABIC LETTER LAM INITIAL FORM
        '\uFEE0',  # ARABIC LETTER LAM MEDIAL FORM
    ],
    # MEEM (م)
    '\u0645': [
        '\u0645',  # ARABIC LETTER MEEM
        '\uFEE1',  # ARABIC LETTER MEEM ISOLATED FORM
        '\uFEE2',  # ARABIC LETTER MEEM FINAL FORM
        '\uFEE3',  # ARABIC LETTER MEEM INITIAL FORM
        '\uFEE4',  # ARABIC LETTER MEEM MEDIAL FORM
    ],
    # NOON (ن)
    '\u0646': [
        '\u0646',  # ARABIC LETTER NOON
        '\uFEE5',  # ARABIC LETTER NOON ISOLATED FORM
        '\uFEE6',  # ARABIC LETTER NOON FINAL FORM
        '\uFEE7',  # ARABIC LETTER NOON INITIAL FORM
        '\uFEE8',  # ARABIC LETTER NOON MEDIAL FORM
    ],
    # NOON GHUNNA (ں)
    '\u06BA': [
        '\u06BA',  # ARABIC LETTER NOON GHUNNA
        '\uFB9E',  # ARABIC LETTER NOON GHUNNA ISOLATED FORM
        '\uFB9F',  # ARABIC LETTER NOON GHUNNA FINAL FORM
    ],
    # WAO (و)
    '\u0648': [
        # Standard Wao
        '\u0648',  # ARABIC LETTER WAW
        '\uFEED',  # ARABIC LETTER WAW ISOLATED FORM
        '\uFEEE',  # ARABIC LETTER WAW FINAL FORM
        # Wao with Hamza (ؤ)
        '\u0624',  # ARABIC LETTER WAW WITH HAMZA ABOVE
        '\uFE85',  # ARABIC LETTER WAW WITH HAMZA ABOVE ISOLATED FORM
        '\uFE86',  # ARABIC LETTER WAW WITH HAMZA ABOVE FINAL FORM
    ],
    # HE GOAL (ہ)
    '\u06C1': [
        # Urdu Heh Goal (ہ)
        '\u06C1',  # ARABIC LETTER HEH GOAL
        '\uFBA6',  # ARABIC LETTER HEH GOAL ISOLATED FORM
        '\uFBA7',  # ARABIC LETTER HEH GOAL FINAL FORM
        '\uFBA8',  # ARABIC LETTER HEH GOAL INITIAL FORM
        '\uFBA9',  # ARABIC LETTER HEH GOAL MEDIAL FORM
        # Arabic Ha (ه)
        '\u0647',  # ARABIC LETTER HEH
        '\uFEE9',  # ARABIC LETTER HEH ISOLATED FORM
        '\uFEEA',  # ARABIC LETTER HEH FINAL FORM
        '\uFEEB',  # ARABIC LETTER HEH INITIAL FORM
        '\uFEEC',  # ARABIC LETTER HEH MEDIAL FORM
        # Heh with Hamza variants (ۂ)
        '\u06C2',  # ARABIC LETTER HEH GOAL WITH HAMZA ABOVE
        '\u06C0',  # ARABIC LETTER HEH WITH YEH ABOVE
        # Te Marbuta (ة)
        '\u0629',  # ARABIC LETTER TE MARBUTA
        '\uFE93',  # ARABIC LETTER TE MARBUTA ISOLATED FORM
        '\uFE94',  # ARABIC LETTER TE MARBUTA FINAL FORM
    ],
    # DO CHASHMI HE (ھ)
    '\u06BE': [
        '\u06BE',  # ARABIC LETTER HEH DOACHASHMEE
        '\uFBAC',  # ARABIC LETTER HEH DOACHASHMEE ISOLATED FORM
        '\uFBAD',  # ARABIC LETTER HEH DOACHASHMEE FINAL FORM
        '\uFBAE',  # ARABIC LETTER HEH DOACHASHMEE INITIAL FORM
        '\uFBAF',  # ARABIC LETTER HEH DOACHASHMEE MEDIAL FORM
    ],
    # CHOTI YE / FARSI YEH / ARABIC YEH (ی / ي)
    '\u06CC': [
        # Urdu/Farsi Standard (ی)
        '\u06CC',  # ARABIC LETTER FARSI YEH
        '\uFBFB',  # ARABIC LETTER FARSI YEH ISOLATED FORM
        '\uFBFC',  # ARABIC LETTER FARSI YEH FINAL FORM
        '\uFBFD',  # ARABIC LETTER FARSI YEH INITIAL FORM
        '\uFBFE',  # ARABIC LETTER FARSI YEH MEDIAL FORM
        # Arabic/Sindhi Standard (ي)
        '\u064A',  # ARABIC LETTER YEH
        '\uFEF1',  # ARABIC LETTER YEH ISOLATED FORM
        '\uFEF2',  # ARABIC LETTER YEH FINAL FORM
        '\uFEF3',  # ARABIC LETTER YEH INITIAL FORM
        '\uFEF4',  # ARABIC LETTER YEH MEDIAL FORM
        # Alef Maksura (ى)
        '\u0649',  # ARABIC LETTER ALEF MAKSURA
        '\uEEF1',  # ARABIC LETTER ALEF MAKSURA ISOLATED FORM
        '\uEEF2',  # ARABIC LETTER ALEF MAKSURA FINAL FORM
    ],
    '\u0626': [ # Yeh with Hamza (ئ) - Common compositional variant
        '\u0626',  # ARABIC LETTER YEH WITH HAMZA ABOVE
        '\uFE8B',  # ARABIC LETTER YEH WITH HAMZA ABOVE INITIAL FORM
        '\uFE8C',  # ARABIC LETTER YEH WITH HAMZA ABOVE MEDIAL FORM
        '\uFE89',  # ARABIC LETTER YEH WITH HAMZA ABOVE ISOLATED FORM
        '\uFE8A',  # ARABIC LETTER YEH WITH HAMZA ABOVE FINAL FORM
    ],
    # BARI YE (ے)
    '\u06D2': [
        '\u06D2',  # ARABIC LETTER YEH BARREE
        '\uFBAE',  # ARABIC LETTER YEH BARREE ISOLATED FORM
        '\uFBAF',  # ARABIC LETTER YEH BARREE FINAL FORM
        '\u06D3',  # ARABIC LETTER YEH BARREE WITH HAMZA ABOVE
    ],
    # KASHEEDA / TATWEEL (ـ)
    # Mapping to empty string is a common way to 'strip' it during normalization
    '': [
        '\u0640',  # ARABIC TATWEEL
    ],
}

LIGATURE_MAP = {
    '\uFEFB': '\u0644\u0627',  # LAM WITH ALEF ISOLATED -> ل + ا
    '\uFEFC': '\u0644\u0627',  # LAM WITH ALEF FINAL -> ل + ا
    '\uFEF5': '\u0644\u0622',  # LAM WITH ALEF MADDA ISOLATED -> ل + آ
    '\uFEF6': '\u0644\u0622',  # LAM WITH ALEF MADDA FINAL -> ل + آ
}

URDU_REVERSAL_LOOKUP = {v: base for base, variants in URDU_VARIANT_MAP.items() for v in variants}

def normalizeUrduChars(text):
    """Replaces ligatures, presentation, positional and some compositional forms with base Urdu characters"""
    if not text:
        return ""

    # Step 1: Handle Multi-character Ligatures
    for ligature, replacement in LIGATURE_MAP.items():
        text = text.replace(ligature, replacement)

    # Step 2: Handle 1-to-1 Character Variants using map()
    # This cleans up positional forms (initial, medial, etc.)
    # map() applies the lambda to every character in the string.
    # .get(c, c) ensures we keep characters not in our dictionary (like spaces/punctuation).
    text = "".join(map(lambda c: URDU_REVERSAL_LOOKUP.get(c, c), text))

    return text

def removeMarks(text):
    """Remove all diacritical marks, identified using Unicode classification"""
    # Selective Diacritic Removal (NFD)
    # NFD is used to isolate marks, then filter them out.
    # Marks to preserve:
    # * U+0653 (Madda - for آ)
    # * U+0654 (Hamza Above - for ئ),
    # other base characters are filtered by character normalization
    preservedMarks = {'\u0653', '\u0654'}
    nfdForm = ud.normalize('NFD', text)
    token = "".join([c for c in nfdForm if c in preservedMarks or not ud.combining(c)])
    return ud.normalize('NFC', token)

def isPunctuation(char):
    return ud.category(char).startswith('P')

def removePunctuation(text):
    return "".join([c for c in text if not isPunctuation(c)])

def isDigit(char):
    return ud.category(char) == 'Nd'

def removeDigits(text):
    return "".join([c for c in text if not isDigit(c)])

def normalizeNonChars(text):
    return removePunctuation(removeDigits(removeMarks(text)))

def normalizeWhiteSpace(text):
    return  " ".join(text.split())

def normalize(text):
    return normalizeWhiteSpace(normalizeNonChars(normalizeUrduChars(text)))


# ******************************************************************************
class Vocabulary():
    def __init__(self, referenceVocabulary=None, sep='$'):
        self.symSpell = SymSpell()
        if referenceVocabulary:
            self.loadReference(referenceVocabulary, sep)
        self.vocab = Counter()

    def loadReference(self, filename, sep='$'):
        self.symSpell.load_dictionary(filename, 0, 1, separator=sep, encoding='utf8')

    def exists(self, word):
        """Check if word exists in reference vocabulary"""
        suggestions = self.symSpell.lookup(word, Verbosity.CLOSEST, max_edit_distance=0)
        return len(suggestions) > 0

    def suggest(self, word, distance=1):
        """Get suggestions from reference vocabulary"""
        return self.symSpell.lookup(word, Verbosity.CLOSEST, max_edit_distance=distance)

    def extract(self, text, filterKnown=True):
        """Extract word-frequency pairs from given text"""
        def cleanToken(token):
            txt = token.text
            if scriptScore(txt) == 0.0:
                return ''
            txt = normalize(txt)
            return txt

        nlp = spacy.blank('ur')
        doc = nlp(text)
        words = [cleanToken(token) for token in doc]
        words = list(filter(None, words))
        words = [w for w in words if filterKnown and not self.exists(w)]
        self.vocab.update(Counter(words))

    @property
    def words(self):
        return [w for w, f in self.vocab.most_common()]

    def save(self, filename, sep='$'):
        """Saves word-frequency pairs to a SymSpell file"""
        with open(filename, "w", encoding="utf-8") as sym:
            for i, (w, f) in enumerate(self.vocab.most_common()):
                sym.write(f"{w}{sep}{f}\n")

    def load(self, filename, sep='$'):
        """Loads word-frequency pairs from a SymSpell file"""
        counter = Counter()
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    # Split by the specific '$' delimiter
                    word, freq = line.rsplit(sep, 1)
                    counter[word] = int(freq)
        self.vocab = counter


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

        self.dictionary: Vocabulary | None = None

        doc = self.document()
        option = doc.defaultTextOption()
        option.setTextDirection(Qt.RightToLeft)
        option.setAlignment(Qt.AlignRight)
        option.setFlags(QTextOption.ShowTabsAndSpaces)
        doc.setDefaultTextOption(option)
        self.sourceHighlighter = WordsHighlighter(doc)

    def setDict(self, dictionary: Vocabulary | None):
        self.dictionary = dictionary
        self.sourceHighlighter.setDict(self.dictionary)

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
            if self.dictionary is not None:
                token = self.textCursor().selectedText()
                word = normalize(token)
                suggestions = self.dictionary.suggest(word, distance=2)
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
        self.errorFormat.setUnderlineColor(Qt.red)
        self.errorFormat.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

        self.symSpell = SymSpell()

        self.dictionary: Vocabulary | None = None

    def setDict(self, dictionary: Vocabulary | None):
        self.dictionary = dictionary

    def highlightBlock(self, text):
        # Match and apply color to the visible whitespace symbols
        matches = self.whitespacePattern.globalMatch(text)
        while matches.hasNext():
            match = matches.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.whiteSpceFormat)

        if self.dictionary is None:
            return

        nlp = spacy.blank('ur')
        doc = nlp(text)
        for token in doc:
            word = normalize(token.text)

            # Skip
            if self.dictionary.exists(word):
                continue
            if all(isPunctuation(char) for char in word):
                continue

            self.setFormat(token.idx, len(token), self.errorFormat)

# ******************************************************************************
class Ui_MainWindow(object):
    # --------------------------------------------------------------------------
    def setupUi(self, parentWindow):
        parentWindow.setObjectName(u"LafzShanaasWindow")
        parentWindow.setWindowTitle("Lafz Shanaas")
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
        urduFont.setFamilies([u"Calibri"])
        urduFont.setPointSize(32)
        self.tbxSourceText.setFont(urduFont)

        self.verticalLayout.addWidget(self.tbxSourceText, stretch=3)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.lstWords = VocabCloud(self.tbNew)
        self.lstWords.setObjectName(u"lstWords")
        # self.lstWords = QListWidget(self.tbNew)
        # self.lstWords.setObjectName(u"lstWords")
        # self.lstWords.setFont(urduFont)
        # self.lstWords.setLayoutDirection(Qt.RightToLeft)
        # self.lstWords.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.lstWords.setAlternatingRowColors(True)
        # self.lstWords.setStyleSheet("""
        #     QListWidget { outline: 0; }
        #     QListWidget::item:selected {
        #         background-color: #888;
        #     }
        #     QListWidget::item:hover {
        #         background-color: #CCC;
        #         color: #fff;
        #     }
        # """)

        self.scrollArea.setWidget(self.lstWords)
        self.verticalLayout.addWidget(self.scrollArea, stretch=1)

        self.tcWordComposition = TagCloud(self.tbNew)
        self.tcWordComposition.setObjectName(u"tcWordComposition")

        self.verticalLayout.addWidget(self.tcWordComposition, stretch=0)

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
class UrduKeyboardDock(QDockWidget):
    # Signal to send the character to the receiver
    charClicked = Signal(str)
    ctrlClicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__("Urdu Keyboard", parent)

        self.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetMovable)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addStretch()

        # Urdu alphabet in alphabetical order
        alphabet = [
            "\u0627", "\u0628", "\u067e", "\u062a", "\u0679", "\u062b", "\u062c", "\u0686", "\u062d", "\u062e",
            "\u062f", "\u0688", "\u0630", "\u0631", "\u0691", "\u0632", "\u0698", "\u0633", "\u0634", "\u0635",
            "\u0636", "\u0637", "\u0638", "\u0639", "\u063a", "\u0641", "\u0642", "\u06a9", "\u06af", "\u0644",
            "\u0645", "\u0646", "\u0648", "\u06c1", "\u06be", "\u0621", "\u06cc", "\u0626", "\u06d2"
        ]

        alphaGrid = QGridLayout()
        # Arrange in 3 rows (approx 13 columns per row)
        COLUMNS_PER_ROW = 13
        for index, char in enumerate(alphabet):
            row = index // COLUMNS_PER_ROW
            # add buttons RTL in a row
            col = (COLUMNS_PER_ROW - 1) - (index % COLUMNS_PER_ROW)
            btn = self.createButton(char, isChar=True)
            alphaGrid.addWidget(btn, row, col)

        layout.addLayout(alphaGrid)
        layout.addSpacing(45)

        ctrlGrid = QGridLayout()
        controls = [
            ("Del", "delete"), ("Bksp", "backspace"),
            ("Home", "home"), ("End", "end"),
            ("\u2190", "left"), ("\u2192", "right"),
        ]

        for index, (label, action) in enumerate(controls):
            row = index // 2
            col = index % 2
            btn = self.createButton(label, isChar=False)
            btn.clicked.connect(lambda checked=False, a=action: self.ctrlClicked.emit(a))
            ctrlGrid.addWidget(btn, row, col)

        layout.addLayout(ctrlGrid)
        layout.addStretch()

        self.setWidget(container)

    def onButtonClick(self, char):
        self.charClicked.emit(char)

    def createButton(self, text, isChar=True):
        btn = QPushButton(text)
        btn.setFocusPolicy(Qt.NoFocus)
        if isChar:
            btn.setFixedSize(45, 45)
        else:
            btn.setFixedSize(60, 45) # Slightly wider for text labels

        # Visual style
        bg_color = "#ffffff" if isChar else "#e1e1e1"
        font_size = 20 if isChar else 12
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: {font_size}px; font-family: 'Calibri', Arial;
                background-color: {bg_color}; border: 1px solid #bdc3c7; border-radius: 5px;
            }}
            QPushButton:hover {{ background-color: #ecf0f1; }}
            QPushButton:pressed {{ background-color: #dcdde1; }}
        """)

        if isChar:
            btn.clicked.connect(lambda checked=False, t=text: self.charClicked.emit(t))
        return btn


# ******************************************************************************
class MainWindow(QMainWindow):
    # --------------------------------------------------------------------------
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.vocabulary = Vocabulary()
        self.ui.tbxSourceText.setDict(self.vocabulary)

        self.setStyleSheet("""
            #Tag { background-color: #e1e4e8; border-radius: 4px; border: 1px solid #ccc; }
            #Tag:hover { background-color: #d1d5da; }
        """)

        self.ui.btnSelectSource.clicked.connect(self.onOpenFile)
        self.ui.lstWords.selectionChanged.connect(self.onSelectionChanged)

        self.keyboard = UrduKeyboardDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.keyboard)
        self.keyboard.charClicked.connect(self.ui.tcWordComposition.inputField.insert)
        self.keyboard.ctrlClicked.connect(self.handleKeyboardControls)
        self.keyboard.setVisible(True)

    # ******************************************************************************
    def handleKeyboardControls(self, action):
        le = self.ui.tcWordComposition.inputField
        if action == "backspace": le.backspace()
        elif action == "delete": le.del_()
        elif action == "left": le.setCursorPosition(le.cursorPosition() + 1)
        elif action == "right": le.setCursorPosition(le.cursorPosition() - 1)
        elif action == "home": le.home(False)
        elif action == "end": le.end(False)

    # ******************************************************************************
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_F1:
            isVisible = self.keyboard.isVisible()
            self.keyboard.setVisible(not isVisible)
        else:
            super().keyPressEvent(event)


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
    def onSelectionChanged(self, text):
        if text:
            self.ui.tcWordComposition.inputField.setText(text)

    # ******************************************************************************
    def loadInputFile(self, filePath):
        assert filePath is not None
        assert type(filePath) == str
        sourceFilePath = Path(filePath)
        assert sourceFilePath.exists(), "Source file does not exist"

        PREPROCESSORS = {
            ".xml": preprocessXml,
            ".tex": preprocessLatex,
            ".html": preprocessHtml,
            ".htm": preprocessHtml,
        }

        # Load source text and trim to tokenizer limit
        ext = sourceFilePath.suffix.lower()
        rawContent = sourceFilePath.read_text(encoding='utf-8-sig')
        sourceTxt = PREPROCESSORS[ext](rawContent) if ext in PREPROCESSORS else rawContent

        if len(sourceTxt) > 1_000_000:
            sourceTxt = sourceTxt[:1_000_000]
            print("Trimming input text size to 1,000,000")

        self.vocabulary.extract(sourceTxt)

        # Update UI
        self.ui.leSourceFile.setText(filePath)
        self.ui.tbxSourceText.setPlainText(rawContent)
        self.ui.lstWords.clearTags()
        self.ui.lstWords.addTags(self.vocabulary.words)
        self.ui.tcWordComposition.inputField.clear()

# Read a text file.
# Tokenize the contents.
# Extract all Urdu words.
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


# ******************************************************************************
class TagWidget(QFrame):
    """Single tag bubble with a remove button."""

    # --------------------------------------------------------------------------
    clicked = Signal(str)

    # --------------------------------------------------------------------------
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setObjectName("Tag")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)

        self.label = QLabel(text)
        urduFont = QFont()
        urduFont.setFamilies(["Noto Naskh Arabic", "Noto Sans"])
        urduFont.setPointSize(12)
        self.label.setFont(urduFont)

        layout.addWidget(self.label)

    # --------------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.label.text())
        super().mousePressEvent(event)


# ******************************************************************************
class VocabCloud(QWidget):
    """Main container with word cloud."""
    # --------------------------------------------------------------------------
    selectionChanged = Signal(str)

    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)

        mainLayout = QVBoxLayout(self)
        self.label = QLabel()
        self.label.setLayoutDirection(Qt.RightToLeft)
        self.label.setAlignment(Qt.AlignRight)

        self.container = QWidget()
        self.container.setLayoutDirection(Qt.RightToLeft)
        self.flowLayout = FlowLayout(self.container)
        self.flowLayout.setSpacing(8)

        mainLayout.addWidget(self.label)
        mainLayout.addWidget(self.container)
        mainLayout.addStretch()

    # --------------------------------------------------------------------------
    def addTags(self, words):
        if words:
            self.clearTags(self.flowLayout)
            for word in words:
                widget = TagWidget(word)
                widget.clicked.connect(self.onTagClicked)

                self.flowLayout.addWidget(widget)

        self.label.setText(f"Count: {self.flowLayout.count()}")

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

        self.label.setText(f"Count: {self.flowLayout.count()}")

    # --------------------------------------------------------------------------
    def onTagClicked(self, text):
        self.selectionChanged.emit(text)


# ******************************************************************************
class ReadOnlyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setLayoutDirection(Qt.RightToLeft)

    def keyPressEvent(self, event):
        event.ignore()


# ******************************************************************************
class TagCloud(QWidget):
    """Main container with input and cloud."""
    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        mainLayout = QVBoxLayout(self)
        self.inputField = ReadOnlyLineEdit()
        urduFont = QFont()
        urduFont.setFamilies(["Noto Naskh Arabic", "Noto Sans"])
        urduFont.setPointSize(18)
        self.inputField.setFont(urduFont)
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
                uniCategory = ud.category(ch)
                widget.setToolTip(f"{ud.name(ch, 'NDEF')} [{uniCategory}]")
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
