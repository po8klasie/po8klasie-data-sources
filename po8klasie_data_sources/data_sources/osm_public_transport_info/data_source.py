import json
from pathlib import Path

from po8klasie_fastapi.db.models import RspoInstitution, Institution
from sqlalchemy.orm import Session

from po8klasie_data_sources.cli.cli_logger import cli_logger
from po8klasie_data_sources.data_sources.osm_public_transport_info.fetch import (
    get_public_transport_stops_data_per_institution,
)
from po8klasie_data_sources.data_sources.osm_public_transport_info.model_mapper import (
    add_public_transport_data_to_institution_model,
)
from po8klasie_data_sources.lib.data_source import DataSource, DataSourceConfigBaseModel


class OSMPublicTransportInfoDataSource(DataSource):
    info = {
        "id": "osm_public_transport_info",
        "name": "OpenStreetMap Public Transport Info",
        "description": "OSM",
    }
    current_file = __file__

    def create_intermediate_files(self, session: Session):
        institutions = session.query(RspoInstitution).all()

        count = len(institutions)
        i = 0

        for institution in institutions:
            i += 1
            cli_logger.info(
                f"{i}/{count}. Adding public transport data for institution #{institution.rspo}"
            )
            has_not_succeeded = True

            while has_not_succeeded:
                try:
                    data = list(
                        get_public_transport_stops_data_per_institution(
                            institution=institution,
                            radius=self.config.stop_distance_from_institution,
                        )
                    )
                    with open(
                        self._get_intermediate_file_path(f"{institution.rspo}.json"),
                        "w",
                    ) as f:
                        json.dump(data, f)

                    has_not_succeeded = False
                except Exception as e:
                    print(e)
                    print("Error occurred. Retrying")

    def create_records(self, session: Session):
        for filepath in Path(self.intermediate_files_dir_path).rglob("*.json"):
            with open(filepath, "r") as f:
                stops_data = json.load(f)
                rspo = filepath.stem
                institution = session.query(Institution).filter_by(rspo=rspo).one_or_none()
                if institution:
                    add_public_transport_data_to_institution_model(
                        session, institution, stops_data
                    )
            session.commit()

    class ConfigModel(DataSourceConfigBaseModel):
        stop_distance_from_institution: int
