from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from db.database import connection
from db.models import UserModel

from config import settings

from logger_config import log
import asyncio

from sqlalchemy.orm import joinedload
from pprint import pprint


def joined_to_dict(user_model, user_dict: dict, joined_models: list) -> dict:
    """Добавление словарей связанных моделей"""
    for model in joined_models:
        user_dict[user_model.telegram_id].update({repr(model): [data.to_dict() for data in joined_models]})
    return user_dict


@connection
async def create_user(*, telegram_id: int, session: AsyncSession) -> int | None:
    """Создание пользователя"""
    try:
        user = UserModel(telegram_id=telegram_id)
        session.add(user)
        await session.commit()
        return user.id
    except IntegrityError as e:
        await session.rollback()
        log.error(f"Ошибка записи в БД уже существующего пользователя для {telegram_id}", exc_info=e)
        return None


@connection
async def add_user_todoist_token(*, todoist_token: str, user_id: int, session: AsyncSession) -> bool:
    """Добавление todoist_token в БД"""
    stmt = select(UserModel.todoist_token).where(UserModel.id == user_id)
    result = await session.execute(stmt)
    token = result.scalar_one_or_none()

    if token == todoist_token:
        raise ValueError('Такой todoist token уже ведён. Введите новый.')

    query = update(UserModel).values(todoist_token=todoist_token)
    await session.execute(query)
    await session.commit()
    return True


@connection
async def get_user_data_by_telegram_id(*, telegram_id: int, session: AsyncSession) -> dict[str | int, Any] | None:
    """Получение записи пользователя по telegram_id"""

    query = (select(UserModel).where(UserModel.telegram_id == telegram_id)
             .options(joinedload(UserModel.todoist_tasks))
             .options(joinedload(UserModel.tasks))
             .options(joinedload(UserModel.indicators))
             .options(joinedload(UserModel.reports))
             )
    result = await session.execute(query)
    user = result.scalar()

    if not user:
        return None

    user_data = {
        user.telegram_id: user.to_dict()
    }

    for joined_model in (user.todoist_tasks, user.tasks, user.reports, user.indicators):
        joined_to_dict(user_model=user, user_dict=user_data, joined_models=joined_model)

    return user_data

if __name__ == '__main__':
    # asyncio.run(create_user(telegram_id=settings.SUPER_USER_TG_ID))
    # asyncio.run(add_user_todoist_token(todoist_token='48cbdb22977eb9d84368aef673d3c7ba7c0f311a', user_id=1))
    pprint(asyncio.run(get_user_data_by_telegram_id(telegram_id=settings.SUPER_USER_TG_ID)))
    pass
