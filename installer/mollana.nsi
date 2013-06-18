; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "Mollana"
!define PRODUCT_VERSION "v0.1.2a"
!define PRODUCT_PUBLISHER "RoXimn"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\mollana.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

!define QT_DIRECTORY "E:\Qt-MSVC\5.0.2\msvc2010"
;!define QT_DIRECTORY "E:\Qt\5.0.2\msvc2010"

; MUI 1.67 compatible ------
!include "MUI.nsh"
!include "FontRegAdv.nsh"
!include "FontName.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "..\png32\mollana.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!define MUI_LICENSEPAGE_CHECKBOX
!insertmacro MUI_PAGE_LICENSE "..\liscence.txt"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\mollana.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

;-------------------------------
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "mollana0.1.2a-win32-setup.exe"
InstallDir "$PROGRAMFILES\Mollana"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File "..\..\build-mollana-Desktop_Qt_5_0_2_MSVC2010_32bit-Release\release\mollana.exe"
  File "..\teckit\TECkit_x86.dll"
  File "${QT_DIRECTORY}\bin\Qt5Widgets.dll"
  File "${QT_DIRECTORY}\bin\Qt5Gui.dll"
  File "${QT_DIRECTORY}\bin\Qt5Core.dll"
  File "${QT_DIRECTORY}\bin\libGLESv2.dll"
  File "${QT_DIRECTORY}\bin\libEGL.dll"
  File "${QT_DIRECTORY}\bin\icuuc49.dll"
  File "${QT_DIRECTORY}\bin\icuin49.dll"
  File "${QT_DIRECTORY}\bin\icudt49.dll"
  File "${QT_DIRECTORY}\bin\D3DCompiler_43.dll"

  SetOutPath "$INSTDIR\platforms"
  File "${QT_DIRECTORY}\plugins\platforms\qwindows.dll"
  File "${QT_DIRECTORY}\plugins\platforms\qminimal.dll"
  
  SetOutPath "$INSTDIR\dict"
  File "..\dict\mollana-urdu.aff"
  File "..\dict\mollana-urdu.dic"
  File "..\dict\mollana-urdu-custom.txt"

  SetOutPath "$INSTDIR\doc"
  File "..\doc\guide.htm"
  File "..\doc\mollana-cheatsheet.pdf"

  SetOutPath "$INSTDIR\doc\css"
  File "..\doc\css\*.css"
   
  SetOutPath "$INSTDIR\doc\img"
  File "..\doc\img\*.png"
  
  StrCpy $FONT_DIR $FONTS
  !insertmacro InstallTTF '..\fonts\DroidNaskh-Regular.ttf'
  !insertmacro InstallTTF '..\fonts\DroidSansMono.ttf'
  SendMessage ${HWND_BROADCAST} ${WM_FONTCHANGE} 0 0 /TIMEOUT=5000

  SetOutPath "$INSTDIR\vcredist"
  File "${QT_DIRECTORY}\..\..\vcredist\vcredist_sp1_x86.exe"
  ExecWait '"$INSTDIR\vcredist\vcredist_sp1_x86.exe" /q /norestart'
  
  CreateDirectory "$SMPROGRAMS\Mollana"
  CreateShortCut "$SMPROGRAMS\Mollana\Mollana.lnk" "$INSTDIR\mollana.exe"
  CreateShortCut "$DESKTOP\Mollana.lnk" "$INSTDIR\mollana.exe"
SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\Mollana\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\mollana.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\mollana.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\platforms\qwindows.dll"
  Delete "$INSTDIR\platforms\qminimal.dll"
  RMDir "$INSTDIR\platforms"
  
  Delete "$INSTDIR\doc\mollana-cheatsheet.pdf"
  Delete "$INSTDIR\doc\guide.htm"
  Delete "$INSTDIR\doc\css\*.css"
  Delete "$INSTDIR\doc\img\*.png"
  
  RMDir "$INSTDIR\doc\css"
  RMDir "$INSTDIR\doc\img"
  RMDir "$INSTDIR\doc"
  
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\mollana.exe"
  Delete "$INSTDIR\icuin49.dll"
  Delete "$INSTDIR\icuuc49.dll"
  Delete "$INSTDIR\libEGL.dll"
  Delete "$INSTDIR\libGLESv2.dll"
  Delete "$INSTDIR\Qt5Core.dll"
  Delete "$INSTDIR\Qt5Gui.dll"
  Delete "$INSTDIR\Qt5Widgets.dll"
  Delete "$INSTDIR\TECkit_x86.dll"
  Delete "$INSTDIR\icudt49.dll"
  Delete "$INSTDIR\D3DCompiler_43.dll"

  ;ExecWait '"$INSTDIR\vcredist\vcredist_sp1_x86.exe /uninstall /q /norestart"'
  Delete "$INSTDIR\vcredist\vcredist_sp1_x86.exe"
  RMDir "$INSTDIR\vcredist"

  RMDir "$INSTDIR"

  Delete "$DESKTOP\Mollana.lnk"

  Delete "$SMPROGRAMS\Mollana\Uninstall.lnk"
  Delete "$SMPROGRAMS\Mollana\Mollana.lnk"
  RMDir "$SMPROGRAMS\Mollana"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd
