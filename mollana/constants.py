# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
"""Global constants used across the application"""
# ******************************************************************************
import os
import platform
from collections import namedtuple
from pathlib import Path
from uuid import uuid5, NAMESPACE_DNS, UUID
from zoneinfo import ZoneInfo

# ******************************************************************************
RVersionType = namedtuple('RVersionType', ['major', 'minor', 'patch', 'phase'])


# ******************************************************************************
class RVersion:
    """Comparable version class"""
    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0, phase: str = ''):
        self._version = RVersionType(major, minor, patch, phase)

    @property
    def major(self) -> int:
        """Major version number"""
        return self._version.major

    @property
    def minor(self) -> int:
        """Minor version number"""
        return self._version.minor

    @property
    def patch(self) -> int:
        """Patch number"""
        return self._version.patch

    @property
    def phase(self) -> str:
        """Phase identifier"""
        return self._version.phase

    def _isComparable(self, other: 'RVersion'):
        """Check if the objects can be compared w.r.t. version"""
        return (
            isinstance(getattr(self, '_version', None), RVersionType) and
            isinstance(getattr(other, '_version', None), RVersionType)
        )

    def __lt__(self, other: 'RVersion'):
        if not self._isComparable(other):
            raise NotImplementedError

        if self._version.major < other._version.major:
            return True
        elif self._version.major > other._version.major:
            return False
        elif self._version.major == other._version.major:
            if self._version.minor < other._version.minor:
                return True
            elif self._version.minor > other._version.minor:
                return False
            elif self._version.minor == other._version.minor:
                return self._version.patch < other._version.patch
        return None

    def __eq__(self, other: 'RVersion'):
        if not self._isComparable(other):
            return NotImplemented
        return (
            (self._version.major == other._version.major) and
            (self._version.minor == other._version.minor) and
            (self._version.patch == other._version.patch)
        )

    def __ne__(self, other: 'RVersion'):
        if not self._isComparable(other):
            return NotImplemented
        return not (self == other)

    def __le__(self, other: 'RVersion'):
        if not self._isComparable(other):
            return NotImplemented
        return self < other or self == other

    def __gt__(self, other: 'RVersion'):
        if not self._isComparable(other):
            return NotImplemented
        return not (self < other or self == other)

    def __ge__(self, other: 'RVersion'):
        if not self._isComparable(other):
            return NotImplemented
        return not (self < other)

    def __repr__(self):
        return '{0}.{1}.{2}{3}'.format(
                self.major, self.minor, self.patch,
                ' ({0})'.format(self.phase) if self.phase else '')

    def __str__(self):
        return '{0}.{1}'.format(self.major, self.minor)


# ******************************************************************************
class RConstants:
    """Defines global constants"""

    @property
    def ApplicationName(self) -> str:
        """Application name/title

        Can and should be usable as file/folder name
        """
        return 'mollana'

    @property
    def ApplicationVersion(self) -> RVersion:
        """Application version"""
        return RVersion(major=0, minor=1, patch=3, phase='Alpha')

    @property
    def AuthorName(self) -> str:
        """Application author name/alias"""
        return 'RoXimn'

    @property
    def AuthorEmail(self) -> str:
        """Application author email"""
        return 'roximn@rixir.org'

    @property
    def Copyright(self) -> str:
        """Application copyright text"""
        return '(C) RoXimn 2025'

    @property
    def Licence(self) -> str:
        """Application usage licence text"""
        return ('This work is licensed under the Creative Commons Attribution '
                '4.0 International License. To view a copy of this license, '
                'visit http://creativecommons.org/licenses/by/4.0/.')

    @property
    def ApplicationUUID(self) -> UUID:
        """Application UUID"""
        return uuid5(NAMESPACE_DNS, self.ApplicationName)

    @property
    def Timezone(self) -> ZoneInfo:
        """Default time zone for the application"""
        return ZoneInfo('Asia/Riyadh')

    _dataPath: Path | None = None
    _configPath: Path | None = None

    @property
    def DataPath(self) -> Path:
        """Folder to use for application data, e.g. log file"""
        if self._dataPath is not None:
            return self._dataPath

        baseFolder = Path.home()
        system = platform.system()
        if system == 'Windows' and 'APPDATA' in os.environ:
            baseFolder = Path(os.environ['APPDATA'])
        elif system == 'Darwin':
            pass
        elif 'XDG_DATA_HOME' in os.environ:
            baseFolder = Path(os.environ['XDG_DATA_HOME'])
        self._dataPath = baseFolder / ('.'+self.ApplicationName) / str(self.ApplicationVersion)
        self._dataPath.mkdir(parents=True, exist_ok=True)
        return self._dataPath

    @property
    def ConfigPath(self) -> Path:
        """Folder to use for application configuration file"""
        if self._configPath is not None:
            return self._configPath

        baseFolder = Path.home()
        system = platform.system()
        if system == 'Windows' and 'APPDATA' in os.environ:
            baseFolder = Path(os.environ['APPDATA'])
        elif system == 'Darwin':
            pass
        elif 'XDG_CONFIG_HOME' in os.environ:
            baseFolder = Path(os.environ['XDG_CONFIG_HOME'])
        self._configPath = baseFolder / ('.'+self.ApplicationName) / str(self.ApplicationVersion)
        self._configPath.mkdir(parents=True, exist_ok=True)
        return self._configPath


# ******************************************************************************
# Export Rx for global access to the application wide constants
# global Rx
Rx = RConstants()


# ******************************************************************************
