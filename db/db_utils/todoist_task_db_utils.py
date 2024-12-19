import asyncio
from pprint import pprint

from db.database import connection
from db.models import TodoistTask
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from todoist_api.todoist_data import get_todoist_data
from logger_config import log


@connection
async def save_todoist_tasks(*, session: AsyncSession, user_id: int, token: str):
    data = await get_todoist_data(token)
    for line in data:
        line.update({'user_id': user_id})
    try:

        task_list = [TodoistTask(**task_data) for task_data in data]
        session.add_all(task_list)
        await session.commit()
        return [task.id for task in task_list]
    except IntegrityError as e:
        await session.rollback()
        log.error('Ошибка добавления данных todoist')
        log.exception(e)
        return None

    # pprint(data)
    # try:
    #     users_list = [User(**user_data) for user_data in users_data]
    #     session.add_all(users_list)
    #     await session.commit()
    #     logger.info('Users created successfully')
    #     return [user.id for user in users_list]
    # except IntegrityError as e:
    #     await session.rollback()
    #     logger.error('Error creating users')
    #     logger.exception(e)
    #     return None


if __name__ == '__main__':
    asyncio.run(save_todoist_tasks(token='48cbdb22977eb9d84368aef673d3c7ba7c0f311a', user_id=1))
