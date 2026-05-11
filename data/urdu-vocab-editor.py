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
from PySide6.QtGui import (
    QFont, QTextOption, QSyntaxHighlighter, QTextCharFormat, QColor,
    QMouseEvent, QTextCursor, QAction
)
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMenuBar,
    QPlainTextEdit, QPushButton, QStatusBar, QTabWidget, QVBoxLayout, QWidget,
    QMainWindow, QFileDialog, QAbstractItemView, QMenu, QFrame, QLayout
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

    # words = [normalizeUrduChars(token.text.strip()) for token in doc if (isAlpha and token.is_alpha) and scriptScore(token.text) >= scoreThreshold]
    # words =
    # for token in doc:
    #     w = normalizeNonChars(normalizeUrduChars(token.text.strip()))
    #     if w and scriptScore(w) > 0.0:
    #         words.append(w)
    words = [normalizeWhiteSpace(normalizeNonChars(normalizeUrduChars(token.text.strip()))) for token in doc if scriptScore(token.text) > 0.0]
    words = [w for w in words if w]
    wordCount = len(words)

    vocab = Counter(words)

    return vocab, wordCount

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
    """
    Replaces presentation/positional forms with standard Urdu tokens
    using the built-in map function for performance.
    """
    if not text:
        return ""

    # Step 1: Handle Multi-character Ligatures
    # We use a regex for efficiency if the ligature list grows,
    # but for a small set, a simple loop or multiple .replace() works well.
    for ligature, replacement in LIGATURE_MAP.items():
        text = text.replace(ligature, replacement)

    # Step 2: Handle 1-to-1 Character Variants using map()
    # This cleans up positional forms (initial, medial, etc.)
    # map() applies the lambda to every character in the string.
    # .get(c, c) ensures we keep characters not in our dictionary (like spaces/punctuation).
    text = "".join(map(lambda c: URDU_REVERSAL_LOOKUP.get(c, c), text))

    return text

def removeMarks(text):
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

def removePunctuation(text):
    return "".join([c for c in text if not ud.category(c).startswith('P')])

def removeDigits(text):
    return "".join([c for c in text if not ud.category(c) == 'Nd'])

def normalizeNonChars(text):
    return removePunctuation(removeDigits(removeMarks(text)))

def normalizeWhiteSpace(text):
    return  " ".join(text.split())

# ******************************************************************************
def normalize2Urdu(token: str) -> str:
    """
    Standardizes Urdu tokens by:
    1. Mapping positional variants (Initial/Medial/Final forms) to base characters.
    2. Converting Arabic/Persian range characters to Urdu standard block.
    3. Removing diacritics and non-spacing marks.
    """
    if not token:
        return token

    # 1. Compatibility Decomposition (NFKC)
    # This automatically converts most positional variants (e.g., ﻒ, ﻘ, ﻂ)
    # from the Presentation Forms blocks to their standard Arabic script bases.
    token = ud.normalize('NFKC', token)

    # 2. Urdu-Specific Base Character Mapping
    # After NFKC, some chars might be in the 'Arabic' block (0643).
    # We must force them into the 'Urdu' preferred block.
    urduBaseMapping = {
        # Kaf variants
        '\u0643': '\u06a9', # Arabic Kaf -> Urdu Kaf
        '\u06a8': '\u06a9', # Swash Kaf -> Urdu Kaf

        # Yeh variants
        '\u064a': '\u06cc', # Arabic Yeh -> Urdu Chooti Yeh
        '\u0649': '\u06cc', # Alif Maqsura -> Urdu Chooti Yeh

        # Heh variants
        '\u0647': '\u06c1', # Arabic Heh -> Urdu Gol Heh
        '\u0629': '\u06c3', # Arabic Ta Marbuta -> Urdu Ta Marbuta

        # Zero-Width non-joiners (often used in positional variants)
        '\u200c': '',
    }

    for target, replacement in urduBaseMapping.items():
        token = token.replace(target, replacement)

    # 3. Selective Diacritic Removal (NFD)
    # We use NFD to isolate marks, then filter them out.
    # Marks to preserve:
    # U+0653 (Madda - for آ)
    # U+0654 (Hamza Above - for ئ / ؤ)
    preserved_marks = {'\u0653', '\u0654'}
    nfd_form = ud.normalize('NFD', token)
    token = "".join([c for c in nfd_form if not ud.combining(c) or c in preserved_marks])

    return ud.normalize('NFC', token)


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
        urduFont.setFamilies([u"Calibri"])
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
