#-------------------------------------------------
#
# Project created by QtCreator 2013-05-07T00:16:00
#
#-------------------------------------------------

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = mollana
TEMPLATE = app

SOURCES += main.cpp \
        mlmainwindow.cpp \
        teckitconverter.cpp

HEADERS  += mlmainwindow.h \
            teckitconverter.h \
            TECkit_Common.h \
            TECkit_Engine.h

FORMS    += mlmainwindow.ui

RC_FILE += mollana.rc

RESOURCES += mollana.qrc

LIBS += -L$$_PRO_FILE_PWD_/teckit -lTECkit

CONFIG(debug, debug|release) {
    DEFINES -= QT_NO_DEBUG_OUTPUT
} else {
    DEFINES += QT_NO_DEBUG_OUTPUT
}

OTHER_FILES += \
    mollana.rc \
    maps/mollana-urdu.map \
    doc/guide.htm \
    doc/css/style.css \
    doc/css/normalize.css
