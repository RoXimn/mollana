#ifndef MLMAINWINDOW_H
#define MLMAINWINDOW_H

//*****************************************************************************
#include <QMainWindow>

//*****************************************************************************
#include "teckitconverter.h"

//*****************************************************************************
const char sORGNAME[] = "RoC";
const char sAPPNAME[] = "Mollana";

//*****************************************************************************
namespace Ui {
    class mlMainWindow;
}

//*****************************************************************************
class mlMainWindow : public QMainWindow {
    Q_OBJECT

    //*************************************************************************
    public:

    explicit mlMainWindow(QWidget *parent = 0);
    ~mlMainWindow();
    //*************************************************************************
    protected:

    void closeEvent(QCloseEvent *event);

    //*************************************************************************
    private slots:

    void newFile();
    void open();
    bool save();
    bool saveAs();
    void about();
    void editorFontChanged();
    void unicodeFontChanged();
    void wordWrapChanged(bool);
    void documentModified();
    void translateText();

    //*************************************************************************
    private:

    void readSettings();
    void writeSettings();

    bool okToContinue();
    void loadFile(const QString &fileName);
    bool saveFile(const QString &fileName);
    void setCurrentFile(const QString &fileName);
    QString strippedName() const;

    //*************************************************************************
    private:

    QString curFile;

    Ui::mlMainWindow *ui;
    TECkitConverter *uniConverter;
};
//*****************************************************************************

#endif // MLMAINWINDOW_H
