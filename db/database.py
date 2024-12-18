from datetime import datetime
from typing import Annotated
from sqlalchemy import func, TIMESTAMP, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declared_attr, class_mapper
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession


from config import settings

import logging

logger = logging.getLogger(__name__)

database_url = settings.db_url
engine = create_async_engine(url=database_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
uniq_string = Annotated[str, mapped_column(unique=True, nullable=False)]  # тип уникальной строки
datetime_format = Annotated[datetime, mapped_column(nullable=False, default='')]  # тип даты


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    # поля по умолчанию для всех таблиц
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    # автоматическое заполнение имени таблицы - имя класса с маленькой буквы
    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def to_dict(self) -> dict:
        """Конвертация объекта SQLAlchemy в словарь"""
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}


def connection(method):
    """Декоратор для открытия сессии"""
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                logger.error("Ошибка подключения к БД.")
                raise e
            finally:
                await session.close()

    return wrapper
