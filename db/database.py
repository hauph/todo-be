from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_utils import database_exists, create_database
from utils.env_loader import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DOMAIN,
    POSTGRES_DB,
)

if (
    POSTGRES_USER is None
    or POSTGRES_PASSWORD is None
    or POSTGRES_DOMAIN is None
    or POSTGRES_DB is None
):
    raise BaseException("Missing POSTGRES database information")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_DOMAIN}/{POSTGRES_DB}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
