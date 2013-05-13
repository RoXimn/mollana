//*****************************************************************************
#include "mlmainwindow.h"

//*****************************************************************************
#include <QApplication>
#include <QFont>

//*****************************************************************************
int main(int argc, char *argv[]) {

    QApplication app(argc, argv);
    mlMainWindow window;

    app.setOrganizationName(sORGNAME);
    app.setApplicationName(sAPPNAME);

    window.show();
    
    return app.exec();
}
//*****************************************************************************

