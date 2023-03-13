from po8klasie_data_sources.lib.environment_manager import EnvironmentManager

from po8klasie_data_sources.project_configs.model_mapper import (
    create_project_model_instance,
)


def init_projects(
    environment_manager: EnvironmentManager,
):
    with environment_manager.db.session() as session:
        for project_config in environment_manager.config.PROJECT_CONFIGS:
            session.add(create_project_model_instance(project_config))
        session.commit()
