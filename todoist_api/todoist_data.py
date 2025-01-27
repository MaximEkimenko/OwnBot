import asyncio

from typing import Any
from datetime import timedelta

import aiohttp

from dateutil.tz import gettz
from dateutil.parser import parse
from todoist_api_python.api_async import TodoistAPIAsync

from config import TIMEZONE, init_timezone_offset
from logger_config import log


async def get_todoist_data(token: str) -> list[dict[str: Any | None]]:
    try:
        """
        Получение данных API Todoist. 
        Для получения выполненных задач используется SYNC API. REST API не умеет работать с 
        is_recurring=True задачами. Ограничение SYNC API - 30 задач за последние сутки.
        Функция возвращает кортеж из выполненных задач за ТЕКУЩИЙ ДЕНЬ в виде словаря с ключами:
        (task: содержание задачи, project: проект задачи, label:метка задачи, done_time: дата время выполнения задачи,
        description: описание задачи)
        """
        api = TodoistAPIAsync(token)
        done_items_url = "https://api.todoist.com/sync/v9/completed/get_all"  # URL получения выполненных задач
        headers = {"Authorization": f"Bearer {token}", "sync_token": "*"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url=done_items_url, headers=headers) as response:
                response_json = await response.json()

        # Проекты из response_json
        projects = {value["id"]: value["name"] for _, value in response_json["projects"].items()}
        # Задачи с датой выполнения из response_json
        tasks = [{"task_id": task["task_id"], "item_id": task["id"], "completed_at": task["completed_at"]}
                 for task in response_json["items"]]
        competed_tasks = []
        timezone_offset = init_timezone_offset()
        # детали задач
        for task_data in tasks:
            api_task = await api.get_task(task_id=task_data["task_id"])
            task = {
                "task": api_task.content,
                "project": projects[api_task.project_id],
                "task_item_id": int(task_data["item_id"]),
                "task_id": int(api_task.id),
                "project_id": int(api_task.project_id),
                "labels": ",".join(api_task.labels),
                "description": api_task.description,
                "completed_at": parse(task_data["completed_at"],
                                      tzinfos=lambda x, y: gettz(TIMEZONE)) + timedelta(hours=timezone_offset),

                "added_at": parse(api_task.created_at,
                                  tzinfos=lambda x, y: gettz(TIMEZONE)) + timedelta(hours=timezone_offset),

                "priority": api_task.priority,
            }
            competed_tasks.append(task.copy())
        return competed_tasks

    except Exception as e:
        log.error("Ошибка в получении выполненных задач от todoist.", exc_info=e)
        log.exception(e)


if __name__ == "__main__":
    res = asyncio.run(get_todoist_data(token="48cbdb22977eb9d84368aef673d3c7ba7c0f311a"))
    for r in res:
        print(r["completed_at"], r["task"])
