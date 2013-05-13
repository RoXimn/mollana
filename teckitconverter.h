#ifndef TECKITCONVERTER_H
#define TECKITCONVERTER_H

//*****************************************************************************
#include "teckit/TECkit_Common.h"
#include "teckit/TECkit_Engine.h"

//*****************************************************************************
#include <QByteArray>
#include <QString>

//*****************************************************************************
class TECkitConverter {

    //*************************************************************************
    private:

    TECkit_Converter	mp_converter;

    //*************************************************************************
    public:

    TECkitConverter( const QByteArray& map );
    ~TECkitConverter();

    bool isValid()
        { return (mp_converter != 0); }

    quint32 getSourceFlags();
    quint32 getTargetFlags();

    QString convert( const QString& intxt );

};
//*****************************************************************************
#endif // TECKITCONVERTER_H
//*****************************************************************************
