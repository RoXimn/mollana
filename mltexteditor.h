//*****************************************************************************
#ifndef MLTEXTEDITOR_H
#define MLTEXTEDITOR_H

//*****************************************************************************
#include <QPlainTextEdit>
#include <QSyntaxHighlighter>
#include <QObject>

//*****************************************************************************
class mlLineNumberArea;
class mlHighlighter;
class Hunspell;

//*****************************************************************************
//*****************************************************************************
//*****************************************************************************
class mlTextEditor : public QPlainTextEdit {

    Q_OBJECT

    //*************************************************************************
    public: //-----------------------------------------------------------------

        mlTextEditor(QWidget *parent = 0);

        void lineNumberAreaPaintEvent(QPaintEvent *event);
        int lineNumberAreaWidth();

    //*************************************************************************
    protected: //--------------------------------------------------------------

        void resizeEvent(QResizeEvent *event);

    //*************************************************************************
    private slots: //----------------------------------------------------------

        void updateLineNumberAreaWidth(int newBlockCount);
        void highlightCurrentLine();
        void updateLineNumberArea(const QRect &, int);

    //*************************************************************************
    private: //----------------------------------------------------------------

        mlHighlighter *m_highlighter;
        QWidget *m_lineNumberArea;
};

//*****************************************************************************
//*****************************************************************************
//*****************************************************************************
class mlHighlighter : public QSyntaxHighlighter {
    //*************************************************************************
    Q_OBJECT

    //*************************************************************************
    public: //-----------------------------------------------------------------
        mlHighlighter(QTextDocument *parent = 0);

    //*************************************************************************
    protected: //--------------------------------------------------------------
        void highlightBlock(const QString &text);

    //*************************************************************************
    private: //----------------------------------------------------------------
        struct HighlightingRule {
         QRegExp pattern;
         QTextCharFormat format;
        };

        QVector<HighlightingRule> highlightingRules;

        QTextCharFormat whiteSpaceFormat;
        QTextCharFormat numericFormat;
        QTextCharFormat punctuationFormat;
        QTextCharFormat honorificsFormat;
        QTextCharFormat haraqatFormat;
        QTextCharFormat alphabetsFormat;
        QTextCharFormat ligaturesFormat;
    //*************************************************************************
};


//*****************************************************************************
class mlLineNumberArea : public QWidget {

    //*************************************************************************
    public: //-----------------------------------------------------------------
        mlLineNumberArea(mlTextEditor *editor) : QWidget(editor) {
            m_textEditor = editor;
        }

        QSize sizeHint() const {
            return QSize(m_textEditor->lineNumberAreaWidth(), 0);
        }

    //*************************************************************************
    protected: //--------------------------------------------------------------
        void paintEvent(QPaintEvent *event) {
            m_textEditor->lineNumberAreaPaintEvent(event);
        }

    //*************************************************************************
    private: //----------------------------------------------------------------

        mlTextEditor *m_textEditor;
    //*************************************************************************
};

//*****************************************************************************
//*****************************************************************************
//*****************************************************************************
class mlSpellChecker {

    //*************************************************************************
    public: //-----------------------------------------------------------------
        mlSpellChecker(const QString &dictionaryPath, const QString &userDictionary);
        ~mlSpellChecker();

        bool spell(const QString &word);
        QStringList suggest(const QString &word);
        void ignoreWord(const QString &word);
        void addToUserWordlist(const QString &word);

    //*************************************************************************
    private: //----------------------------------------------------------------
        void put_word(const QString &word);
        Hunspell *m_hunspell;
        QString m_userDictionary;
        QString m_encoding;
        QTextCodec *m_codec;

    //*************************************************************************
};


//*****************************************************************************
#endif // MLTEXTEDITOR_H
//*****************************************************************************
