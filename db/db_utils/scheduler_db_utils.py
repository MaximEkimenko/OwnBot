import enums
from sqlalchemy import select, exists, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import connection
from db.models import ScheduleTask
from utils.common_utils import get_flat_dict

from logger_config import log


@connection
async def is_schedule_exists(task_name: str, user_id: int, session: AsyncSession) -> bool:
    """Проверка наличия напоминания"""
    stmt = select(exists().where(ScheduleTask.name == task_name,
                                 ScheduleTask.user_id == user_id
                                 ))
    result = await session.execute(stmt)
    return result.scalar()


@connection
async def save_reminder_data(schedule_params: dict,
                             user_telegram_data: dict,
                             user_id: int,
                             task_type: enums.TaskType,
                             session: AsyncSession) -> bool:
    """Сохранение параметров напоминания"""
    schedule_name = schedule_params.get("id")
    stmt = select(exists().where(ScheduleTask.name == schedule_name,
                                 ScheduleTask.user_id == user_id))
    result = await session.execute(stmt)
    is_exists = result.scalar()
    if is_exists:
        log.debug("Напоминание {name} уже существует.", name=schedule_name)
        return False
    try:
        data = {'schedule_params': schedule_params,
                "user_telegram_data": user_telegram_data,
                "user_id": user_id,
                "task_type": task_type,
                "name": schedule_params["id"]
                }
        report = ScheduleTask(**data)
        session.add(report)
        await session.commit()
        log.debug('Данные Напоминания сохранены {name}.', name=schedule_name)
    except Exception as e:
        await session.rollback()
        log.error(f'Ошибка при сохранении напоминания.', exc_info=e)
        log.exception(e)

    return True


@connection
async def update_reminder_data(session: AsyncSession,
                               schedule_params: dict,
                               user_telegram_data: dict,
                               user_id: int,
                               task_type: enums.TaskType
                               ) -> bool:
    """Обновление параметров напоминания"""
    # обновление данных
    task_name = schedule_params["id"]
    stmt = (
        update(ScheduleTask)
        .where(ScheduleTask.user_id == user_id,
               ScheduleTask.name == task_name)
        .values(
            schedule_params=schedule_params,
            user_telegram_data=user_telegram_data,
            task_type=task_type
        )
    )
    try:
        await session.execute(stmt)
        await session.commit()
        log.debug("Успешное обновление {task} записи в БД.", task=task_name)
    except Exception as e:
        log.error("Ошибка записи данных в БД.", exc_info=e)
        return False

    return True


@connection
async def delete_reminder_data(session: AsyncSession,
                               task_name: str,
                               user_id: int,
                               ) -> bool:
    """Удаление напоминания"""
    stmt = (
        delete(ScheduleTask).where(ScheduleTask.user_id == user_id,
                                   ScheduleTask.name == task_name)
    )
    try:
        await session.execute(stmt)
        await session.commit()
        log.debug("Успешное удаление {task} записи в БД.", task=task_name)
    except Exception as e:
        log.error("Ошибка удаления записи в БД.", exc_info=e)
        return False

    return True


@connection
async def get_scheduler_params(user_id: int, session: AsyncSession):
    """Получение всех запланированных задач пользовался"""
    stmt = select(ScheduleTask).where(ScheduleTask.user_id == user_id)
    result = await session.execute(stmt)
    results = result.scalars().all()
    return [line.to_dict() for line in results]


@connection
async def get_all_users_scheduler_params(session: AsyncSession):
    """Получение всех запланированных задач пользовался"""
    stmt = select(ScheduleTask)
    result = await session.execute(stmt)
    results = result.scalars().all()
    return [line.to_dict() for line in results]
