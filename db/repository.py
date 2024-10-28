from abc import ABC, abstractmethod

from sqlalchemy.orm import sessionmaker

from db.models import ImageHistory, ImageHistoryEntity


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
    session_maker = None

    @classmethod
    def session_maker_init(cls, session_maker: sessionmaker):
        if cls.session_maker is None:
            cls.session_maker = session_maker

    @classmethod
    def add(cls, entity: ImageHistoryEntity) -> None:
        row = ImageHistory(
            user_id=entity.user_id,
            file_id=entity.file_id,
            text=entity.text,
            datess=entity.datess
        )
        print(row)
        with cls.session_maker() as session:
            session.add(row)
            session.commit()

    @classmethod
    def get_history(cls, user_id: int) -> list[str]:
        with cls.session_maker() as session:
            result = session.query(ImageHistory).filter_by(user_id=user_id).all()
        if result:
            return [f"Дата: {row.datess}\nСообщение: {i + 1}\nРаспознано:\n{row.text}"
                    for i, row in enumerate(result)]
        return ["История пуста."]

    @classmethod
    def clear_history(cls, user_id: int) -> str:
        with cls.session_maker() as session:
            deleted_count = session.query(ImageHistory).filter_by(user_id=user_id).delete()
            session.commit()
        return 'История очищена.' if deleted_count > 0 else "История пуста"
