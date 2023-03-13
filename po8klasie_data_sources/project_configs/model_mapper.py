from po8klasie_fastapi.app.project.models import Project
from po8klasie_fastapi.app.project.schemas import ProjectSchema


def create_project_model_instance(data):
    validated_data = ProjectSchema.parse_obj(data)
    return Project(
        project_id=validated_data.project_id,
        project_name=validated_data.project_name,
        school_view_config=validated_data.school_view_config.dict(),
        search_view_config=validated_data.search_view_config.dict(),
    )
