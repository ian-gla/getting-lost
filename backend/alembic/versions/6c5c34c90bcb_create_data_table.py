"""create data table

Revision ID: 6c5c34c90bcb
Revises:
Create Date: 2025-01-08 12:32:48.659886

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2 as ga


# revision identifiers, used by Alembic.
revision: str = "6c5c34c90bcb"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

schema = "lost"


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("age", sa.Integer, nullable=False),
        sa.Column("gender", sa.Integer, nullable=False),
        sa.Column("nav_skill", sa.Integer, nullable=False),
        schema=schema,
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user",
            sa.Integer,
            sa.ForeignKey(f"{schema}.users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "start",
            ga.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                spatial_index=True,
            ),
            nullable=True,
        ),
        sa.Column(
            "lost",
            ga.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                spatial_index=True,
            ),
            nullable=True,
        ),
        sa.Column(
            "end",
            ga.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                spatial_index=True,
            ),
            nullable=True,
        ),
        sa.Column("start_radius", sa.Integer),
        sa.Column("lost_radius", sa.Integer),
        sa.Column("end_radius", sa.Integer),
        sa.Column("when", sa.String(15)),
        sa.Column("time_of_day", sa.String(10)),
        sa.Column("day_of_week", sa.String(10)),
        sa.Column("guidance", sa.String(20)),
        sa.Column("group", sa.String(10)),
        sa.Column("factors", sa.String(30)),
        sa.Column("familiarity", sa.Integer),
        sa.Column("context", sa.Text),
        sa.Column("explain", sa.Text),
        schema=schema,
    )


def downgrade() -> None:
    op.drop_table("users", schema=schema)
    op.drop_table("events", schema=schema)
    op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE;")
    op.execute("DROP EXTENSION IF EXISTS postgis CASCADE;")
