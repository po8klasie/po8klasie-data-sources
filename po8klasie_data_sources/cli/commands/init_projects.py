from po8klasie_data_sources.lib.environment_manager import EnvironmentManager
from db.models import Project


def init_projects(
    environment_manager: EnvironmentManager,
):
    with environment_manager.db.session() as session:
        for project_config in environment_manager.config.PROJECT_CONFIGS:
            session.add(Project(**project_config))
        session.commit()
