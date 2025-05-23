"""Валидация параметров задач по расписанию."""
from aiogram import types

import enums

from logger_config import log
from own_bot_exceptions import IntInputError, CronWeekDayInputError
from utils.common_utils import verify_integer, verify_cron_day_of_week


async def validate_task_type(message: types.Message, task_type_letter: str) -> enums.TaskType | None:
    """Валидация типа задачи."""
    # словарь перевода команды пользователя в TaskType
    task_type_translate_dict = enums.TaskType.get_task_type_translate_dict()

    if task_type_letter not in task_type_translate_dict:
        await message.answer(
            f"Тип задачи {task_type_letter!r} не существует. Воспользуйтесь командой /help для справки.",
        )
        log.warning(
            "Ввод несуществующего символа типа задачи {task_type_letter!r} пользователем {user!r}",
            task_type_letter=task_type_letter,
            user=message.from_user.id,
        )
        return None

    return task_type_translate_dict[task_type_letter]


async def validate_day_of_week(message: types.Message, day_input: str) -> str | None:
    """Валидация интервала дней недели в виде cron."""
    try:
        return verify_cron_day_of_week(day_input)
    except CronWeekDayInputError as e:
        await message.answer(e.args[0])
        log.warning("Введён неверный день недели {day_of_week!r}.", day_of_week=day_input)
        return None


async def validate_cron_hour_minute_integer(message: types.Message, value: str) -> int | None:
    """Валидация часов и минут cron."""
    try:
        return verify_integer(value)

    except IntInputError as e:
        await message.answer(e.args[0])
        log.warning("Введено неверное значение для. {error!r}", error=e.args[0])
        return None
