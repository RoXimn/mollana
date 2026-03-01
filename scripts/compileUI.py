# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
import os
import site
import subprocess

# ******************************************************************************
UIC = os.path.join(site.getsitepackages()[1], 'PySide6/uic.exe')
RCC = os.path.join(site.getsitepackages()[1], 'PySide6/rcc.exe')


# ******************************************************************************
def compileUI(filename: str) -> None:
    """Compile Qt UI file to python code.

    Compile time conversion of the UI design files into python code to be
    integrated into Qt applications.

    Only filename with full path should be given, without file extension. The
    `.ui` extension is added to read the file and `_ui.py` suffix is added to
    the output file. For example to convert `c:\\path\\to\\interface-file.ui`,
    provide `c:\\path\\to\\interface-file` without the `.ui` suffix.

    Args:
        filename (str): Filename of the UI file with full path *without*
            file extension.

    Output:
        The `PySide2/uic` is used to compile the provided UI file to
        python file and adds a `_ui.py` suffix to the output file.
    """
    inFile, outFile = filename + '.ui', filename + '_ui.py'
    try:
        subprocess.run([UIC,
                        '--generator', 'python',
                        '--from-imports',
                        '--output', outFile,
                        inFile],
                       capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print('Unsuccessful compilation of UI', inFile, '->', outFile)
        print(f'*** Err# {e.returncode}:{e.stderr.decode("utf-8")}\n')
    else:
        print('Compiled UI', inFile, '->', outFile)


# ******************************************************************************
def compileRC(filename: str) -> None:
    """Compile Qt RCC file to python code.

    Compile time conversion of the resource files into python code to be
    integrated into Qt applications.

    Only filename with full path should be given, without file extension. The
    `.ui` extension is added to read the file and `_ui.py` suffix is added to
    the output file. For example to convert `c:\\path\\to\\interface-file.ui`,
    provide `c:\\path\\to\\interface-file` without the `.ui` suffix.

    Args:
        filename (str): Filename of the UI file with full path *without*
            file extension.

    Output:
        The `PySide2/uic` is used to compile the provided UI file to
        python file and adds a `_ui.py` suffix to the output file.
    """
    inFile, outFile = filename + '.qrc', filename + '_rc.py'

    try:
        subprocess.run([RCC, '-g', 'python', '-o', outFile, inFile],
                       capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print('Unsuccessful compilation of QRC', inFile, '->', outFile)
        print(f'*** Err# {e.returncode}:{e.output.decode("utf-8")}\n')
    else:
        print('Compiled QRC', inFile, '->', outFile)


# ******************************************************************************
if __name__ == '__main__':
    commonFiles = []

    # Compile User Interface files
    uiFiles = commonFiles[:]
    uiFiles.extend([
        'mollana/mainwindow',
    ])
    for filename in uiFiles:
        compileUI(filename)

    # Compile Resource files
    rcFiles = commonFiles[:]
    rcFiles.extend([
        'mollana/mollana',
    ])
    for filename in rcFiles:
        compileRC(filename)

# ******************************************************************************
