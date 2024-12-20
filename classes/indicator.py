from typing import List
from indicator_param import IndicatorParam
from todoist_task import TodoistTask


class Indicator:
    """Показатель"""
    def __init__(self, name: str, params: IndicatorParam):
        self.name = name
        self.params = params
        self.todoist_data: List[TodoistTask] = []

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
    #  1 Формирование фйалов параметров индикаторов, с доступом для конечного пользователя;
    #  2 Чтение файлов настроек, инициализация класса параметров;
    #  3 Расчёт показателей, агрегация данных;
    #  4 Запись в БД;


    async def read_settings(self):
        """Чтение настроек"""

