import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Sequence, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

Base: declarative_base = declarative_base()

class ImageHistory(Base):
    __tablename__ = 'image_history'
    id = Column(Integer, Sequence('image_id_seq'), primary_key=True)
    user_id = Column(String)
    datess = Column(DateTime, default=datetime.today())
    file_id = Column(String)
    text = Column(String)

class DriverDB:
    engine = None
    session_maker = None
    @classmethod
    def create_db(cls, DATABASE_URL):
        if cls.engine is None and cls.session_maker is None:
            cls.engine = create_engine(f'sqlite:///{DATABASE_URL}', echo=False)
            cls.session_maker = sessionmaker(bind=cls.engine)
        if not os.path.exists(DATABASE_URL):
            Base.metadata.create_all(cls.engine)

    @classmethod
    def add(cls, file_id: str, text: str, user_id: int) -> None:
        with cls.session_maker() as session:
            row = ImageHistory(file_id=file_id, text=text, user_id=user_id)
            session.add(row)
            session.commit()

    @classmethod
    def history(cls, user_id: int) -> list[str, ]:
        with cls.session_maker() as session:
            result = list(session.query(ImageHistory).filter_by(user_id=user_id))
            if result:
                text = ["История обработанных изображений.", ]
                for number, row in enumerate(result, start=1):
                    text.append(f"Дата: {row.datess}\nСообщение: {number}\nРаспознано:\n{row.text}")
            else:
                text = ["История пуста.", ]
        return text

    @classmethod
    def clear(cls, user_id: int) -> str:
        result = "'При удалении возникла ошибка.'"
        with cls.session_maker() as session:
            session.query(ImageHistory).filter_by(user_id=user_id).delete()
            session.commit()
            result = 'История очищена.'
        return result