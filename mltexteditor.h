//*****************************************************************************
#ifndef MLTEXTEDITOR_H
#define MLTEXTEDITOR_H

//*****************************************************************************
#include <QPlainTextEdit>
#include <QSyntaxHighlighter>
#include <QObject>

//*****************************************************************************
class LineNumberArea;
class mlHighlighter;

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
class mlHighlighter : public QSyntaxHighlighter {
    //*************************************************************************
    Q_OBJECT

    //*************************************************************************
    public:
        mlHighlighter(QTextDocument *parent = 0);

    //*************************************************************************
    protected:
        void highlightBlock(const QString &text);

    //*************************************************************************
    private:
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
class LineNumberArea : public QWidget {

    //*************************************************************************
    public:
        LineNumberArea(mlTextEditor *editor) : QWidget(editor) {
            m_textEditor = editor;
        }

        QSize sizeHint() const {
            return QSize(m_textEditor->lineNumberAreaWidth(), 0);
        }

    //*************************************************************************
    protected:

        void paintEvent(QPaintEvent *event) {
            m_textEditor->lineNumberAreaPaintEvent(event);
        }

    //*************************************************************************
    private:

    mlTextEditor *m_textEditor;
    //*************************************************************************
};

//*****************************************************************************
#endif // MLTEXTEDITOR_H
//*****************************************************************************
