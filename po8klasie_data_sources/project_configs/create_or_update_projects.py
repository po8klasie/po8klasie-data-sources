from po8klasie_fastapi.app.project.schemas import ProjectSchema

from po8klasie_data_sources.lib.environment_manager import EnvironmentManager

from po8klasie_fastapi.app.project.models import Project


def create_project_model_args(data):
    validated_data = ProjectSchema.parse_obj(data)
    return dict(
        project_id=validated_data.project_id,
        project_name=validated_data.project_name,
        school_view_config=validated_data.school_view_config.dict(),
        search_view_config=validated_data.search_view_config.dict(),
    )


def create_or_update_projects(
        environment_manager: EnvironmentManager,
):
    with environment_manager.db.session() as session:
        for project_config_data in environment_manager.config.PROJECT_CONFIGS:
            project_id = project_config_data["project_id"]
            db_project_config = session.query(Project).filter(
                Project.project_id == project_id)

            model_args = create_project_model_args(project_config_data)

            if not db_project_config.one_or_none():
                db_project_config = Project(**model_args)
            else:
                db_project_config.update(**model_args)

            session.add(db_project_config)
        session.commit()
