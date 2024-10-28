from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Sequence
from sqlalchemy.orm import declarative_base

Base: declarative_base = declarative_base()


@dataclass
class ImageHistoryEntity:
    user_id: int
    file_id: str
    text: str
    datess: datetime


class ImageHistory(Base):
    __tablename__ = 'image_history'
    id = Column(Integer, Sequence('image_id_seq'), primary_key=True)
    user_id = Column(Integer)
    file_id = Column(String)
    text = Column(String)
    datess = Column(DateTime)
