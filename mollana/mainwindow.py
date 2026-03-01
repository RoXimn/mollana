# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from PySide6.QtCore import (
    QTimer
)
from PySide6.QtWidgets import (
    QMainWindow, QMessageBox
)

from mollana.constants import Rx
from mollana.mainwindow_ui import Ui_MainWindow


# ******************************************************************************
class MainWindow(QMainWindow):
    """Application MainWindow class"""

    # **************************************************************************
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.actionNew.triggered.connect(self.onNew)
        self.ui.actionOpen.triggered.connect(self.onOpen)
        self.ui.actionSave.triggered.connect(self.onSave)
        self.ui.actionQuit.triggered.connect(self.onExit)

        # self.ui.actionAboutQt.triggered.connect(qApp.aboutQt)

        self.ui.autoSaveTimer = QTimer(self)
        self.ui.autoSaveTimer.timeout.connect(self.onAutoSave)

        # Recent files
        # self.ui.maxRecentCount = RSettings().Main.RecentMaxCount
        #
        # self.ui.recentSeperator = self.ui.menuRecent.addSeparator()
        # self.ui.menuRecent.insertAction(self.ui.actionClearRecent, self.ui.recentSeperator)
        # self.ui.recentSeperator.setVisible(False)
        #
        # self.ui.actionClearRecent.setEnabled(False)
        # self.ui.actionClearRecent.triggered.connect(self.onClearRecentFiles)
        #
        # self.ui.recentFileActionList = []
        # for i in range(self.ui.maxRecentCount):
        #     act = QAction(self)
        #     act.setVisible(False)
        #     act.triggered.connect(self.onOpenRecent)
        #     self.ui.recentFileActionList.append(act)
        #     self.ui.menuRecent.insertAction(self.ui.recentSeperator, act)
        #
        # self.updateRecentFileList()

    # **************************************************************************
    def onNew(self) -> None:
        qApp.logger.info("on new action")

    # **************************************************************************
    def onOpen(self) -> None:
        qApp.logger.info("on open action")

    # **************************************************************************
    # def onOpenRecent(self) -> None:
    #     action: QAction = self.sender()  # type: ignore
    #     if action:
    #         if self.audioProject.data:
    #             self.onProjectClose()
    #         self.loadAudioProject(action.data())

    # **************************************************************************
    def onExit(self) -> None:
        self.close()

    # **************************************************************************
    def onAbout(self) -> None:
        QMessageBox.about(
            self,
            f'{Rx.ApplicationName} - About',
            f'<h4>{Rx.ApplicationName} <tt>{Rx.ApplicationVersion}</tt><br>'
            f'{Rx.Copyright}</h4>'
            f'<p>{Rx.Licence}</p>'
            '<h4>Attributions</h4>'
            '<ul>'
            '<li>Some icons by <a href="https://github.com/KDE/oxygen-icons5">Oxygen Icons</a>, '
            'licensed under <a href="https://www.gnu.org/licenses/lgpl-3.0.en.html">'
            'GNU Lesser General Public License v3.0</a> License.</li>'
            '</ul>'
            '</div>'
        )

    # **************************************************************************
    # def adjustRecentListForCurrent(self, projectFilename: Path):
    #     qApp.logger.debug(f"Adjusting recent list for {projectFilename}")
    #     settings = RSettings()
    #     recentFiles: List[Path] = settings.Main.RecentFiles
    #     qApp.logger.debug(f"Total recents[{len(recentFiles)}] "
    #                       f"{', '.join(f'{rf!s}' for rf in recentFiles)}")
    #
    #     while projectFilename in recentFiles:
    #         recentFiles.remove(projectFilename)
    #     recentFiles.insert(0, projectFilename)
    #     if len(recentFiles) > self.ui.maxRecentCount:
    #         del recentFiles[self.ui.maxRecentCount:]
    #     settings.Main.RecentFiles = recentFiles
    #     settings.save()
    #     qApp.logger.debug(f"Updated recents[{len(recentFiles)}] "
    #                       f"{', '.join(f'{rf!s}' for rf in recentFiles)}")
    #
    #     self.updateRecentFileList()

    # **************************************************************************
    # def updateRecentFileList(self):
    #     settings = RSettings()
    #     recentFiles: List[Path] = settings.Main.RecentFiles
    #     total: int = min(len(recentFiles), settings.Main.RecentMaxCount)
    #     qApp.logger.debug(f"Total recents[{total}] "
    #                       f"{', '.join(f'{rf!s}' for rf in recentFiles)}")
    #
    #     for i in range(total):
    #         recentFile = recentFiles[i]
    #         fn = recentFile.stem
    #         act = self.ui.recentFileActionList[i]
    #         act.setText(f'&{i + 1}. {fn}')
    #         act.setIcon(QIcon(':/images/icons/folder-bookmark.png'))
    #         act.setVisible(True)
    #         act.setToolTip(str(recentFile))
    #         act.setData(recentFile)
    #
    #     for i in range(total, self.ui.maxRecentCount):
    #         self.ui.recentFileActionList[i].setVisible(False)
    #
    #     hasRecent: bool = total > 0
    #     self.ui.actionClearRecent.setEnabled(hasRecent)
    #     self.ui.recentSeperator.setVisible(hasRecent)

    # **************************************************************************
    # def onClearRecentFiles(self):
    #     settings = RSettings()
    #     settings.Main.RecentFiles.clear()
    #     settings.save()
    #     self.updateRecentFileList()

    # **************************************************************************
    def onAutoSave(self):
        qApp.logger.info(f"Autosaving ...")
        self.onSave()

    # **************************************************************************
    def onSave(self):
        qApp.logger.info("on save action")

# ******************************************************************************
