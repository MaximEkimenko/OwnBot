from datetime import timedelta
from typing import Any
from dateutil.parser import parse
import aiohttp
import asyncio
from pprint import pprint

from config import TIME_ZONE
from todoist_api_python.api_async import TodoistAPIAsync
from logger_config import log


# TODO обойти ограничение в 30 выполненных задач за последние сутки:
#  делать выгрузку на фоне по сигналу при выполнении (отправке команды?).
#  Или по расписанию несколько раз в день (каждый час?).


async def get_todoist_data(token: str) -> list[dict[str: Any | None]]:
    try:
        """
        Полк учение данных API Todoist. 
        Для получения выполненных задач используется SYNC API. REST API не умеет работать с 
        is_recurring=True задачами. Ограничение SYNC API - 30 задач за последние сутки.
        Функция возвращает кортеж из выполненных задач за ТЕКУЩИЙ ДЕНЬ в виде словаря с ключами:
        (task: содержание задачи, project: проект задачи, label:метка задачи, done_time: дата время выполнения задачи,
        description: описание задачи)
        """
        api = TodoistAPIAsync(token)
        done_items_url = 'https://api.todoist.com/sync/v9/completed/get_all'  # URL получения выполненных задач
        headers = {"Authorization": f'Bearer {token}', "sync_token": '*'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url=done_items_url, headers=headers) as response:
                response_json = await response.json()

        # Проекты из response_json
        projects = {value['id']: value['name'] for _, value in response_json['projects'].items()}
        # Задачи с датой выполнения из response_json
        tasks = [{'task_id': task['task_id'], 'item_id': task['id'], 'completed_at': task['completed_at']}
                 for task in response_json['items']]
        competed_tasks = []
        # детали задач
        for task_data in tasks:
            # TODO проблема с is_recurring task они обновляются постоянно, даже когда не выполнены. т.к.
            #  task_id не меняется.
            api_task = await api.get_task(task_id=task_data['task_id'])
            # pprint(api_task)
            task = {
                'task': api_task.content,
                'project': projects[api_task.project_id],
                'task_item_id': int(task_data['item_id']),
                'task_id': int(api_task.id),
                'project_id': int(api_task.project_id),
                'labels': ','.join(api_task.labels),
                'description': api_task.description,
                'completed_at': parse(task_data['completed_at'], ignoretz=True) + timedelta(hours=TIME_ZONE),
                'added_at': parse(api_task.created_at, ignoretz=True) + timedelta(hours=TIME_ZONE),

                'priority': api_task.priority,
            }
            competed_tasks.append(task.copy())
        return competed_tasks

    except Exception as e:
        log.error('Ошибка в получении выполненных задач от todoist.')
        log.exception(e)


if __name__ == '__main__':
    pprint(asyncio.run(get_todoist_data(token='48cbdb22977eb9d84368aef673d3c7ba7c0f311a')))
