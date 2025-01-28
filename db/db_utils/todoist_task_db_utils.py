"""Утилиты работы с БД для записей полученных из todoist api."""
from collections.abc import Sequence

from sqlalchemy import or_, and_, func, text, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from config import init_today
from db.models import TodoistTask
from db.database import connection
from logger_config import log
from todoist_api.todoist_data import get_todoist_data


@connection
async def save_todoist_tasks(*, session: AsyncSession, user_id: int, todoist_token: str) -> str | None:
    """Сохранение в БД данных todoist."""
    # данные todoist
    today = init_today()
    todoist_data = await get_todoist_data(todoist_token)
    result_string = ""
    if not todoist_data:
        return None

    # добавление FK поля владельца
    for line in todoist_data:
        line.update({"user_id": user_id})
    # данные БД
    stmt_length_limit = len(todoist_data) * 2 + 1  # длина списка данных из БД в зависимости от лимита todoist
    stmt = (select(TodoistTask)
            .where(TodoistTask.user_id == user_id)
            .order_by(TodoistTask.id.desc()).limit(stmt_length_limit))
    result = await session.execute(stmt)
    db_result = result.scalars().all()
    db_data = [line.to_dict() for line in db_result]

    # записи только за сегодня
    filtered_todoist = [line for line in todoist_data if line["completed_at"].date() == today]
    filtered_db = [line for line in db_data if line["completed_at"].date() == today]

    db_task_ids = {line["task_item_id"] for line in filtered_db}

    # новые записи за сегодня
    diff_data = [line for line in filtered_todoist if line["task_item_id"] not in db_task_ids]

    # добавление отличительных данных в БД
    if diff_data:
        try:
            data_list = [TodoistTask(**data) for data in diff_data]
            session.add_all(data_list)
            await session.commit()
            result_string += f'Задачи {[data["task"] for data in diff_data]} успешно сохранены.\n'
            log.success(result_string)
        except IntegrityError as e:
            log.error("Ошибка БД при сохранении.")
            log.exception(e)
    else:
        result_string += "Задачи todoist для добавления отсутствуют.\n"
        log.info(result_string)

    return result_string


@connection
async def get_description_todoist_tasks(literal_dict: dict, session: AsyncSession) -> Sequence[TodoistTask]:
    """Получение задач todoist по словарю литералов за текущий день."""
    # TODO здесь нужен user_id?
    today = init_today()

    conditions = [
        text(f"TodoistTask.description REGEXP '^{literal}[0-9]*$'")
        for data_dict in literal_dict.values()
        for literal in data_dict
    ]

    date_condition = func.date(TodoistTask.completed_at) == today
    query = select(TodoistTask).where(and_(or_(*conditions), date_condition))

    try:
        result = await session.execute(query)
        tasks = result.scalars().all()
    except IntegrityError as e:
        log.error("Ошибка БД при получении задач todoist по словарю литералов.", exc_info=e)
        raise

    return tasks


@connection
async def get_quantity_todoist_task(project_indicator_dict: dict, session: AsyncSession) -> Sequence:
    """Получение задач todoist по словарю показателей за текущий день."""
    today = init_today()
    # условия
    project_conditions = [TodoistTask.project == project for project in project_indicator_dict]
    date_condition = func.date(TodoistTask.completed_at) == today

    query = (
        select(
            TodoistTask.project,
            func.count(TodoistTask.id).label("project_count"),
        )
        .where(and_(or_(*project_conditions), date_condition))
        .group_by(TodoistTask.project)
    )

    try:
        result = await session.execute(query)
        tasks = result.all()
    except IntegrityError as e:
        log.error("Ошибка БД при получении задач todoist по словарю проектов.", exc_info=e)
        raise

    return tasks
