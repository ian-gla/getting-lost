import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from .models import Base

load_dotenv()
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_url = os.environ.get("database_url")
engine = create_engine(db_url, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

