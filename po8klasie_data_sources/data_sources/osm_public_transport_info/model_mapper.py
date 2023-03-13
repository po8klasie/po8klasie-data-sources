from sqlalchemy.exc import NoResultFound

from po8klasie_fastapi.db.models import (
    PublicTransportStop,
    PublicTransportRoute,
    InstitutionPublicTransportStopAssociation,
)


def map_public_transport_route_to_model(db, route_data):
    osm_id = route_data["osm_id"]

    try:
        route_match = db.query(PublicTransportRoute).filter_by(osm_id=osm_id).one()
        return route_match
    except NoResultFound:
        return PublicTransportRoute(
            osm_id=osm_id,
            name=route_data["name"],
            route_from=route_data["route_from"],
            route_to=route_data["route_to"],
            ref=route_data["ref"],
            type=route_data["type"],
            operator=route_data["operator"],
        )


def map_public_transport_stop_to_model(db, stop_data):
    osm_id = stop_data["osm_id"]
    try:
        stop_match = db.query(PublicTransportStop).filter_by(osm_id=osm_id).one()
        return stop_match
    except NoResultFound:
        public_transport_routes = [
            map_public_transport_route_to_model(db, route_data)
            for route_data in stop_data["public_transport_routes"]
        ]

        return PublicTransportStop(
            osm_id=osm_id,
            name=stop_data["name"],
            latitude=stop_data["latitude"],
            longitude=stop_data["longitude"],
            public_transport_routes=public_transport_routes,
        )


def add_public_transport_data_to_institution_model(db, institution, data):
    for stop in data:
        assoc = InstitutionPublicTransportStopAssociation(
            distance=stop["distance"],
            radius=stop["radius"],
            public_transport_stop=map_public_transport_stop_to_model(
                db, stop["public_transport_stop"]
            ),
        )
        institution.public_transport_stops.append(assoc)
