"""Класс параметров показателя."""
# TODO ну жен этот класс?


class IndicatorParam:
    """Параметры для расчёта показателя."""

    __slots__ = (
        "calc_as_average",
        "indicator_name",
        "label_calc_name",
        "label_track_name",
        "project_name",
        "track_by_name",
        "track_by_project",
        "user_id",
    )

    def __init__(self, user_id: int,
                 indicator_name: str | None = None,
                 project_name: str | None = None,
                 label_track_name: str | None = None,
                 label_calc_name: str | None = None,
                 *,
                 track_by_name: bool = False,
                 track_by_project: bool = False,
                 calc_as_average: bool = False) -> None:
        """Инициализация параметров показателя."""
        self.indicator_name = indicator_name
        self.project_name = project_name
        self.label_track_name = label_track_name
        self.label_calc_name = label_calc_name
        self.track_by_name = track_by_name
        self.track_by_project = track_by_project
        self.calc_as_average = calc_as_average
        self.user_id = user_id

    # async def add_params_json(self) -> bool: # TODO перенесено в user
    #     """Добавление настроек через файл json."""
    #     return await indicator_db_utils.add_indicator_params_json(self.user_id)

    async def add_param(self) -> None:
        # TODO метод добавление параметра пользователем и вызовом через интерфейс через интерфейс
        """Добавление параметра."""

    async def update_param(self) -> None:
        # TODO
        """Обновление параметров."""

    async def delete_param(self) -> None:
        # TODO
        """Удаление параметров."""
