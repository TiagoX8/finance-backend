import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")

    if not url:
        raise ValueError("DATABASE_URL não configurada no ambiente")

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    return url


DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()