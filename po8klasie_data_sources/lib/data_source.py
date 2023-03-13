from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session
from termcolor import colored

from os import path
from pydantic import BaseModel
from pathlib import Path

from po8klasie_data_sources.cli.cli_logger import cli_logger

from po8klasie_data_sources.lib.environment_manager import EnvironmentManager


class DataSourceConfigBaseModel(BaseModel):
    disabled: Optional[bool] = False


class DataSource:
    intermediate_files_dir_path: str | None = None

    def __init__(self, environment_manager: EnvironmentManager):
        self.environment_manager = environment_manager
        self._load_config()
        self._init_intermediate_files_dir()

    def _load_config(self):
        config_key = f"{self.info['id'].upper()}_DATA_SOURCE_CONFIG"
        config_dict = getattr(self.environment_manager.config, config_key)
        self.config = self.ConfigModel.parse_obj(config_dict)

    def _init_intermediate_files_dir(self):
        self.intermediate_files_dir_path = path.join(
            self.environment_manager.env_intermediate_files_dir_path,
            self.info["id"],
        )
        Path(self.intermediate_files_dir_path).mkdir(parents=True, exist_ok=True)

    def _get_intermediate_file_path(self, filename):
        return path.join(self.intermediate_files_dir_path, filename)

    def create_intermediate_files(self, session: Session):
        raise NotImplementedError(
            f"create_intermediate_files not implemented for {self.info.get('name')} data source"
        )

    def create_records(self, session: Session):
        raise NotImplementedError(
            f"create_records not implemented for {self.info.get('name')} data source"
        )

    def log(self, message):
        cli_logger.info(
            colored(f"[{self.info.get('id')} ds]: ", attrs=["bold"]) + message
        )

    class ConfigModel(DataSourceConfigBaseModel):
        pass
