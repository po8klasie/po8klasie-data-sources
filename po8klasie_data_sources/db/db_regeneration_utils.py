# flake8: noqa
from sqlalchemy import MetaData


def drop_all(engine):
    meta = MetaData(bind=engine)
    meta.reflect()

    omit = ["spatial_ref_sys"]  # required by postgis

    for tbl in reversed(meta.sorted_tables):
        if str(tbl) not in omit:
            engine.execute(f"DROP TABLE IF EXISTS {tbl}")


def create_all(engine):
    from db.models import Base

    Base.metadata.reflect(bind=engine)
    Base.metadata.create_all(bind=engine)
