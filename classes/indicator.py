import asyncio
import json
from typing import List

from calculate_methods.description_based import get_description_todoist_dict
from calculate_methods.quantity_based import get_quantity_todoist_dict
from calculate_methods.pdf_based import pdf_indicator_to_db
from classes.indicator_param import IndicatorParam
from classes.todoist_task import TodoistTask
from io import BytesIO
from db.db_utils.indicator_db_utils import get_indicator_params_id_dict, create_or_update_indicators
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

    async def calculate_save_indicators(self) -> tuple:
        """Выполнение расчётов показателей для записи в БД"""
        # метод основанный на описании
        description_based_result = await get_description_todoist_dict(self.user_id)
        # количественней метод
        quantity_result = await get_quantity_todoist_dict(self.user_id)

        return description_based_result, quantity_result

    async def verificate_indicators(self, indicators_to_update: dict) -> dict:
        """Валидация показателей"""
        exist_indicators = await get_indicator_params_id_dict(user_id=self.user_id)

        valid_indicators = dict()
        for indicator_to_update, indicator_value in indicators_to_update.items():
            if indicator_to_update not in exist_indicators:
                return {'*failed': indicator_to_update}
            # если все показатели верные
            valid_indicators[indicator_to_update] = {'value': indicator_value,
                                                     'params_id': exist_indicators[indicator_to_update]}
        return valid_indicators

    async def pdf_save_indicators(self, file_data: BytesIO):
        """Выполнение расчёта показателей из pdf и запись в БД"""
        return await pdf_indicator_to_db(self.user_id, file_data)

    async def manual_update_save_indicators(self, indicator_data):
        """Сохранение данных из команды update"""
        return await create_or_update_indicators(self.user_id, data=indicator_data)


if __name__ == '__main__':
    pass
