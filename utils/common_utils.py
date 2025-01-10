from classes.user import User
from aiogram import types
from logger_config import log
import re
import datetime


async def user_auth(message: types.Message):
    """Аутентификация пользователя"""
    command_name = message.text.split()[0]
    try:
        user = await User.auth(message.from_user.id)
    # TODO
    except ValueError:
        log.warning('Попытка доступа к команде '
                    '{command_name} пользователем: '
                    '{full_name}, '
                    'telegram_id={id}.',
                    command_name=command_name,
                    full_name=message.from_user.full_name,
                    id=message.from_user.id)
        return False
    return user


async def verify_string_as_filename(input_string: str) -> str:
    """
    Асинхронно проверяет строку на возможность использования её в качестве имени файла.
    Вызывает исключение ValueError, если строка содержит недопустимые символы
    или не соответствует правилам именования файлов.
    """
    if not input_string:
        # TODO
        raise ValueError("Имя пользователя не может быть пустым.")

    # Список недопустимых символов для имен файлов в разных ОС
    invalid_chars = r'[\\\\/:*?"<>|]'  # Windows запрещенные символы

    # Максимальная длина имени файла в большинстве ОС
    max_length = 255

    # Проверка недопустимых символов
    if re.search(invalid_chars, input_string):
        # TODO
        raise ValueError(f"Строка содержит недопустимые символы: {invalid_chars}")

    # Проверка длины файла
    if len(input_string) > max_length:
        # TODO
        raise ValueError(f"Строка слишком длинная. Максимальная длина: {max_length} символов.")

    # Проверка зарезервированных имен в Windows
    reserved_names = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    base_name = input_string.split('.')[0].upper()  # Учитываем только базовое имя (до расширения)
    if base_name in reserved_names:
        # TODO
        raise ValueError(f"Строка зарезервирована в Windows: {base_name}")

    # Проверка на пробелы или точки в начале и конце имени файла
    if input_string.strip() != input_string or input_string.endswith('.'):
        # TODO
        raise ValueError("Строка не должна начинаться или заканчиваться пробелами или точками.")
    return input_string


def get_bot_for_schedule(message: types.Message, schedule_bot):
    """Проверка задачи по расписанию"""
    if schedule_bot:
        return schedule_bot
    return message.bot


def get_flat_dict(data_object: object) -> dict:
    """"Получение плоского словаря атрибутов объекта"""
    raw_telegram_data = {}

    for key, val in data_object.__dict__.items():
        if hasattr(val, "__dict__"):  # атрибут объект
            raw_telegram_data[key] = val.__dict__

        elif isinstance(val, list):  # список
            for index, item in enumerate(val, start=1):
                if hasattr(item, "__dict__"):  # внутри списка объект
                    raw_telegram_data[f"{key}_{index}"] = item.__dict__
                elif isinstance(item, dict):  # внутри списка словарь
                    raw_telegram_data[f"{key}_{index}"] = item
                else:
                    raw_telegram_data[f"{key}_{index}"] = item

        elif isinstance(val, datetime.datetime):  # если атрибут дата
            raw_telegram_data[key] = val.timestamp()

        else:
            raw_telegram_data[key] = val
    return raw_telegram_data


def get_min_telegram_data(message: types.Message) -> dict:
    """Получение минимального набора данных telegram"""
    return {'from_user': {'id': message.from_user.id,
                          'first_name': message.from_user.first_name,
                          'last_name': message.from_user.last_name,
                          'username': message.from_user.username,
                          },
            'date': message.date.timestamp(),
            'text': message.text,
            }
