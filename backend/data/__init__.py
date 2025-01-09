import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_url = os.environ.get("database_url")
engine = create_engine(db_url, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

from data.db import CrudTable
