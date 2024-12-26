import asyncio
from collections import defaultdict

from db.db_utils import todoist_task_db_utils
from db.db_utils.indicator_db_utils import get_literal_project_dict, create_or_update_indicators

from db.models import TodoistTask
from typing import Sequence


# TODO logger, try-except


async def get_description_todoist_dict(user_id: int) -> str:
    """Получение словаря задач todoist с для расчёта по description"""
    data = await get_literal_project_dict(user_id=user_id)
    tasks: Sequence[TodoistTask] = await todoist_task_db_utils.get_description_todoist_tasks(literal_dict=data)
    literal_indicator = {}
    for inner_dict in data.values():
        literal_indicator.update(inner_dict)

    indicators_sum_dict = defaultdict(lambda: {'value': 0, 'params_id': None})

    for task in tasks:
        literal = task.description[0]  # первый символ это литерал
        if literal in literal_indicator:
            indicator = literal_indicator[literal]['indicator_name']
            params_id = literal_indicator[literal]['params_id']
            indicators_sum_dict[indicator]['value'] += int(task.description[1:])
            indicators_sum_dict[indicator]['params_id'] = params_id

    # Сохранение данных
    return await create_or_update_indicators(data=dict(indicators_sum_dict), user_id=user_id)

    # return dict(indicators_sum_dict)


if __name__ == '__main__':
    asyncio.run(get_description_todoist_dict(user_id=1))
