from functools import lru_cache
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import PendingRollbackError
import os

from config import get_settings

db_url = os.getenv("test_database_url")
if db_url:
    _engine = create_engine(db_url, pool_pre_ping=True)
else:
    _engine = create_engine(get_settings().database_url.unicode_string(), pool_pre_ping=True)


@lru_cache
def create_session(engine=None) -> scoped_session:
    if not engine:
        engine = _engine
    Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return Session


def get_session(engine=None) -> Generator[scoped_session, None, None]:
    Session = create_session(engine)
    try:
        yield Session
    except PendingRollbackError:
        scoped_session.rollback()
    finally:
        Session.remove()
