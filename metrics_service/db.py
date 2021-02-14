from os import environ

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_user = environ.get('POSTGRES_USER', '')
db_password = environ.get('POSTGRES_PASSWORD', '')
db_name = environ.get('POSTGRES_DB', '')
db_host = environ.get('POSTGRES_HOST', '')

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

db = sessionmaker(bind=engine)
Base = declarative_base()
