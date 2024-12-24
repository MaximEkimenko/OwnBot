from collections import defaultdict

from db.db_utils import todoist_task_db_utils
from db.db_utils.indicator_db_utils import get_literal_project_dict
from db.models import TodoistTask
from typing import Sequence
# TODO logger, try-except


async def get_description_todoist_dict(user_id: int) -> dict:
    """Получение словаря задач todoist с для расчёта по description"""
    data = await get_literal_project_dict(user_id=user_id)
    tasks: Sequence[TodoistTask] = await todoist_task_db_utils.get_description_todoist_tasks(literal_dict=data)

    literal_indicator = {}
    for inner_dict in data.values():
        literal_indicator.update(inner_dict)

    indicators_sum_dict = defaultdict(int)

    for task in tasks:
        literal = task.description[0]
        if literal in literal_indicator:
            indicator = literal_indicator[literal]
            indicators_sum_dict[indicator] += int(task.description[1:])

    return dict(indicators_sum_dict)


if __name__ == '__main__':
    pass



