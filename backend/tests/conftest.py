from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session
from sqlalchemy_utils import create_database, database_exists

from app import create_app
from data.models import Base, Users, Positions, Events
from data.session import create_session


@pytest.fixture(scope="session")
def db() -> scoped_session:
    db_session: scoped_session = create_session()
    assert db_session.bind is not None
    engine: Engine = db_session.bind.engine
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return db_session


@pytest.fixture(scope="session")
def cleanup_db(db: scoped_session) -> None:
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())


@pytest.fixture(scope="session")
def app_client(cleanup_db: Any) -> Generator[TestClient, None, None]:
    app = create_app()
    yield TestClient(app)


@pytest.fixture()
def create_user(db: scoped_session, create_position: Positions) -> Generator[Users, None, None]:
    user = Users(
        age="18-24",
        gender="F",
        nav_skill=3,
        position=create_position.id,
    )
    db.add(user)
    db.commit()
    yield user


@pytest.fixture()
def create_position(db: scoped_session) -> Generator[Positions, None, None]:
    """
    start = LatLng(55.872179, -4.292532)
    end = LatLng(55.8723, -4.289259)
    lost = LatLng(55.873101, -4.290547)
    start_radius = 0
    lost_radius = 0
    end_radius = 0
    """
    position = Positions(
        start="POINT(55.872179 -4.292532)",
        lost="POINT(55.873101 -4.290547)",
        end="POINT(55.8723 -4.289259)",
        start_radius=0,
        lost_radius=100,
        end_radius=0,
    )
    db.add(position)
    db.commit()
    yield position


@pytest.fixture()
def create_event(db: scoped_session, create_user: Users) -> Generator[Events, None, None]:
    user = create_user
    event = Events(
        user=user.id,
        position=user.position,
        when="This week",
        time_of_day="Morning",
        day_of_week="Monday",
        guidance="Smart Phone/Sat Nav",
        group="No",
        factors="Environment",
        familiarity=1,
        context="",
        explain="",
    )
    db.add(event)
    db.commit()
    yield event
