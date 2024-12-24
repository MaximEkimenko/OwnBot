import asyncio
import datetime
from pprint import pprint

from sqlalchemy import select, update, or_, func, and_
from db.database import connection
from db.models import TodoistTask
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from todoist_api.todoist_data import get_todoist_data
from logger_config import log
from typing import Sequence
from sqlalchemy import text


@connection
async def save_todoist_tasks(*, session: AsyncSession, user_id: int, todoist_token: str) -> bool:
    """Сохранение в БД данных todoist"""
    # данные todoist
    todoist_data = await get_todoist_data(todoist_token)
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

    today = datetime.date.today() - datetime.timedelta(days=1)
    # Отфильтруем записи в db_data только за today
    # filtered_db_data = [line for line in todoist_data if line['completed_at'].date() == today]
    # #
    # # # Проверим отличия todoist_data и filtered_db_data
    # diff_data = [
    #     line for line in todoist_data
    #     if not any(line['task_item_id'] == db_line['task_item_id'] for db_line in filtered_db_data)
    # ]
    # pprint(diff_data)
    # TODO ЗАГРУЖАТЬ ТОЛЬКО TODAY
    diff_data = [
        line for line in todoist_data
        if all(
            line['task_item_id'] != db_line['task_item_id']
            and line['completed_at'].date() == today
            for db_line in db_data
        )
    ]


    # отличия todoist_data b и db_data
    # diff_data = [line for line in todoist_data if
    #              not any(line['task_item_id'] == db_line['task_item_id']
    #                      # and line['completed_at'].date() == today
    #                      for db_line in db_data)]


    #
    # diff_data = [line for line in todoist_data if
    #              all(line['task_item_id'] != db_line['task_item_id']
    #                      and line['completed_at'].date() == today
    #                      for db_line in db_data)]

    # обновления в данных, которые уже есть
    # updated_data = [line for line in todoist_data if
    #                 not any(line['description'] == db_line['description'] for db_line in db_data)]



    updated_data = [
        line for line in todoist_data
        if all(
            line['description'] != db_line['description']
            and line['completed_at'].date() == today
            for db_line in db_data
        )
    ]


    pprint(updated_data)

    # добавление отличительных данных в БД
    if diff_data:
        try:
            data_list = [TodoistTask(**data) for data in diff_data]
            session.add_all(data_list)
            await session.commit()
            log.success(f'задачи todoist {[data["task"] for data in diff_data]} успешно занесены в БД.')
        except IntegrityError as e:
            log.error('Ошибка БД при сохранении задач todoist.')
            log.exception(e)
    else:
        log.info('Выполненные задачи todoist для обновления отсутствуют.')

    return True


@connection
async def get_description_todoist_tasks(literal_dict: dict, session: AsyncSession) -> Sequence[TodoistTask]:
    """Получение задач todoist по словарю литералов за текущий день"""
    conditions = []
    for project, literals in literal_dict.items():
        for literal in literals:
            conditions.append(
                # Из логики исключено имя проекта # TODO уточнить по результатам проекта
                # В логику Не добавлено имя задачи;
                # Выборка только по уникальному литералу в регулярном выражении
                text(f"TodoistTask.description REGEXP '^{literal}[0-9]*$'")
                # (TodoistTask.project == project) & text(f"TodoistTask.description REGEXP '^{literal}[a-zA-Z0-9]*$'")
            )

    today = datetime.date.today() - datetime.timedelta(days=1)
    date_condition = func.date(TodoistTask.completed_at) == today

    query = select(TodoistTask).where(and_(or_(*conditions), date_condition))

    try:
        result = await session.execute(query)
        tasks = result.scalars().all()
    except IntegrityError as e:
        log.error('Ошибка БД при получении задач todoist по словарю литералов.')
        log.exception(e)
        raise e

    return tasks


@connection
async def get_quantity_todoist_task(project_indicator_dict: dict, session: AsyncSession):
    """Получение задач todoist по словарю показателей за текущий день"""
    conditions = []
    for project, indicator in project_indicator_dict.items():
        conditions.append(
            (TodoistTask.project == project)
        )

    today = datetime.date.today() - datetime.timedelta(days=1)
    date_condition = func.date(TodoistTask.completed_at) == today

    # query = select(TodoistTask).where(and_(or_(*conditions), date_condition))
    project_count_subquery = (
        select(
            TodoistTask.project,
            func.count(TodoistTask.id).label('project_count')
        )
        .group_by(TodoistTask.project)
        .subquery()
    )

    query = (
        select(
            TodoistTask,
            project_count_subquery.c.project_count  # Количество задач для каждого проекта
        )
        .join(
            project_count_subquery,
            TodoistTask.project == project_count_subquery.c.project
        )
        .where(and_(or_(*conditions), date_condition))
    )

    query = (
        select(
            TodoistTask.project,  # Название проекта
            func.count(TodoistTask.id).label("project_count")  # Количество задач
        )
        .where(and_(or_(*conditions), date_condition))
        .group_by(TodoistTask.project)  # Группировка по проекту
    )

    try:
        result = await session.execute(query)
        tasks = result.all()
    except IntegrityError as e:
        log.error('Ошибка БД при получении задач todoist по словарю проектов.')
        log.exception(e)
        raise e

    return tasks


if __name__ == '__main__':
    pass
