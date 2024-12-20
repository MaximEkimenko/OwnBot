import asyncio
from pprint import pprint
from sqlalchemy import select, update
from db.database import connection
from db.models import TodoistTask
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from todoist_api.todoist_data import get_todoist_data
from logger_config import log


@connection
async def save_todoist_tasks(*, session: AsyncSession, user_id: int, token: str) -> bool:
    """Сохранение в БД данных todoist"""
    # данные todoist
    todoist_data = await get_todoist_data(token)
    if not todoist_data:
        return False

    # добавление FK поля владельца
    for line in todoist_data:
        line.update({'user_id': user_id})
    # данные БД
    stmt_length_limit = len(todoist_data) * 2 + 1  # длина списка данных из БД в зависимости от лимита todoist
    stmt = (select(TodoistTask)
            .where(TodoistTask.user_id == user_id)
            .order_by(TodoistTask.id.desc()).limit(stmt_length_limit))
    result = await session.execute(stmt)
    db_result = result.scalars().all()
    db_data = [line.to_dict() for line in db_result]
    # отличия todoist_data b и db_data
    diff_data = [line for line in todoist_data if
                 not any(line['task_item_id'] == db_line['task_item_id'] for db_line in db_data)]
    # добавление отличительных данных в БД
    if diff_data:
        try:
            data_list = [TodoistTask(**data) for data in diff_data]
            session.add_all(data_list)
            await session.commit()
            log.success(f'задачи todoist {[data['task'] for data in diff_data]} успешно занесены в БД.')
        except IntegrityError as e:
            log.error('Ошибка БД при сохранении задач todoist.')
            log.exception(e)
    else:
        log.info('Выполненные задачи todoist для обновления отсутствуют.')

    return True

if __name__ == '__main__':
    asyncio.run(save_todoist_tasks(token='48cbdb22977eb9d84368aef673d3c7ba7c0f311a', user_id=1))
