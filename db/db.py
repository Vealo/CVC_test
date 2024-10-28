import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from db.repository import SqlAlchemyImageHistoryRepository

Base: declarative_base = declarative_base()


class DriverDB:
    engine = None
    session_maker = None

    @classmethod
    def create_db(cls, database_url):
        if cls.engine is None and cls.session_maker is None:
            cls.engine = create_engine(f'sqlite:///{database_url}', echo=False)
            cls.session_maker = sessionmaker(bind=cls.engine)
            if not os.path.exists(database_url):
                Base.metadata.create_all(cls.engine)

    @classmethod
    def get_repository(cls) -> SqlAlchemyImageHistoryRepository:
        SqlAlchemyImageHistoryRepository.session_maker_init(cls.session_maker)
        return SqlAlchemyImageHistoryRepository
