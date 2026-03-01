# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
"""This module manages application wide settings with singleton object,
persisted as a TOML file.

It uses pydantic based confz library for the actual work.

All settings have a default value, and are recreated if missing from the source.
"""
# ******************************************************************************
import logging
from dataclasses import dataclass
from enum import auto
from typing import List, Any
from pathlib import Path

import tomlkit
from tomlkit.exceptions import TOMLKitError
from strenum import StrEnum
from confz import BaseConfig
from pydantic import Field, BaseModel, FilePath, PositiveInt, ValidationError, DirectoryPath
from confz import ConfigSource
from confz.loaders import Loader, register_loader

from mollana.constants import Rx


# ******************************************************************************
class LogLevels(StrEnum):
    """Python log levels"""
    CRITICAL = auto()
    WARNING = auto()
    INFO = auto()
    DEBUG = auto()


# **************************************************************************
class Themes(StrEnum):
    """Application themes"""
    Light = auto()
    Dark = auto()
    HighContrast = auto()


# ******************************************************************************
class MainConfig(BaseModel):
    """Main configuration options"""
    LogLevel: LogLevels = Field(
        default=LogLevels.DEBUG,
        description="Verbosity of the log output "
                    f"({'|'.join([e for e in LogLevels])}). Default is DEBUG"
    )
    Theme: Themes = Field(
        default=Themes.Light,
        description="Application theme "
                    f"({'|'.join([e for e in Themes])}). Default is Light"
    )
    ProjectBaseDirectory: DirectoryPath = Field(
        default="",
        description="Default base directory in which project folders are created",
    )
    RecentMaxCount: PositiveInt = Field(
        default=10,
        le=25,
        description="Maximum number of recent files to keep track of [1 - 25]. "
                    "Default is 10",
    )
    RecentFiles: List[FilePath] = Field(
        default=[],
        description="List of recent files"
    )
    AutoSaveInterval: PositiveInt = Field(
        default=5,
        description="Interval in minutes for autosave. Default is 5"
    )


# ******************************************************************************
CONFIG_FILENAME: str = 'preferences.toml'
"""Filename of the configurations file"""


# **************************************************************************
def _createConfigToml() -> tomlkit.TOMLDocument:
    """Create a de novo configuration document in TOML format"""
    tdoc = tomlkit.TOMLDocument()
    seperator = tomlkit.comment("*" * 78)

    # Header Section
    (tdoc
     .add(seperator)
     .add(tomlkit.comment(f"{Rx.ApplicationName} Preferences"))
     .add(tomlkit.comment(f'Application version: {Rx.ApplicationVersion!s}'))
     .add(tomlkit.nl()))

    # Main
    main = tomlkit.table()
    for fieldName, fieldInfo in (MainConfig.model_fields.items()):
        (main
         .add(tomlkit.comment(fieldInfo.description))
         .add(fieldName, fieldInfo.default)
         .add(tomlkit.nl()))
    tdoc['Main'] = main

    # Footer
    tdoc.add(seperator)

    return tdoc


# ******************************************************************************
@dataclass
class TomlSource(ConfigSource):
    tomlFile: Path


class TomlLoader(Loader):
    """Loader class to load configuration from a TOML file"""
    @classmethod
    def populate_config(cls, config: dict, tomlSource: TomlSource):
        log = logging.getLogger(Rx.ApplicationName)
        if not tomlSource.tomlFile.is_file():
            log.debug(f'{tomlSource.tomlFile} not found. Creating de novo config file...')
            tomlSource.tomlFile.write_text(tomlkit.dumps(_createConfigToml()))

        try:
            tdoc: tomlkit.TOMLDocument = tomlkit.loads(tomlSource.tomlFile.read_text(encoding='utf-8'))
        except TOMLKitError as e:
            log.warning(f'Error decoding {tomlSource.tomlFile!s}: {e!s}')
            log.debug('Resetting the toml document...')
            tdoc = _createConfigToml()

        if 'Main' not in tdoc:
            log.warning(f'"Main" section missing from config TOML')
            main = tomlkit.table()
            for fieldName, fieldInfo in (MainConfig.model_fields.items()):
                (main
                 .add(tomlkit.comment(fieldInfo.description))
                 .add(fieldName, fieldInfo.default)
                 .add(tomlkit.nl()))
            tdoc['Main'] = main

        configUpdate = {}
        try:
            mainConfig = MainConfig.model_validate(tdoc['Main'])
            configUpdate['Main'] = mainConfig
        except ValidationError as ve:
            log.warning(f'{ve.error_count()} error(s) found in preferences "Main" section')
            recentFiles = {i: v for i, v in enumerate(tdoc['Main']["RecentFiles"])}
            for e in ve.errors():
                field = e['loc'][0]
                log.warning(f'{field}="{e["input"]}": {e["msg"]}')
                if field == 'RecentFiles' and e['type'] == 'path_not_file':
                    i: int = e['loc'][1]
                    log.debug(f'Removing file[{i}]:{e["input"]} value of {field}')
                    recentFiles.pop(i)
                else:
                    log.debug(f'Resetting {field}="{e["input"]}" to default')
                    tdoc['Main'][field] = MainConfig.model_fields[field].default

            tdoc['Main']["RecentFiles"] = list(recentFiles.values())
            # Re-attempt validating patched config
            mainConfig = MainConfig.model_validate(tdoc['Main'])
            configUpdate['Main'] = mainConfig

        cls.update_dict_recursively(config, configUpdate)


register_loader(TomlSource, TomlLoader)


# ******************************************************************************
def _encoder(item: Any) -> str:
    if isinstance(item, Path):
        return tomlkit.string(str(item), literal=True)
    else:
        print(f'_encoder: {item}[{type(item)}]')
        raise TOMLKitError()


tomlkit.register_encoder(_encoder)


# ******************************************************************************
class RSettings(BaseConfig):
    Main: MainConfig

    CONFIG_SOURCES = TomlSource(tomlFile=Rx.ConfigPath / CONFIG_FILENAME)

    class Config:
        use_enum_values = True
        frozen = False

    # **************************************************************************
    def save(self):
        """Write current configuration to file.

        The current configuration file is loaded and updated. The overhead of loading
        everytime for saving should be small.

        Raises:
            ValueError: If the configuration file does not exist and
                `denovo` is `False`.
        """
        log = logging.getLogger(Rx.ApplicationName)
        filePath = Rx.ConfigPath / CONFIG_FILENAME
        try:
            tdoc: tomlkit.TOMLDocument = tomlkit.loads(filePath.read_text(encoding='utf-8'))
        except TOMLKitError as e:
            log.warning(f'Error decoding {filePath!s}: {e!s}')
            log.debug('Resetting the toml document...')
            tdoc = _createConfigToml()

        # Main
        main = tdoc['Main']
        for fieldName, fieldInfo in self.Main.model_fields.items():
            main[fieldName] = getattr(self.Main, fieldName)

        # Write toml file
        filePath.write_text(tomlkit.dumps(tdoc))  # TODO: Error handling
        log.debug(f'Preferences saved. ({filePath.resolve()!s})')


# ******************************************************************************
if __name__ == '__main__':
    from pathlib import Path

    # Write config file
    if not Path(CONFIG_FILENAME).is_file():
        print(f"Creating config file: {CONFIG_FILENAME}")
        RSettings.create()

    # Read the config file
    appConfig = RSettings()
    print(appConfig.model_dump_json())
