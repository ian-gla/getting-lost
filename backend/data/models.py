import sqlalchemy as sa
import geoalchemy2 as ga
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


schema = "lost"

metadata_obj = MetaData(schema=schema)


class Base(DeclarativeBase):
    metadata = metadata_obj


class Users(Base):
    __tablename__ = "users"

    id = sa.Column("id", sa.Integer, primary_key=True)
    age = sa.Column("age", sa.String, nullable=False)
    gender = sa.Column("gender", sa.String, nullable=False)
    nav_skill = sa.Column("nav_skill", sa.String, nullable=False)
    position = sa.Column(
        "position", sa.Integer, sa.ForeignKey(f"{schema}.positions.id", ondelete="CASCADE"), nullable=False
    )


class Positions(Base):
    __tablename__ = "positions"
    id = sa.Column("id", sa.Integer, primary_key=True)
    start = sa.Column(
        "start",
        ga.types.Geometry(
            geometry_type="POINT",
            srid=4326,
            from_text="ST_GeomFromEWKT",
            spatial_index=True,
        ),
        nullable=True,
    )
    lost = sa.Column(
        "lost",
        ga.types.Geometry(
            geometry_type="POINT",
            srid=4326,
            from_text="ST_GeomFromEWKT",
            spatial_index=True,
        ),
        nullable=True,
    )
    end = sa.Column(
        "end",
        ga.types.Geometry(
            geometry_type="POINT",
            srid=4326,
            from_text="ST_GeomFromEWKT",
            spatial_index=True,
        ),
        nullable=True,
    )
    start_radius = sa.Column("start_radius", sa.Integer)
    lost_radius = sa.Column("lost_radius", sa.Integer)
    end_radius = sa.Column("end_radius", sa.Integer)


class Events(Base):
    __tablename__ = "events"

    id = sa.Column("id", sa.Integer, primary_key=True)
    user = sa.Column(
        "user",
        sa.Integer,
        sa.ForeignKey(f"{schema}.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    position = sa.Column(
        "position", sa.Integer, sa.ForeignKey(f"{schema}.positions.id", ondelete="CASCADE"), nullable=False
    )
    when = sa.Column("when", sa.String(15))
    time_of_day = sa.Column("time_of_day", sa.String(10))
    day_of_week = sa.Column("day_of_week", sa.String(10))
    guidance = sa.Column("guidance", sa.String(20))
    group = sa.Column("group", sa.String(10))
    factors = sa.Column("factors", sa.String(30))
    familiarity = sa.Column("familiarity", sa.Integer)
    context = sa.Column("context", sa.Text)
    explain = sa.Column("explain", sa.Text)
