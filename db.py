import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Sequence, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class ImageHistory(Base):
    __tablename__ = 'image_history'
    id = Column(Integer, Sequence('image_id_seq'), primary_key=True)
    user_id = Column(String)
    datess = Column(DateTime, default=datetime.today())
    file_id = Column(String)
    text = Column(String)

class DriverDB:
    def __init__(self, db_url='history.db'):
        self.DATABASE_URL =db_url
        self.engine = create_engine(f'sqlite:///{db_url}', echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.Base = declarative_base()
        self.session = self.Session()

    def create_db(self):
        if not os.path.exists(self.DATABASE_URL):
            Base.metadata.create_all(self.engine)

    def add(self, file_id: str, text: str, user_id: int) -> None:
        new_entry = ImageHistory(file_id=file_id, text=text, user_id=user_id)
        self.session.add(new_entry)
        self.session.commit()

    def history(self, user_id: int) -> list[str, ]:
        result = list(self.session.query(ImageHistory).filter_by(user_id=user_id))
        if result:
            text = ["История обработанных изображений.", ]
            for number, row in enumerate(result, start=1):
                text.append(f"Дата: {row.datess}\nСообщение: {number}\nРаспознано:\n{row.text}")
            return text
        return ["История пуста.",]

    def clear(self, user_id: int) -> str:
        try:
            self.session.query(ImageHistory).filter_by(user_id=user_id).delete()
            self.session.commit()
            return 'История очищена.'
        except Exception as e:
            return 'При удалении возникла ошибка.'
