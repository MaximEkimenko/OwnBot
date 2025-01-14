from aiogram import types

from own_bot_exceptions import CronWeekDayInputError, IntInputError, StringLengthError
from utils.common_utils import verify_integer, verify_string_length, verify_cron_day_of_week, get_min_telegram_data, \
    get_flat_dict
from logger_config import log


async def verify_schedule_params(message: types.Message, reminder_elements: list) -> dict | None:
    """"Проверка ввода данных планирования задачи"""
    # проверка дней недели
    try:
        day_of_week = verify_cron_day_of_week(reminder_elements[1])
    except CronWeekDayInputError as e:
        await message.answer(text=e.args[0])
        log.warning("Введен неверный день недели. {day_of_week}",
                    day_of_week=reminder_elements[1],
                    errors=e.args[0])
        return
    # проверка значений часа и минуты
    try:
        hour = verify_integer(reminder_elements[2])
    except IntInputError as e:
        await message.answer(text=e.args[0])
        log.warning("Ввод неверного числа. {errors}", errors=e.args[0])
        return
    try:
        minute = verify_integer(reminder_elements[3])
    except IntInputError as e:
        await message.answer(text=e.args[0])
        log.warning("Ввод неверного числа. {errors}", errors=e.args[0])
        return
    # проверка строки напоминания
    try:
        text = verify_string_length(reminder_elements[4], 1000)
    except StringLengthError as e:
        await message.answer(text=e.args[0])
        log.warning("Ввод слишком длинного текста. {errors}", errors=e.args[0])
        return
    # заполнение параметров НЕ напоминания (задачи без текста)
    except IndexError:
        text = None
    schedule_params = {
        "day_of_week": day_of_week,
        "hour": hour,
        "minute": minute,
        "text": text,
    }
    return schedule_params


def get_telegram_data_dict(message: types.Message) -> dict:
    """ Получение данных telegram """
    try:
        user_telegram_data = get_flat_dict(message)
        log.debug("Данные telegram для пользователя {user} успешно получены.", user=message.from_user.id)
    except Exception as e:
        user_telegram_data = get_min_telegram_data(message, user_id=message.from_user.id)
        log.error("Ошибка получения данных telegram для пользователя {user} сохранён упрощённый словарь.",
                  user=message.from_user.id, exc_info=e)

    return user_telegram_data
