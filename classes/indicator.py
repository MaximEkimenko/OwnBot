import asyncio
import json
from typing import List

from calculate_methods.description_based import get_description_todoist_dict
from calculate_methods.quantity_based import get_quantity_todoist_dict
from indicator_param import IndicatorParam
from todoist_task import TodoistTask
from pathlib import Path
from config import BaseDIR
from db.db_utils import indicator_db_utils


class Indicator:
    """Показатель"""
    def __init__(self,
                 user_id: int,
                 name: str = None,
                 params: IndicatorParam = None):
        self.name = name
        self.params = params
        self.todoist_data: List[TodoistTask] = []
        self.user_id = user_id

    # TODO источник предыдущей версии расчёта проект owneed_bot -
    #  - файл progress_tracker_db_write.py
    #  - функция indicators_write

    # TODO
    #  Виды показателей:
    #      - Складываемые по description одного проекта todoist_task с разделением по литералу
    #       (признаку проекта), например:
    #       словарь соответствия показателей литералам:
    #       projects_keys = {'Study': {'B': 'book', 'A': 'audiobook', 'V': 'video'},
    #                      'Wealth': {'M': 'add_income', 'P': 'poms'}}
    #       Для todoist_task читаем проект, description, литерал; сопоставляем и складываем.
    #       for project in projects_keys:
    #           study_data.update(task_description_read(projects_keys=projects_keys, project=project, today=today));
    #      - Количество выполненных задач внутри определённого проекта в течении суток;
    #      - Операции со значениями из ячеек файлов excel, json файлов и т.д.

    # TODO
    #  1 Метод Indicator.add_json - который добавляет параметры показателя из json файла
    #  2 Метод Indicator.add_params- который добавляет параметры в получением из интерфейса (FSM для Aiogram)
    #  3 Расчёт показателей, агрегация данных;
    #  4 Запись в БД;

    async def calculate_indicators(self):
        """Выполнение расчётов показателей"""
        # метод основанный на описании
        description_based_indicators = await get_description_todoist_dict(self.user_id)

        # количественней метод
        quantity_based = await get_quantity_todoist_dict(self.user_id)


        # агрегация
        indicators = description_based_indicators | quantity_based

        print(indicators)
    async def read_settings(self):
        """Чтение настроек"""


if __name__ == '__main__':
    pass


