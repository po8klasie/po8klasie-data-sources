import shapely.geometry

from po8klasie_fastapi.db.models import SecondarySchoolInstitution
from po8klasie_data_sources.data_sources.rspo.model_mapper import (
    create_model_from_rspo_institution_data,
)


def create_institution_records(db, project_id: str, data):
    for institution_data in data:
        institution = SecondarySchoolInstitution(
            rspo_institution=create_model_from_rspo_institution_data(institution_data),
            available_languages=[],
            available_extended_subjects=[],
            points_stats_max=1000,
            points_stats_min=-1,
            project_id=project_id,
        )

        institution.geometry = shapely.geometry.Point(
            map(
                float,
                (
                    institution.rspo_institution.longitude,
                    institution.rspo_institution.latitude,
                ),
            )
        ).wkt

        db.add(institution)
