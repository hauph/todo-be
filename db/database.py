from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_utils import database_exists, create_database
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.environ.get("POSTGRES_USER") or None
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD") or None
POSTGRES_DOMAIN = os.environ.get("POSTGRES_DOMAIN") or None
POSTGRES_DB = os.environ.get("POSTGRES_DB") or None

if (
    POSTGRES_USER is None
    or POSTGRES_PASSWORD is None
    or POSTGRES_DOMAIN is None
    or POSTGRES_DB is None
):
    raise "Missing POSTGRES database information"

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_DOMAIN}/{POSTGRES_DB}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
