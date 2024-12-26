import asyncio
import datetime
from pprint import pprint

from sqlalchemy import select, update, or_, func, and_
from db.database import connection
from db.models import TodoistTask
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from todoist_api.todoist_data import get_todoist_data
from logger_config import log
from typing import Sequence
from sqlalchemy import text
from config import today


@connection
async def save_todoist_tasks(*, session: AsyncSession, user_id: int, todoist_token: str) -> str:
    """Сохранение в БД данных todoist"""
    # TODO Разобраться с тем, что в случае обновления по description в result string попадает и diff и update записи
    # данные todoist
    todoist_data = await get_todoist_data(todoist_token)
    result_string = ''
    if not todoist_data:
        return 'Ошибка получения данных todoist, проверьте верность token.'

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

    # записи только за сегодня
    filtered_todoist = [line for line in todoist_data if line['completed_at'].date() == today]
    filtered_db = [line for line in db_data if line['completed_at'].date() == today]

    db_task_ids = {line['task_item_id'] for line in filtered_db}
    db_descriptions = {line['description'] for line in filtered_db}

    # новые записи за сегодня
    diff_data = [line for line in filtered_todoist if line['task_item_id'] not in db_task_ids]
    # обновлённые записи по описанию
    # TODO убедится, что сценарий когда ежедневные задачи (recurring task с одинаковым task_id)
    #  не могут быть закрыты несколько раз в день (ручные задачи будут иметь другой task_id  пойдут в diff_dict),
    #  а значит update не нужен
    # updated_data = [line for line in filtered_todoist if line['description'] not in db_descriptions]

    # добавление отличительных данных в БД
    if diff_data:
        try:
            data_list = [TodoistTask(**data) for data in diff_data]
            session.add_all(data_list)
            await session.commit()
            result_string += f'Записи {[data["task"] for data in diff_data]} успешно сохранены.\n'
            log.success(result_string)
        except IntegrityError as e:
            log.error('Ошибка БД при сохранении.')
            log.exception(e)
    else:
        result_string += 'Задачи todoist для добавления отсутствуют.\n'
        log.info(result_string)
    # TODO удалить лишнее по результату тестов
    # обновление данных с изменённым описанием
    # if updated_data:
    #     try:
    #         for data in updated_data:
    #             stmt = (
    #                 update(TodoistTask)
    #                 .where(TodoistTask.user_id == user_id, TodoistTask.task_item_id == data['task_item_id'])
    #                 .values(description=data['description'])
    #             )
    #             await session.execute(stmt)
    #         await session.commit()
    #         # result_string += f'Записи {[data["task"] for data in updated_data]} успешно обновлены.\n'
    #         log.success(result_string)
    #
    #     except SQLAlchemyError as e:
    #         log.error('Ошибка БД при обновлении.')
    #         log.exception(e)
    # else:
    #     result_string += 'Задачи todoist для обновления отсутствуют.\n'
    #     log.info(result_string)

    return result_string


@connection
async def get_description_todoist_tasks(literal_dict: dict, session: AsyncSession) -> Sequence[TodoistTask]:
    """Получение задач todoist по словарю литералов за текущий день"""
    conditions = []
    for project, data_dict in literal_dict.items():
        # literal = data_dict
        for literal in data_dict.keys():
            conditions.append(
                # Из логики исключено имя проекта # TODO уточнить по результатам проекта
                # В логику Не добавлено имя задачи;
                # Выборка только по уникальному литералу в регулярном выражении
                text(f"TodoistTask.description REGEXP '^{literal}[0-9]*$'")
                # (TodoistTask.project == project) & text(f"TodoistTask.description REGEXP '^{literal}[a-zA-Z0-9]*$'")
            )

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
    # print(project_indicator_dict)
    conditions = []
    for project, _ in project_indicator_dict.items():
        conditions.append(
            (TodoistTask.project == project)
        )
    date_condition = func.date(TodoistTask.completed_at) == today

    query = (
        select(
            TodoistTask.project,
            func.count(TodoistTask.id).label("project_count")
        )
        .where(and_(or_(*conditions), date_condition))
        .group_by(TodoistTask.project)
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
