from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings

# Serverless functions are short-lived and scale out horizontally, so an in-process
# pool would multiply open connections across instances. Open one connection per
# request here and let the database side (Neon/Supabase pooled endpoint) do the pooling.
engine = create_engine(settings.database_url, poolclass=NullPool)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
