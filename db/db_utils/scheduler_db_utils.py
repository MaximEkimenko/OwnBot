import asyncio
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import connection
from db.models import ScheduleTask

from logger_config import log


@connection
async def save_reminder_data(*, schedule_params: dict,
                             telegram_user_data: dict,
                             user_id: int,
                             session: AsyncSession) -> bool:
    """Сохранение параметров напоминания"""
    schedule_name = schedule_params.get('name')
    stmt = select(exists().where(ScheduleTask.name == schedule_name))
    result = await session.execute(stmt)
    is_exists = result.scalar()
    if is_exists:
        log.debug('Напоминание {name} уже существует.', name=schedule_name)
        return False

    try:
        pass
        # report = ScheduleTask(**data)
        # session.add(report)
        # await session.commit()
        # log.debug('Данные Напоминания сохранены {name}.', name=schedule_name)
    except Exception as e:
        await session.rollback()
        log.error(f'Ошибка при сохранении напоминания.', exc_info=e)
        log.exception(e)


    return True



if __name__ == '__main__':


    _schedule_params = {



    }

    # {
    #     "trigger": 'cron', "day_of_week": "mon-sun", "hour": 12, "minute": 2,
    #     "id": "send_private",
    #     "reminder_text": "text_first_reminder"
    # },


    _telegram_user_data = {



    }

    asyncio.run(save_reminder_data(schedule_params=_schedule_params,
                                   telegram_user_data=_telegram_user_data,
                                   user_id=1))

