@echo off
set INNOSETUP_DIR="C:\Program Files (x86)\Inno Setup 6"

@REM cd docs
@REM call make clean
@REM call make html
@REM cd ..

python scripts/compileUI.py
pyinstaller --clean --noconfirm mollana.app.spec

%INNOSETUP_DIR%\ISCC.exe installer\mollana-installer.iss
