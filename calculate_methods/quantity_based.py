import asyncio
from collections import defaultdict
from pprint import pprint

from db.db_utils.indicator_db_utils import get_project_indicator_dict, create_or_update_indicators
from db.db_utils.todoist_task_db_utils import get_quantity_todoist_task


# TODO logger, try-except


async def get_quantity_todoist_dict(user_id: int) -> str:
    """Расчёт показателей по количеству"""
    project_indicator_dict = await get_project_indicator_dict(user_id=user_id)
    tasks = await get_quantity_todoist_task(project_indicator_dict)
    quantity_todoist_dict = defaultdict(lambda: {'value': 0, 'params_id': None})

    for task in tasks:
        indicator_data = project_indicator_dict[task[0]]
        indicator_name = indicator_data['indicator_name']
        params_id = indicator_data['params_id']
        quantity_todoist_dict[indicator_name]['value'] = task[1]
        quantity_todoist_dict[indicator_name]['params_id'] = params_id

    return await create_or_update_indicators(data=dict(quantity_todoist_dict), user_id=user_id)

    # return dict(quantity_todoist_dict)


if __name__ == '__main__':
    asyncio.run(get_quantity_todoist_dict(user_id=1))
