from typing import List

from po8klasie_data_sources.cli.cli import cli
from po8klasie_data_sources.lib.data_source import DataSource
from po8klasie_data_sources.lib.environment_manager import EnvironmentManager


class DataManager:
    data_sources: List[DataSource]
    environment_manager: EnvironmentManager

    def __init__(
        self, data_sources: List[DataSource], config_modules: dict[str, DataSource]
    ):
        self.data_sources = data_sources
        self._config_modules = config_modules

    def init_cli(self, file):
        self.environment_manager = EnvironmentManager(
            data_sources=self.data_sources,
            config_modules=self._config_modules,
            file=file,
        )
        cli_context = dict(environment_manager=self.environment_manager)
        cli(obj=cli_context)
