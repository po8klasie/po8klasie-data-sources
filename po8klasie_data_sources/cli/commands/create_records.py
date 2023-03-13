from typing import List
from po8klasie_data_sources.lib.environment_manager import EnvironmentManager


def create_records(
    environment_manager: EnvironmentManager, data_sources_ids: List[str]
):
    with environment_manager.db.session() as session:
        for data_source in environment_manager.filter_data_sources(
            data_sources_ids=data_sources_ids
        ):
            data_source.create_records(session=session)
        session.commit()
