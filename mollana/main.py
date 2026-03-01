# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
"""Application main module.

This module uses houses the :py:func:`~rekhtanavees.main.main` function, which
constructs the PySide QApplication.
"""
# ******************************************************************************
from __future__ import annotations

import logging
import logging.config
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QStyleFactory

from mollana.constants import Rx
from mollana.misc.utils import slugify
from mollana.mainwindow import MainWindow
from mollana.settings import RSettings, Themes


# ******************************************************************************
def _createLogger(dataPath: str) -> logging.Logger:
    """Configure logging system and create an application logger instance"""
    logging.config.dictConfig(config={
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '[{levelname}] {message}',
                'style': '{',
            },
            'detailed': {
                'format': '{asctime} [{levelname}] {message}',
                'datefmt': '%Y-%b-%dT%H:%M:%S%z',
                'style': '{',
            },
            'debuggingDetail': {
                'format': '{asctime} [{levelname}] {module}.{funcName}[{lineno}]: {message}',
                'datefmt': '%Y-%b-%dT%H:%M:%S%z',
                'style': '{',
            },
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            },
            'stderr': {
                'class': 'logging.StreamHandler',
                'level': 'WARNING',
                'formatter': 'simple',
                'stream': 'ext://sys.stderr',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(Path(dataPath) / f'{slugify(Rx.ApplicationName)}.log'),
                'level': 'NOTSET',
                'formatter': 'debuggingDetail',
                'maxBytes': 1_048_576,  # 1 MiB
                'backupCount': 10,
            },
        },
        'loggers': {
            'root': {
                'level': 'NOTSET',
                'handlers': ['file', 'stdout'],
            },
        },
    })
    logging.addLevelName(99, "RUNTIME")
    logger = logging.getLogger(Rx.ApplicationName)
    return logger


# ******************************************************************************
class RApplication(QApplication):
    """Main application class

    Defines application level logger `log` to be universally accessible across the
    application in a consistent uniform way.
    """
    # **************************************************************************
    def __init__(self, argv, **kwargs):
        super(RApplication, self).__init__(argv, **kwargs)

        # ----------------------------------------------------------------------
        # QApplication info
        self.setApplicationName(Rx.ApplicationName)
        self.setApplicationVersion(repr(Rx.ApplicationVersion))
        self.aboutToQuit.connect(self.onQuit)

        # ----------------------------------------------------------------------
        # Logging
        logger: logging.Logger = _createLogger(str(Rx.DataPath))
        logger.log(99, f'Initializing {Rx.ApplicationName} {Rx.ApplicationVersion!r}...')

        # ----------------------------------------------------------------------
        # Preferences
        # os.chdir(Rx.ConfigPath)  # Change directory to settings file location
        settings = RSettings()
        logger.info(f'Preferences loaded')

        logger.setLevel(settings.Main.LogLevel.name)
        logger.debug(f'Log level set to {settings.Main.LogLevel}')

        # ----------------------------------------------------------------------
        # Theming
        self.applyTheme(settings.Main.Theme)

    # **************************************************************************
    def applyTheme(self, theme: Themes) -> None:
        """Apply user selected theme to the application main window"""
        logging.getLogger(Rx.ApplicationName).debug(f'Applying theme {theme}...')
        # **********************************************************************
        if theme == Themes.Light:
            pass
        # **********************************************************************
        elif theme == Themes.Dark:
            # ------------------------------------------------------------------
            # Dark theme
            self.setStyle(QStyleFactory.create('Fusion'))
            darkPalette = QPalette()
            darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
            darkPalette.setColor(QPalette.WindowText, Qt.white)
            darkPalette.setColor(QPalette.Base, QColor(25, 25, 25))
            darkPalette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            darkPalette.setColor(QPalette.ToolTipBase, Qt.white)
            darkPalette.setColor(QPalette.ToolTipText, Qt.white)
            darkPalette.setColor(QPalette.Text, Qt.white)
            darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
            darkPalette.setColor(QPalette.ButtonText, Qt.white)
            darkPalette.setColor(QPalette.BrightText, Qt.red)
            darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
            darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            darkPalette.setColor(QPalette.HighlightedText, Qt.black)

            self.setPalette(darkPalette)
            self.setStyleSheet('QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }')
        # **********************************************************************
        elif theme == Themes.HighContrast:
            pass

    # **************************************************************************
    def start(self):
        """Start application event loop."""
        qApp.logger.debug('Starting application event loop...')
        return self.exec()

    # **************************************************************************
    def onQuit(self):
        """Close application resources (QSettings and log)."""
        qApp.logger.info(f'{Rx.ApplicationName} shutting down')
        RSettings().save()

        qApp.logger.log(99, '\n'*3)
        logging.shutdown()

    # **************************************************************************
    @property
    def logger(self) -> logging.Logger:
        """Application wide logger"""
        return logging.getLogger(Rx.ApplicationName)


# ******************************************************************************
def main() -> int:
    """Main function of the application.

    Returns:
        int: error number, 0 = success.
    """
    # **************************************************************************
    app = RApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    # **************************************************************************
    mainWindow = MainWindow()

    mainWindow.show()
    result = app.start()

    # **************************************************************************
    return result


# ******************************************************************************
if __name__ == '__main__':
    sys.exit(main())

# ******************************************************************************
