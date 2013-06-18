//*****************************************************************************
#include <QPainter>
#include <QTextBlock>

#include <QFile>
#include <QTextStream>
#include <QTextCodec>
#include <QStringList>
#include <QDebug>

//*****************************************************************************
#include "mltexteditor.h"
#include "hunspell.hxx"

//*****************************************************************************
mlTextEditor::mlTextEditor(QWidget *parent) : QPlainTextEdit(parent) {

    m_lineNumberArea = new mlLineNumberArea(this);
    m_highlighter = new mlHighlighter(document());

    QTextOption op = document()->defaultTextOption();
    op.setFlags( op.flags() | QTextOption::ShowTabsAndSpaces );
    document()->setDefaultTextOption( op );

    connect(this, SIGNAL(blockCountChanged(int)), this, SLOT(updateLineNumberAreaWidth(int)));
    connect(this, SIGNAL(updateRequest(QRect,int)), this, SLOT(updateLineNumberArea(QRect,int)));
    connect(this, SIGNAL(cursorPositionChanged()), this, SLOT(highlightCurrentLine()));

    updateLineNumberAreaWidth(0);
    highlightCurrentLine();
}

//*****************************************************************************
int mlTextEditor::lineNumberAreaWidth() {
    int digits = 2;
    int max = qMax(2, blockCount());
    while (max >= 10) {
        max /= 10;
        ++digits;
    }

    int space = 3 + fontMetrics().width(QLatin1Char('9')) * digits;

    return space;
}

//*****************************************************************************
void mlTextEditor::updateLineNumberAreaWidth(int /* newBlockCount */) {
    setViewportMargins(lineNumberAreaWidth(), 0, 0, 0);
}

//*****************************************************************************
void mlTextEditor::updateLineNumberArea(const QRect &rect, int dy) {
    if (dy)
        m_lineNumberArea->scroll(0, dy);
    else
        m_lineNumberArea->update(0, rect.y(), m_lineNumberArea->width(), rect.height());

    if (rect.contains(viewport()->rect()))
        updateLineNumberAreaWidth(0);
}

//*****************************************************************************
void mlTextEditor::resizeEvent(QResizeEvent *e) {
    QPlainTextEdit::resizeEvent(e);

    QRect cr = contentsRect();
    m_lineNumberArea->setGeometry(QRect(cr.left(), cr.top(), lineNumberAreaWidth(), cr.height()));
}

//*****************************************************************************
void mlTextEditor::highlightCurrentLine() {
    QList<QTextEdit::ExtraSelection> extraSelections;

    if (!isReadOnly()) {
        QTextEdit::ExtraSelection selection;

        QColor lineColor = QColor(Qt::yellow).lighter(160);

        selection.format.setBackground(lineColor);
        selection.format.setProperty(QTextFormat::FullWidthSelection, true);
        selection.cursor = textCursor();
        selection.cursor.clearSelection();
        extraSelections.append(selection);
    }

    setExtraSelections(extraSelections);
}

//*****************************************************************************
void mlTextEditor::lineNumberAreaPaintEvent(QPaintEvent *event) {
    QPainter painter(m_lineNumberArea);

    QLinearGradient graygd(0, 0, event->rect().width(), 0);
      graygd.setColorAt(0.0, Qt::white);
      graygd.setColorAt(1.0, Qt::lightGray);
    painter.fillRect(event->rect(), graygd);

    //-------------------------------------------------------------------------
    QTextBlock block = firstVisibleBlock();
    int blockNumber = block.blockNumber();
    int top = (int) blockBoundingGeometry(block).translated(contentOffset()).top();
    int bottom = top + (int) blockBoundingRect(block).height();

    //-------------------------------------------------------------------------
    while (block.isValid() && top <= event->rect().bottom()) {
        if (block.isVisible() && bottom >= event->rect().top()) {
            QString number = QString::number(blockNumber + 1);
            painter.setPen(Qt::black);
            painter.drawText(0, top, m_lineNumberArea->width() - 3, fontMetrics().height(),
                             Qt::AlignRight, number);
        }

        block = block.next();
        top = bottom;
        bottom = top + (int) blockBoundingRect(block).height();
        ++blockNumber;
    }
}

//*****************************************************************************
mlHighlighter::mlHighlighter(QTextDocument *parent)
    : QSyntaxHighlighter(parent) {
    //-------------------------------------------------------------------------
    HighlightingRule rule;

    //-------------------------------------------------------------------------
    // whiteSpaceFormat
    whiteSpaceFormat.setForeground(Qt::gray);
    rule.pattern = QRegExp("\\s+");
    rule.format = whiteSpaceFormat;
    highlightingRules.append(rule);

    //-------------------------------------------------------------------------
    // numericFormat
    numericFormat.setForeground(Qt::red);
    rule.pattern = QRegExp("\\d+");
    rule.format = numericFormat;
    highlightingRules.append(rule);

    //-------------------------------------------------------------------------
    // punctuationFormat
    punctuationFormat.setForeground(Qt::darkGreen);
    rule.format = punctuationFormat;

    // Full stop
    rule.pattern = QRegExp("(\\.\\.)+");
    highlightingRules.append(rule);

    // Tatweel
    rule.pattern = QRegExp("(\\-\\-)+");
    highlightingRules.append(rule);

    // Decimal Separator
    rule.pattern = QRegExp("(?=\\d)\\.(?=\\d)");
    highlightingRules.append(rule);

    // Others
    rule.pattern = QRegExp("[\\?\\|;%\\*\\(\\)\\{\\}\\[\\]\\!\\@\\#\\$\\&\\-\\+\\=]+");
    highlightingRules.append(rule);

    //-------------------------------------------------------------------------
    // haraqatFormat
    haraqatFormat.setForeground(Qt::blue);
    rule.format = haraqatFormat;

    rule.pattern = QRegExp("(\\b[AIU]|\\B[aiu]{1,2}|\\^)" );
    highlightingRules.append(rule);

    rule.pattern = QRegExp("(\\.aN\\b|\\.iN\\b|\\.uN\\b|"
                           "\\.AN\\b|\\.IN\\b|\\.UN\\b|-e\\b)");
    highlightingRules.append(rule);
    //-------------------------------------------------------------------------
    // alphabetsFormat
    alphabetsFormat.setForeground(Qt::darkRed);
    rule.format = alphabetsFormat;

    rule.pattern = QRegExp("(bb|pp|tt|TT|'s's|jj|cc|'h'h|KK"
                           "dd|DD|ZZ|rr|RR|zz|'z'z|ss|SS|"
                           "\\.s\\.s|\\.z\\.z|,t,t|,z,z|"
                           "ee|GG|ff|qq|kk|'k'k|gg|ll|mm|nn|vv|yy)");
    highlightingRules.append(rule);

    //-------------------------------------------------------------------------
    // honorificsFormat
    honorificsFormat.setForeground(Qt::magenta);
    rule.format = honorificsFormat;

    rule.pattern = QRegExp("(\\|PBUH|\\|ALY|\\|RADI|\\|RHMT|\\|TKH)");
    highlightingRules.append(rule);

    //-------------------------------------------------------------------------
    // ligaturesFormat
    ligaturesFormat.setForeground(Qt::darkBlue);
    rule.format = ligaturesFormat;

    rule.pattern = QRegExp("(SANAH|SAFHA|NUMBER|FOOTNOTE|SHER|MISRA)");
    highlightingRules.append(rule);

    rule.pattern = QRegExp("(ALLAH|AKBAR|JALLA|MUHAMMAD|RASUL|SALLA|"
                           "ALAYHI|WASALLAM|SALAM|SLM|BISMILLAH)");
    highlightingRules.append(rule);
}

//*****************************************************************************
void mlHighlighter::highlightBlock(const QString &text) {
    //-------------------------------------------------------------------------
    foreach (const HighlightingRule &rule, highlightingRules) {
        QRegExp expression(rule.pattern);
        int index = expression.indexIn(text);
        while (index >= 0) {
            int length = expression.matchedLength();
            setFormat(index, length, rule.format);
            index = expression.indexIn(text, index + length);
        }
    }
}

//*****************************************************************************
mlSpellChecker::mlSpellChecker(const QString &dictionaryPath,
                           const QString &userDictionary) {

    //-------------------------------------------------------------------------
    m_userDictionary = userDictionary;

    QString dictFile = dictionaryPath + ".dic";
    QString affixFilename = dictionaryPath + ".aff";
    QByteArray dictFilePathBA = dictFile.toLocal8Bit();
    QByteArray affixFilePathBA = affixFilename.toLocal8Bit();
    m_hunspell = new Hunspell(affixFilePathBA.constData(), dictFilePathBA.constData());

    //-------------------------------------------------------------------------
    // detect encoding analyzing the SET option in the affix file
    m_encoding = "ISO8859-1";
    QFile affixFile(affixFilename);
    if (affixFile.open(QIODevice::ReadOnly)) {
        QTextStream stream(&affixFile);
        QRegExp enc_detector("^\\s*SET\\s+([A-Z0-9\\-]+)\\s*", Qt::CaseInsensitive);
        for(QString line = stream.readLine(); !line.isEmpty(); line = stream.readLine()) {
            if (enc_detector.indexIn(line) > -1) {
                m_encoding = enc_detector.cap(1);
                qDebug() << QString("Encoding set to ") + m_encoding;
                break;
            }
        }
        affixFile.close();
    }
    m_codec = QTextCodec::codecForName(this->m_encoding.toLatin1().constData());

    //-------------------------------------------------------------------------
    if(!m_userDictionary.isEmpty()) {
        QFile userDictonaryFile(m_userDictionary);
        if(userDictonaryFile.open(QIODevice::ReadOnly)) {
            QTextStream stream(&userDictonaryFile);
            for(QString word = stream.readLine();
                !word.isEmpty(); word = stream.readLine())
            put_word(word);
            userDictonaryFile.close();
        } else {
            qWarning() << "User dictionary in "
                       << m_userDictionary
                       << "could not be opened";
        }
    } else {
        qDebug() << "User dictionary not set.";
    }
    //-------------------------------------------------------------------------
}

//*****************************************************************************
mlSpellChecker::~mlSpellChecker() {
    delete m_hunspell;
}

//*****************************************************************************
bool mlSpellChecker::spell(const QString &word) {
    //-------------------------------------------------------------------------
    // Encode from Unicode to the encoding used by current dictionary
    return m_hunspell->spell(m_codec->fromUnicode(word).constData()) != 0;
}

//*****************************************************************************
QStringList mlSpellChecker::suggest(const QString &word) {
    //-------------------------------------------------------------------------
    char **suggestWordList;

    //-------------------------------------------------------------------------
    // Encode from Unicode to the encoding used by current dictionary
    int numSuggestions = m_hunspell->suggest( &suggestWordList,
                                 m_codec->fromUnicode(word).constData() );
    QStringList suggestions;
    for(int i=0; i < numSuggestions; ++i) {
        suggestions << m_codec->toUnicode(suggestWordList[i]);
        free(suggestWordList[i]);
    }
    return suggestions;
    //-------------------------------------------------------------------------
}

//*****************************************************************************
void mlSpellChecker::ignoreWord(const QString &word) {
    //-------------------------------------------------------------------------
    put_word(word);
}

//*****************************************************************************
void mlSpellChecker::put_word(const QString &word) {
    //-------------------------------------------------------------------------
    m_hunspell->add(m_codec->fromUnicode(word).constData());
}

//*****************************************************************************
void mlSpellChecker::addToUserWordlist(const QString &word) {
    //-------------------------------------------------------------------------
    put_word(word);
    if(!m_userDictionary.isEmpty()) {
        QFile userDictonaryFile(m_userDictionary);
        if(userDictonaryFile.open(QIODevice::Append)) {
            QTextStream stream(&userDictonaryFile);
            stream << word << "\n";
            userDictonaryFile.close();
        } else {
            qWarning() << "User dictionary in "
                       << m_userDictionary
                       << "could not be opened for appending a new word";
        }
    } else {
        qDebug() << "User dictionary not set.";
    }
    //-------------------------------------------------------------------------
}

//*****************************************************************************
