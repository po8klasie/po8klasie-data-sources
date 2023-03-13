import importlib
from typing import List, Dict, Any
from os import path
from dotenv import dotenv_values

from po8klasie_data_sources.db.db import DatabaseManager

DEFAULT_ENVIRONMENT_STRING = "local"


class EnvironmentManager:
    configs = {}
    _data_sources = []
    config: Dict[str, Dict[str, Any]] = {}
    env_vars = {}
    environment_string = None
    db: DatabaseManager
    initialized_data_sources: list[Any] = []
    current_dir: str
    is_environment_loaded = False
    env_intermediate_files_dir_path: str

    def __init__(self, config_modules: dict[str, Any], file, data_sources=List[Any]):
        self._config_modules = config_modules
        self._data_sources = data_sources
        self.current_dir = path.dirname(file)

    def _validate_environment_string(self, environment_string):
        if not environment_string:
            environment_string = DEFAULT_ENVIRONMENT_STRING
        if environment_string not in self._config_modules:
            raise Exception(f"No config provided for {environment_string} environment")
        return environment_string

    def _load_configs(self):
        self.configs = {
            key: importlib.import_module(module)
            for key, module in self._config_modules.items()
        }
        self.config = self.configs[self.environment_string]

    def _set_intermediate_files_dir_path(self, override_intermediate_files_dir=False):
        dir_path = self.config.INTERMEDIATE_FILES_DIR
        if override_intermediate_files_dir:
            dir_path = override_intermediate_files_dir

        self.env_intermediate_files_dir_path = path.join(self.current_dir, dir_path)

    def _load_env_vars(self):
        self.env_vars = dotenv_values(f".env.{self.environment_string}")

    def _init_db(self):
        if "DATABASE_URL" not in self.env_vars:
            raise Exception("No DATABASE_URL env var supplied")
        self.db = DatabaseManager(database_url=self.env_vars["DATABASE_URL"])

    def _init_data_sources(self):
        self.initialized_data_sources = []
        for data_source in self._data_sources:
            self.initialized_data_sources.append(data_source(self))

    def load_environment(
        self, environment_string: str, override_intermediate_files_dir=False
    ):
        if self.is_environment_loaded:
            return
        self.environment_string = self._validate_environment_string(environment_string)
        self._load_configs()
        self._load_env_vars()
        self._init_db()
        self._set_intermediate_files_dir_path(
            override_intermediate_files_dir=override_intermediate_files_dir
        )
        self._init_data_sources()
        self.is_environment_loaded = True

    def filter_data_sources(self, data_sources_ids: List[str]):
        if len(data_sources_ids) == 1 and data_sources_ids[0].strip() == "__all__":
            return self.initialized_data_sources

        filtered_data_sources = []
        for data_source in self.initialized_data_sources:
            print(data_source.config)
            if data_source.config.disabled:
                continue

            if data_source.info.get("id") in data_sources_ids:
                filtered_data_sources.append(data_source)

        if not len(filtered_data_sources):
            raise Exception("No data source found")

        return filtered_data_sources
