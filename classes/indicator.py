"""Основной класс показателя."""
from io import BytesIO

from classes.indicator_param import IndicatorParam
from calculate_methods.pdf_based import pdf_indicator_to_db
from db.db_utils.indicator_db_utils import (
    create_indicator_params,
    create_or_update_indicators,
    get_indicator_params_id_dict,
)
from calculate_methods.quantity_based import get_quantity_todoist_dict
from calculate_methods.description_based import get_description_todoist_dict
from calculate_methods.default_values_based import get_default_values_dict

# TODO источник предыдущей версии расчёта проект owneed_bot -
#  - файл progress_tracker_db_write.py
#  - функция indicators_write

# TODO V1.0:
#      - Показатель количества выполненных задач по метке начать с @Achievement.
#        (или обойтись только формированием отчёта из таблицы БД? То есть вместо
#        ежедневного показателя формируем только отчёт (раз в месяц по расписанию?))
#      - Операции со значениями из ячеек файлов excel
#      - Операции со значениями из ключей файлов json файлов
#      - Метод Indicator.add_json - который добавляет параметры показателя из json файла,
#        который загружает пользователь
#      - Метод Indicator.add_params- который добавляет параметры показателя и получает данные
#        из интерфейса (FSM?)


class Indicator:
    """Показатель."""

    __slots__ = ("name", "params", "user_id")

    def __init__(self,
                 user_id: int,
                 name: str | None = None,
                 params: IndicatorParam | None = None) -> None:
        """Инициализация показателя."""
        self.name = name
        self.params = params  # TODO нужно ли?
        self.user_id = user_id

    async def calculate_save_indicators(self) -> tuple:
        """Выполнение расчётов показателей для записи в БД."""
        # метод основанный на описании
        description_based_result = await get_description_todoist_dict(self.user_id)
        # количественней метод
        quantity_result = await get_quantity_todoist_dict(self.user_id)
        # значения по умолчанию
        default_values = await get_default_values_dict(self.user_id)

        return description_based_result, quantity_result, default_values

    async def verificate_indicators(self, indicators_to_update: dict) -> dict:
        """Валидация показателей."""
        exist_indicators = await get_indicator_params_id_dict(user_id=self.user_id)

        valid_indicators = {}
        for indicator_to_update, indicator_value in indicators_to_update.items():
            if indicator_to_update not in exist_indicators:
                return {"*failed": indicator_to_update}
            # если все показатели верные
            valid_indicators[indicator_to_update] = {"value": indicator_value,
                                                     "params_id": exist_indicators[indicator_to_update]}
        return valid_indicators

    async def pdf_save_indicators(self, file_data: BytesIO) -> str:
        """Выполнение расчёта показателей из pdf и запись в БД."""
        return await pdf_indicator_to_db(self.user_id, file_data)

    async def manual_update_save_indicators(self, indicator_data: dict) -> str:
        """Сохранение данных из команды update."""
        return await create_or_update_indicators(self.user_id, data=indicator_data)


    async def add_indicator_params(self, params: dict) -> None:
        """Добавление параметра показателя."""
        return await create_indicator_params(user_id=self.user_id, data=params)

