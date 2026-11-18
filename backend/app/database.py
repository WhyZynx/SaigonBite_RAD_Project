import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import declarative_base, sessionmaker

project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


def database_url_from_environment():
    configured_url = os.getenv("DATABASE_URL")
    if configured_url:
        # URL.create safely quotes reserved characters when SQLAlchemy renders it.
        return make_url(configured_url)
    return URL.create(
        drivername=os.getenv("DB_DRIVER", "mysql+pymysql"),
        username=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD") or None,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "SaigonBiteDB"),
        query={"charset": "utf8mb4"},
    )


SQLALCHEMY_DATABASE_URL = database_url_from_environment()

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
