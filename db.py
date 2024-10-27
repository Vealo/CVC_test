import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Sequence
from sqlalchemy.orm import sessionmaker, declarative_base, Session

Base: declarative_base = declarative_base()


class ImageHistory(Base):
    __tablename__ = 'image_history'
    id = Column(Integer, Sequence('image_id_seq'), primary_key=True)
    user_id = Column(Integer)
    file_id = Column(String)
    text = Column(String)
    datess = Column(DateTime)


@dataclass
class ImageHistoryEntity:
    user_id: int
    file_id: str
    text: str
    datess: datetime


class ImageHistoryRepository(ABC):
    @abstractmethod
    def add(self, entity: ImageHistoryEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_history(self, user_id: int) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def clear_history(self, user_id: int) -> str:
        raise NotImplementedError


class SqlAlchemyImageHistoryRepository(ImageHistoryRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, entity: ImageHistoryEntity) -> None:
        row = ImageHistory(
            user_id=entity.user_id,
            file_id=entity.file_id,
            text=entity.text,
            datess=entity.datess
        )
        self.session.add(row)
        self.session.commit()

    def get_history(self, user_id: int) -> list[str]:
        result = self.session.query(ImageHistory).filter_by(user_id=user_id).all()
        if result:
            return [f"Дата: {row.datess}\nСообщение: {i + 1}\nРаспознано:\n{row.text}"
                    for i, row in enumerate(result)]
        return ["История пуста."]

    def clear_history(self, user_id: int) -> str:
        deleted_count = self.session.query(ImageHistory).filter_by(user_id=user_id).delete()
        self.session.commit()
        return 'История очищена.' if deleted_count > 0 else "История пуста"


class DriverDB:
    engine = None
    session_maker = None

    @classmethod
    def create_db(cls, database_url):
        if cls.engine is None and cls.session_maker is None:
            cls.engine = create_engine(f'sqlite:///{database_url}', echo=True)
            cls.session_maker = sessionmaker(bind=cls.engine)
            if not os.path.exists(database_url):
                Base.metadata.create_all(cls.engine)

    @classmethod
    def get_repository(cls) -> SqlAlchemyImageHistoryRepository:
        session = cls.session_maker()
        return SqlAlchemyImageHistoryRepository(session)
