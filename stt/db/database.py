from sqlalchemy import create_engine  # , StaticPool,
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from stt.config import get_settings

DATABASE_URL = get_settings().database_url


# SQLALCHEMY_DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_SERVER}/{PG_DB}"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": not DATABASE_URL.startswith("sqlite")},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


async def create_db_and_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
