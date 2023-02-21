from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from config import DATABASE_URL

Base = declarative_base()


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, index=True)
    name_image = Column(String, unique=True, index=True)
    path_to_ndvi = Column(String, nullable=True)
    path_to_image = Column(String, nullable=True)


def connect_db():
    try:
        engine = create_engine(DATABASE_URL, connect_args={})
        session = Session(bind=engine.connect())
        yield session
    finally:
        session.close()


def start_db():
    engine = create_engine(DATABASE_URL, connect_args={})
    session = Session(bind=engine.connect())
    Base.metadata.create_all(bind=engine)
    session.close()
