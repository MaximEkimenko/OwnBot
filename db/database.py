"""Настройки работы с БД через sqlAlchemy."""
from typing import Any, Annotated
from datetime import datetime
from collections.abc import Callable, Coroutine

from sqlalchemy import TIMESTAMP, Integer, func
from sqlalchemy.orm import Mapped, DeclarativeBase, class_mapper, declared_attr, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine

from config import settings
from logger_config import log

database_url = settings.db_url
engine = create_async_engine(url=database_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
uniq_string = Annotated[str, mapped_column(unique=True, nullable=False)]  # тип уникальной строки
datetime_format = Annotated[datetime, mapped_column(nullable=False, default="")]  # тип даты


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс моделей sqlAlchemy."""

    __abstract__ = True
    # поля по умолчанию для всех таблиц
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # автоматическое заполнение имени таблицы - имя класса с маленькой буквы
    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        """Имя таблицы по умолчанию."""
        return cls.__name__.lower()

    def to_dict(self) -> dict:
        """Конвертация объекта SQLAlchemy в словарь."""
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}


# def connection(method) -> Coroutine:
def connection(method: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Декоратор для открытия сессии."""
    async def wrapper(*args: list[Any], **kwargs: dict[Any:Any]) -> Callable[..., Coroutine[Any, Any, Any]]:
        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception:
                await session.rollback()
                log.error("Ошибка подключения к БД.")
                raise
            finally:
                await session.close()

    return wrapper
