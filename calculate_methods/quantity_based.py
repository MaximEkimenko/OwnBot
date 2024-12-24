import asyncio

from db.db_utils.indicator_db_utils import get_project_indicator_dict
from db.db_utils.todoist_task_db_utils import get_quantity_todoist_task
# TODO logger, try-except


async def get_quantity_todoist_dict(user_id: int):
    """Расчёт показателей по количеству"""
    project_indicator_dict = await get_project_indicator_dict(user_id=user_id)
    quantity_todoist_dict = dict()
    tasks = await get_quantity_todoist_task(project_indicator_dict)
    for task in tasks:
        quantity_todoist_dict[project_indicator_dict[task[0]]] = task[1]

    return quantity_todoist_dict


if __name__ == '__main__':
    asyncio.run(get_quantity_todoist_dict(user_id=1))

