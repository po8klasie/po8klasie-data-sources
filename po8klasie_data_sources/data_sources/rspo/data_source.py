import json
from pathlib import Path
from typing import Dict, List

import urllib3

from sqlalchemy.orm import Session

from po8klasie_data_sources.data_sources.rspo.create_institution_records import (
    create_institution_records,
)
from po8klasie_data_sources.data_sources.rspo.fetch import (
    fetch_boroughs_rspo_institution_data,
)
from po8klasie_data_sources.lib.data_source import DataSource, DataSourceConfigBaseModel


class RspoDataSource(DataSource):
    info = {
        "id": "rspo",
        "name": "Rejestr Szkół i Placówek Oświatowych",
        "description": "Rejestr MEIN",
    }

    def create_intermediate_files(self, session: Session):
        urllib3.disable_warnings()
        for project_id, borough_names in self.config.borough_names_per_project.items():
            institution_data = list(
                fetch_boroughs_rspo_institution_data(borough_names, log=self.log)
            )
            with open(self._get_intermediate_file_path(f"{project_id}.json"), "w") as f:
                json.dump(institution_data, f)

    def create_records(self, session: Session):
        for filepath in Path(self.intermediate_files_dir_path).rglob("*.json"):
            with open(filepath, "r") as f:
                institution_data = json.load(f)
                create_institution_records(session, filepath.stem, institution_data)
        session.commit()

    class ConfigModel(DataSourceConfigBaseModel):
        borough_names_per_project: Dict[str, List[str]]
