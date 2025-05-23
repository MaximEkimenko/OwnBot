"""Общие функции."""
import re
import datetime

from typing import Any, Never

from aiogram import Bot, types

from logger_config import log
from own_bot_exceptions import (
    IntInputError,
    StringInputError,
    StringLengthError,
    EmptyValueInputError,
    CronWeekDayInputError,
)


def verify_string_as_filename(input_string: str) -> str:
    """Асинхронно проверяет строку на возможность использования её в качестве имени файла.

    Вызывает исключение ValueError, если строка содержит недопустимые символы
    или не соответствует правилам именования файлов.
    """
    if not input_string:
        raise EmptyValueInputError

    # Список недопустимых символов для имен файлов в разных ОС
    invalid_chars = r'[\\\\/:*?"<>|]'  # Windows запрещенные символы

    # Максимальная длина имени файла
    max_length = 255

    # Проверка недопустимых символов
    if re.search(invalid_chars, input_string):
        raise StringInputError(invalid_chars=invalid_chars)

    # Проверка длины файла
    if len(input_string) > max_length:
        raise StringInputError(max_length=max_length)

    # Проверка зарезервированных имен в Windows
    reserved_names = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    base_name = input_string.split(".")[0].upper()  # Учитываем только базовое имя (до расширения)
    if base_name in reserved_names:
        raise StringInputError(base_name=base_name)

    # Проверка на пробелы или точки в начале и конце имени файла
    if input_string.strip() != input_string or input_string.endswith("."):
        raise StringInputError
    return input_string


def get_bot_for_schedule(message: types.Message, schedule_bot: Bot) -> Bot:
    """Проверка задачи по расписанию."""
    if schedule_bot:
        return schedule_bot
    return message.bot


def verify_integer(number: str | int | float) -> int:
    """Проверка входящего значения на тип integer."""
    try:
        return int(number)
    except ValueError as e:
        raise IntInputError(number) from e


def verify_string_length(input_string: str | None, str_length: int) -> str | None:
    """Вызывает исключение если строка превышает длину в str_length символов."""
    if not input_string:
        return None
    # Проверка длины
    if len(input_string) > str_length:
        raise StringLengthError(str_length)

    return input_string


def verify_cron_day_of_week(day_of_week: str) -> str:
    """Вызывает исключение если входящая строка не соответствует числовому значению cron day_od_week."""
    pattern = "^[0-6](-[0-6])?$"
    if not re.match(pattern, day_of_week):
        raise CronWeekDayInputError
    return day_of_week


def list_of_tuples_to_str(list_of_tuples: list[Any]) -> str:
    """Приведение списка кортежей к строке."""
    return "\n\n".join(" | ".join(map(str, row)) for row in list_of_tuples)


def get_telegram_data_dict(message: types.Message) -> dict:
    """Получение данных telegram."""
    try:
        user_telegram_data = get_flat_dict(message)
        log.debug("Данные telegram для пользователя {user} успешно получены.", user=message.from_user.id)
    except Exception as e:
        user_telegram_data = get_min_telegram_data(message, user_id=message.from_user.id)
        log.error("Ошибка получения данных telegram для пользователя {user} сохранён упрощённый словарь.",
                  user=message.from_user.id, exc_info=e)

    return user_telegram_data


def get_flat_dict(data_object: object) -> dict:
    """Получение плоского словаря атрибутов объекта."""
    raw_data = {}

    for key, val in data_object.__dict__.items():
        if hasattr(val, "__dict__"):  # атрибут объект
            raw_data[key] = val.__dict__

        elif isinstance(val, list):  # список
            for index, item in enumerate(val, start=1):
                if hasattr(item, "__dict__"):  # внутри списка объект
                    raw_data[f"{key}_{index}"] = item.__dict__
                elif isinstance(item, dict):  # внутри списка словарь
                    raw_data[f"{key}_{index}"] = item
                else:
                    raw_data[f"{key}_{index}"] = item

        elif isinstance(val, datetime.datetime):  # если атрибут дата
            raw_data[key] = val.timestamp()

        else:
            raw_data[key] = val
    return raw_data


def get_min_telegram_data(message: types.Message, user_id: int) -> dict:
    """Получение минимального набора данных telegram."""
    return {"from_user": {"id": message.from_user.id,
                          "first_name": message.from_user.first_name,
                          "last_name": message.from_user.last_name,
                          "username": message.from_user.username,
                          },
            "date": message.date.timestamp(),
            "text": message.text,
            "user_id": user_id,
            }


def should_be_never_called() -> Never:
    """Функция не должна вызываться."""
    msg = "Вызвана функция should_be_never_called."
    raise AssertionError(msg)
