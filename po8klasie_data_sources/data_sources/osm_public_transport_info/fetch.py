import overpy
from geopy import distance as geopy_distance

api = overpy.Overpass()

overpass_query = """
        (
            node(around:{radius},{lat},{lng})["public_transport"="stop_position"];
            relation(bn)["route"];
        );
        out body;
"""


def get_nearby_stops_and_routes(radius, lat, lng):
    return api.query(overpass_query.format(radius=radius, lat=lat, lng=lng))


def map_node_to_public_transport_stop_data(node):
    osm_id = str(node.id)
    return dict(
        osm_id=osm_id,
        name=node.tags.get("name"),
        latitude=float(node.lat),
        longitude=float(node.lon),
        public_transport_routes=[],
    )


def map_relation_to_public_transport_route_data(relation):
    osm_id = str(relation.id)
    return dict(
        osm_id=osm_id,
        name=relation.tags.get("name"),
        route_from=relation.tags.get("from"),
        route_to=relation.tags.get("to"),
        ref=relation.tags.get("ref"),
        type=relation.tags.get("route"),
        operator=relation.tags.get("operator"),
    )


def get_stop_id_from_relation_members(members, stop_ids):
    member_ids = set(str(member.ref) for member in members)
    return next(iter(stop_ids.intersection(member_ids) or []), None)


def calc_distance(institution, stop):
    return geopy_distance.geodesic(
        (institution.longitude, institution.latitude),
        (stop["longitude"], stop["latitude"]),
    ).meters


def get_public_transport_stops_data_per_institution(institution, radius):
    result = get_nearby_stops_and_routes(
        radius=radius, lat=institution.latitude, lng=institution.longitude
    )

    stops_mapping = {}

    for node in result.nodes:
        stop = map_node_to_public_transport_stop_data(node)
        stops_mapping[stop["osm_id"]] = stop

    stop_ids = set(stops_mapping.keys())

    for relation in result.relations:
        stop_id = get_stop_id_from_relation_members(
            members=relation.members, stop_ids=stop_ids
        )

        if any([not stop_id, stop_id not in stops_mapping]):
            continue

        route = map_relation_to_public_transport_route_data(relation)

        stops_mapping[stop_id]["public_transport_routes"].append(route)

    for stop in stops_mapping.values():
        yield dict(
            rspo=institution.rspo,
            distance=calc_distance(institution, stop),
            public_transport_stop=stop,
            radius=radius,
        )
