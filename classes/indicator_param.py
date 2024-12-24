import asyncio

from db.db_utils import indicator_db_utils


class IndicatorParam:
    """Параметры для расчёта показателя"""
    def __init__(self, user_id: int,
                 indicator_name: str | None = None,
                 project_name: str | None = None,
                 label_track_name: str = None,
                 label_calc_name: str = None,
                 track_by_name: bool = False,
                 track_by_project: bool = False,
                 calc_as_average: bool = False):
        self.indicator_name = indicator_name
        self.project_name = project_name
        self.label_track_name = label_track_name
        self.label_calc_name = label_calc_name
        self.track_by_name = track_by_name
        self.track_by_project = track_by_project
        self.calc_as_average = calc_as_average
        self.user_id = user_id

    async def add_params_json(self):
        """Добавление настроек через файл json"""
        return await indicator_db_utils.add_indicator_params_json(self.user_id)

    async def add_param(self):
        # TODO
        """Добавление параметра"""

    async def delete_param(self):
        # TODO
        """Удаление параметров"""

    async def update_param(self):
        # TODO
        """Обновление параметров"""


if __name__ == '__main__':
    pass

