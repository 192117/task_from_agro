from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
import os


db = create_engine(os.environ["URI_DB"])
db.connect()

Base = declarative_base()

class Fields(Base):
    __tablename__ = 'fields'
    __tableargs__ = {
        'comment': 'Поля.'
    }
    id = Column(Integer, nullable=False, primary_key=True, unique=True, autoincrement=True)
    name = Column(String, unique=True, comment="Name field.")
    data = Column(Text, comment="Information about field.")

Base.metadata.create_all(db)
# Base.metadata.drop_all(db) # Удалить таблицы в БД.