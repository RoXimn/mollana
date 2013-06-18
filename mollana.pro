#-------------------------------------------------
#-------------------------------------------------

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = mollana
TEMPLATE = app

DEFINES += HUNSPELL_STATIC

SOURCES += main.cpp \
        mltexteditor.cpp \
        mlmainwindow.cpp \
        teckitconverter.cpp

HEADERS  += mlmainwindow.h \
            teckitconverter.h \
            TECkit_Common.h \
            TECkit_Engine.h \
            mltexteditor.h

FORMS    += mlmainwindow.ui

RC_FILE += mollana.rc

RESOURCES += mollana.qrc

INCLUDEPATH += $$_PRO_FILE_PWD_/teckit
INCLUDEPATH += $$_PRO_FILE_PWD_/hunspell

LIBS += -L$$_PRO_FILE_PWD_/teckit -lTECkit \
        -L$$_PRO_FILE_PWD_/hunspell -llibhunspell

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
    doc/css/normalize.css \
    doc/mollana-cheatsheet.tex \
    installer/README.txt
