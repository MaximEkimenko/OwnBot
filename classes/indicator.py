from typing import List
from indicator_param import IndicatorParam
from todoist_task import TodoistTask


class Indicator:
    """Показатель"""
    def __init__(self, name: str, params: IndicatorParam):
        self.name = name
        self.params = params
        self.todoist_data: List[TodoistTask] = []

    def update_indicator(self):
        # Логика обновления индикатора
        pass

    def calculate_indicators(self, params, todoist_data):
        # Логика расчета индикаторов
        pass
