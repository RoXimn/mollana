#include <QtGlobal>
#include <QtDebug>
#include "teckitconverter.h"

//*****************************************************************************
TECkitConverter::TECkitConverter( const QByteArray& map ) : mp_converter(0) {

    TECkit_Converter	cvtr;
    bool                direction = true;  // Forward = true, Reverse = false
    unsigned int        inform  = kForm_UTF16LE;
    unsigned int        outform = kForm_UTF8;

    if( map.isNull() ) {
        // raise exception
        qDebug() << "TECkitConverter ctor: Null mapping object\n";
        return;
    }

    /*
    TECkit_Status
    WINAPI
    TECkit_CreateConverter(
        Byte*				mapping,
        UInt32				mappingSize,
        Byte				mapForward,
        UInt16				sourceForm,
        UInt16				targetForm,
        TECkit_Converter*	converter);
    */

    long status = TECkit_CreateConverter(
                    (Byte*)map.constData(),
                    (UInt32)map.size(),
                    (Byte)(direction ? 1 : 0),
                    (UInt16)inform,
                    (UInt16)outform,
                    &cvtr);

    if (status != kStatus_NoError) {
        // raise exception
        qDebug() << "TECkit_CreateConverter status error: " << status << "\n";
        return;
    }

    mp_converter = cvtr;
}

//*****************************************************************************
TECkitConverter::~TECkitConverter() {

    if( mp_converter ) {
        long status = TECkit_DisposeConverter( mp_converter );
        if (status != kStatus_NoError) {
            // raise exception
            qDebug() << "TECkit_DisposeConverter status error: " << status << "\n";
        }
        mp_converter = 0;
    }
}

//*****************************************************************************
quint32 TECkitConverter::getSourceFlags() {

    quint32 flags = 0;

    if( mp_converter ) {
        UInt32 sourceFlags;
        long status = TECkit_GetConverterFlags( mp_converter, &sourceFlags, 0 );
        if (status != kStatus_NoError) {
            // raise exception
            qDebug() << "TECkit_GetConverterFlags status error: " << status << "\n";
        }
        flags = sourceFlags;
    }

    return flags;
}

//*****************************************************************************
quint32 TECkitConverter::getTargetFlags() {

    quint32 flags = 0;

    if( mp_converter ) {
        UInt32 targetFlags;
        long status = TECkit_GetConverterFlags( mp_converter, 0, &targetFlags );
        if (status != kStatus_NoError) {
            // raise exception
            qDebug() << "TECkit_GetConverterFlags status error: " << status << "\n";
        }
        flags = targetFlags;
    }

    return flags;
}

//*****************************************************************************
// Convert the
QString TECkitConverter::convert( const QString& intxt ) {

    const int BUFFERSZ = 16384;

    /*
        Convert text from a buffer in memory, with options
        (note that former inputIsComplete flag is now a bit in the options parameter)

    TECkit_Status
    WINAPI
    TECkit_ConvertBufferOpt(
        TECkit_Converter	converter,
        const Byte*			inBuffer,
        UInt32				inLength,
        UInt32*				inUsed,
        Byte*				outBuffer,
        UInt32				outLength,
        UInt32*				outUsed,
        UInt32				inOptions,
        UInt32*				lookaheadCount);
    */

    UInt32 inUsed = 0;
    UInt32 outUsed = 0;
    UInt32 lookahead = 0;
    //QByteArray inutf = intxt.toUtf8();
    QByteArray oututf = QByteArray();

    oututf.resize(BUFFERSZ);

    long status = TECkit_ConvertBufferOpt(
                        mp_converter,

                        (Byte*)intxt.utf16(), // QString UTF16 data
                        intxt.size() << 1, // Number of chars * 2 bytes
                        &inUsed,

                        (Byte*)oututf.data(),
                        BUFFERSZ,
                        &outUsed,

                        kOptionsUnmapped_UseReplacementCharSilently,
                        &lookahead );

    if (status != kStatus_NoError) {
        if( (status & kStatusMask_Basic) != kStatus_NeedMoreInput ) {
            // raise exception
            qDebug() << "TECkit_ConvertBufferOpt status error: " << status << "\n";
            return QString("!*!*!ERROR!*!*!");
        } else {
            Q_ASSERT(outUsed < oututf.size());
            oututf[outUsed] = '\0';
        }
    }

    return QString::fromUtf8(oututf);
}

//*****************************************************************************
