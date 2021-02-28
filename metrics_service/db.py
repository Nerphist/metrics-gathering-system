from os import environ

from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

db_user = environ.get('POSTGRES_USER', '')
db_password = environ.get('POSTGRES_PASSWORD', '')
db_name = environ.get('POSTGRES_DB', '')
db_host = environ.get('POSTGRES_HOST', '')

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

db = sessionmaker(bind=engine)


class Base:
    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


def get_db() -> Session:
    session = db()
    try:
        yield session
    finally:
        session.close()
