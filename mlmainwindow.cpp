//*****************************************************************************
#include "mlmainwindow.h"
#include "ui_mlmainwindow.h"

//*****************************************************************************
#include <QFile>
#include <QByteArray>
#include <QDebug>
#include <QSettings>
#include <QFileDialog>
#include <QFontDialog>
#include <QMessageBox>
#include <QTextOption>

//*****************************************************************************
mlMainWindow::mlMainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::mlMainWindow),
    uniConverter(0) {

    ui->setupUi(this);

    //-------------------------------------------------------------------------
    // Load the mapping file
    QByteArray map;
    QFile mfile(":/maps/maps/mollana-urdu.tec");
    if( mfile.open( QIODevice::ReadOnly ) ) {
        qDebug() << "Internal Urdu mapping file loaded...";
        map = mfile.readAll();
        mfile.close();
        qDebug() << "Map size: " << map.size() << "";
    } else {
        qDebug() << "Unable to open Internal Urdu mapping file for reading...\n";
        //raise exception
        return;
    }

    //-------------------------------------------------------------------------
    // Create the converter
    uniConverter = new TECkitConverter( map );
    if( !uniConverter->isValid() ) {
        qDebug() << "Unable to create Unicode TECkit converter...";
        //raise exception
        return;
    }

    //-------------------------------------------------------------------------
    // Toolbars
    ui->mainToolBar->addAction( ui->actionNew );
    ui->mainToolBar->addAction( ui->actionOpen );
    ui->mainToolBar->addAction( ui->actionSave );
    ui->mainToolBar->addSeparator();

    ui->mainToolBar->addAction( ui->actionUndo );
    ui->mainToolBar->addAction( ui->actionRedo );
    ui->mainToolBar->addSeparator();

    ui->mainToolBar->addAction( ui->actionCopy );
    ui->mainToolBar->addAction( ui->actionCut );
    ui->mainToolBar->addAction( ui->actionPaste );
    ui->mainToolBar->addSeparator();

    ui->mainToolBar->addAction( ui->actionUnicodeViewFont );
    ui->mainToolBar->addAction( ui->actionWordWrap );
    ui->mainToolBar->addSeparator();

    //-------------------------------------------------------------------------
    // Signal/Slots
    connect(ui->actionNew,      SIGNAL(triggered()),
            this,               SLOT(newFile()) );
    connect(ui->actionOpen,     SIGNAL(triggered()),
            this,               SLOT(open()) );
    connect(ui->actionSave,     SIGNAL(triggered()),
            this,               SLOT(save()) );
    connect(ui->actionSaveAs,   SIGNAL(triggered()),
            this,               SLOT(saveAs()) );
    connect(ui->actionQuit,     SIGNAL(triggered()),
            this,               SLOT(close()) );
    connect(ui->actionSelectAll,SIGNAL(triggered()),
            ui->tbxEditor,      SLOT(selectAll()) );
    connect(ui->actionEditorFont,
                                SIGNAL(triggered()),
            this,               SLOT(editorFontChanged()) );
    connect(ui->actionUnicodeViewFont,
                                SIGNAL(triggered()),
            this,               SLOT(unicodeFontChanged()) );
    connect(ui->actionAbout,    SIGNAL(triggered()),
            this,               SLOT(about()) );

    connect(ui->tbxEditor->document(),
                                SIGNAL(contentsChanged()),
            this,               SLOT(documentModified()) );

    // Copy, Cut & Paste
    connect(ui->actionCut,      SIGNAL(triggered()),
            ui->tbxEditor,      SLOT(cut()) );
    connect(ui->actionCopy,     SIGNAL(triggered()),
            ui->tbxEditor,      SLOT(copy()) );
    connect(ui->actionPaste,    SIGNAL(triggered()),
            ui->tbxEditor,      SLOT(paste()) );

    connect(ui->tbxEditor,      SIGNAL(copyAvailable(bool)),
            ui->actionCopy,     SLOT(setEnabled(bool)) );
    connect(ui->tbxEditor,      SIGNAL(copyAvailable(bool)),
            ui->actionCut,      SLOT(setEnabled(bool)) );

    // Undo & Redo
    connect(ui->actionUndo,     SIGNAL(triggered()),
            ui->tbxEditor,      SLOT(undo()) );
    connect(ui->actionCopy,     SIGNAL(triggered()),
            ui->tbxEditor,      SLOT(redo()) );

    connect(ui->tbxEditor,      SIGNAL(undoAvailable(bool)),
            ui->actionUndo,     SLOT(setEnabled(bool)) );
    connect(ui->tbxEditor,      SIGNAL(redoAvailable(bool)),
            ui->actionRedo,     SLOT(setEnabled(bool)) );

    connect(ui->actionWordWrap, SIGNAL(toggled(bool)),
            this,               SLOT(wordWrapChanged(bool)) );

    connect(ui->actionUnicodeOutput,
                                SIGNAL(toggled(bool)),
            ui->dckUnicodeOutput,
                                SLOT(setVisible(bool)) );

    connect(ui->tbxEditor,      SIGNAL(textChanged()),
            this,               SLOT(translateText()) );

    //-------------------------------------------------------------------------
    QFont f = ui->tbxUnicodeView->font();
    f.setStyleStrategy(QFont::PreferAntialias);
    ui->tbxUnicodeView->setFont(f);

    //-------------------------------------------------------------------------
    // Start with a new file
    newFile();
}

//*****************************************************************************
mlMainWindow::~mlMainWindow() {
    delete ui;
}

//*****************************************************************************
void mlMainWindow::documentModified() {
    setWindowModified(ui->tbxEditor->document()->isModified());
}

//*****************************************************************************
void mlMainWindow::closeEvent(QCloseEvent *event) {
    //-------------------------------------------------------------------------
    if( okToContinue() ) {
        writeSettings();
        event->accept();
    } else {
        event->ignore();
    }
}

//*****************************************************************************
void mlMainWindow::newFile() {
    //-------------------------------------------------------------------------
    if( okToContinue() ) {
        ui->tbxEditor->clear();
        setCurrentFile("");
    }
}

//*****************************************************************************
void mlMainWindow::open() {
    //-------------------------------------------------------------------------
    if( okToContinue() ) {
        QString fileName = QFileDialog::getOpenFileName(this,
                            tr("%1 - Open a file").arg(sAPPNAME),
                            ".",
                            "Text files (*.txt);;All files (*.*)" );
        if (!fileName.isEmpty())
            loadFile(fileName);
    }
}

//*****************************************************************************
bool mlMainWindow::save() {
    //-------------------------------------------------------------------------
    if( curFile.isEmpty() ) {
        return saveAs();
    } else {
        return saveFile(curFile);
    }
}

//*****************************************************************************
bool mlMainWindow::saveAs() {
    //-------------------------------------------------------------------------
    QString fileName = QFileDialog::getSaveFileName(this,
                            tr("%1 - Save current file").arg(sAPPNAME),
                            ".",
                            "Text files (*.txt);;All files (*.*)" );
    if( fileName.isEmpty() )
        return false;

    return saveFile(fileName);
}

//*****************************************************************************
void mlMainWindow::about() {
    //-------------------------------------------------------------------------
    QMessageBox msgBox(this);
    msgBox.setIconPixmap( QPixmap(":/icons/png32/mollana64.png") );
    msgBox.setTextFormat(Qt::RichText);
    msgBox.setText(
        tr("<p>© Copyright RoXimn 2013<br/>All right reserved.</p>"

        "<p>%1 is an Urdu Unicode text editor that uses "
        "Roman transilteration for easy LTR editing and seemless "
        "real-time conversion to unicode urdu text.</p>"

        "<p><b>Credits</b></p>"

        "<p><b><a href=\"https://github.com/android/platform_frameworks_base/blob/master/data/fonts/DroidNaskh-Regular.ttf\">Droid Arabic Naskh<a></b> font under Apache 2.0 License<br/>"
        "Designer: Pascal Zoghbi, Foundry: <a href=\"http://www.29arabicletters.com/foundry/custom/?m=1-1-1&fid=26\">Ascender Corporation/29arabicletters</a><br/>"
        "Droid Arabic Naskh is an Arabic type designed for use in Google™ products such as Google ChromeOS™ and Android™</p>"

        "<p><b><a href=\"http://scripts.sil.org/TECkit\">TECkit<a></b> a Text Encoding Conversion toolkit under GNU LGPL License<br/>"
        "Author: Jonathan Kew, Organization: <a href=\"http://scripts.sil.org\">SIL International</a><br/>"
        "TECkit is a low-level toolkit intended to be used for performing encoding conversions using a "
        "<i>TECkit engine</i> which relies on mapping tables to perform the conversions.</p>"
       ).arg(sAPPNAME) );
    msgBox.exec();
}

//*****************************************************************************
void mlMainWindow::readSettings() {
    //-------------------------------------------------------------------------
    QSettings settings(sORGNAME, sAPPNAME);
    QPoint pos = settings.value("pos", QPoint(200, 200)).toPoint();
    QSize size = settings.value("size", QSize(400, 400)).toSize();

    resize(size);
    move(pos);
}

//*****************************************************************************
void mlMainWindow::writeSettings() {
    //-------------------------------------------------------------------------
    QSettings settings(sORGNAME, sAPPNAME);
    settings.setValue("pos", pos());
    settings.setValue("size", size());
}

//*****************************************************************************
bool mlMainWindow::okToContinue() {
    if( ui->tbxEditor->document()->isModified() ) {
        QMessageBox::StandardButton ret;
        ret = QMessageBox::warning(this, tr(sAPPNAME),
                     tr("The document has been modified.\n"
                        "Do you want to save your changes?"),
                     QMessageBox::Save |
                     QMessageBox::Discard |
                     QMessageBox::Cancel);

        if (ret == QMessageBox::Save)
            return save();
        else if (ret == QMessageBox::Cancel)
            return false;
    }
    return true;
}

//*****************************************************************************
void mlMainWindow::setCurrentFile(const QString &fileName) {

    curFile = fileName;
    ui->tbxEditor->document()->setModified(false);
    setWindowModified(false);

    QString shownName = curFile;
    if( curFile.isEmpty() )
        shownName = "untitled.txt";
    else
        shownName = strippedName();

    setWindowFilePath(shownName);
    setWindowTitle( tr("%1 - %2[*]")
                    .arg(sAPPNAME)
                    .arg(shownName) );
}

//*****************************************************************************
QString mlMainWindow::strippedName() const {
    return QFileInfo(curFile).fileName();
}

//*****************************************************************************
void mlMainWindow::loadFile(const QString &fileName) {
    QFile file(fileName);
    if (!file.open(QFile::ReadOnly | QFile::Text)) {
        QMessageBox::warning(this, tr(sAPPNAME),
                             tr("Cannot read file %1:\n%2.")
                             .arg(fileName)
                             .arg(file.errorString()));
        return;
    }

    QTextStream in(&file);
    in.setCodec("UTF-8");
    ui->tbxEditor->setPlainText(in.readAll());
    ui->tbxEditor->document()->setModified(false);

    setCurrentFile(fileName);
    ui->statusBar->showMessage(tr("File %1 loaded").arg( fileName ), 3000);
}

//*****************************************************************************
bool mlMainWindow::saveFile(const QString &fileName) {
    QFile file(fileName);
    if (!file.open(QFile::WriteOnly | QFile::Text)) {
        QMessageBox::warning(this, tr(sAPPNAME),
                             tr("Cannot write file %1:\n%2.")
                             .arg(fileName)
                             .arg(file.errorString()));
        return false;
    }

    QTextStream out(&file);
    out.setCodec("UTF-8");
    out << ui->tbxEditor->toPlainText();

    setCurrentFile(fileName);
    ui->statusBar->showMessage(tr("File %1 saved").arg(fileName), 3000);
    return true;
}

//*****************************************************************************
void mlMainWindow::editorFontChanged() {
    //-------------------------------------------------------------------------
    bool ok;
    QFont edfont = QFontDialog::getFont( &ok, ui->tbxEditor->font(), this );
    if( ok )
        ui->tbxEditor->setFont(edfont);
}

//*****************************************************************************
void mlMainWindow::unicodeFontChanged() {
    //-------------------------------------------------------------------------
    bool ok;
    QFont edfont = QFontDialog::getFont( &ok, ui->tbxUnicodeView->font(), this );
    if( ok ) {
        edfont.setStyleStrategy(QFont::PreferAntialias);
        ui->tbxUnicodeView->setFont(edfont);
    }
}


//*****************************************************************************
void mlMainWindow::wordWrapChanged(bool checked) {
    if( checked ) {
        ui->tbxEditor->setLineWrapMode( QPlainTextEdit::WidgetWidth );
        ui->tbxUnicodeView->setLineWrapMode( QTextEdit::WidgetWidth );
    } else {
        ui->tbxEditor->setLineWrapMode( QPlainTextEdit::NoWrap );
        ui->tbxUnicodeView->setLineWrapMode( QTextEdit::NoWrap );
    }
}

//*****************************************************************************
void mlMainWindow::translateText() {
    QString o, i;
    // The converter mangles things up if does not finds characters at the
    // ends of text
    i = ui->tbxEditor->document()->toPlainText();
    o = uniConverter->convert(" " + i + " ");
    o.chop(1);
    ui->tbxUnicodeView->setPlainText( o.right( o.size() - 1 ) );
}

//*****************************************************************************
//*****************************************************************************
