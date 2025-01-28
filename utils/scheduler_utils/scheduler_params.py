"""Параметры задач по расписанию."""
import json

from pathlib import Path

from aiogram import types

import enums

from config import BaseDIR
from logger_config import log
from own_bot_exceptions import StringLengthError
from utils.common_utils import verify_string_length, should_be_never_called
from settings.mail_sender_config import files, receivers
from utils.scheduler_utils.params_validation import (
    validate_task_type,
    validate_day_of_week,
    validate_cron_hour_minute_integer,
)

# TODO V1.0
#  добавить отчёты по имени показателя в расписание при выборе task_param при task_type = REPORT


async def validate_input_create_scheduler_params(message: types.Message, task_elements: list) -> dict | None:
    """Проверка ввода данных планирования задачи создание параметров."""
    task_type = await validate_task_type(message, task_elements[1])
    if task_type is None:
        return None

    day_of_week = await validate_day_of_week(message, task_elements[2])
    if day_of_week is None:
        return None

    hour = await validate_cron_hour_minute_integer(message, task_elements[3])
    if hour is None:
        return None

    minute = await validate_cron_hour_minute_integer(message, task_elements[4])
    if minute is None:
        return None

    task_kwargs = await create_task_kwargs(message, task_type, task_elements[5])
    if task_kwargs is None:
        should_be_never_called()  # TODO есть сценарий когда она вызывается при ошибке - найти и обработать.

    return {
        "day_of_week": day_of_week,
        "hour": hour,
        "minute": minute,
        "task_type": task_type,
        "task_kwargs": task_kwargs,
    }


async def create_task_kwargs(message: types.Message,
                             task_type: enums.TaskType,
                             task_param: str) -> dict | None:
    """Создание task_kwargs по task_param."""
    telegram_id = message.from_user.id
    bot = message.bot
    match task_type:
        case enums.TaskType.REMINDER:
            try:
                task_text = verify_string_length(task_param, 1000)
            except StringLengthError as e:
                await message.answer(e.args[0])
                log.warning("Ввод слишком длинного текста. {errors!r}", errors=e.args[0])
                return None
            else:
                return {"telegram_id": telegram_id, "task_text": task_text, "bot": bot}

        case enums.TaskType.REPORT:
            if task_param == "full":
                return {"telegram_id": telegram_id, "bot": bot}
            # TODO
            #  elif task_param = имя_показателя:
            #  вызывается функция_которая_сравнивает_task_param_и_все_показатели_возвращая_bool:
            #  в kwargs передаётся имя показателя для выбора хендлера телеграм отправки отчёта
            await message.answer(f"Неверно введён параметр вида отчёта {task_param!r}.")
            log.warning("Неверно введён параметр для получения отчёта {task_param!r}.", task_param=task_param)
            return None

        case enums.TaskType.EMAIL:
            return await create_email_task_kwargs(message, task_param)

        case _:
            log.warning("Тип отчёта {task_type!r} не учтён в match case.", task_type=task_type)
            should_be_never_called()


async def create_email_task_kwargs(message: types.Message, task_param: str) -> dict | None:
    """Получение параметров отправки почты в зависимости от task_param."""
    if task_param == "conf":
        return {"files": files, "receivers": receivers}

    if task_param == "json":
        try:
            json_path = BaseDIR / Path("sender.json")
            json_content = json.loads(json_path.read_text(encoding="utf-8"))
            return {"files": json_content["files"], "receivers": json_content["receivers"]}
        except Exception as e:
            await message.answer(f"Ошибка заполнения файла {BaseDIR / Path('sender.json')!r}.")
            log.error("Ошибка заполнения файла sender.json пользователем {user!r}.",
                      user=message.from_user.id,
                      exc_info=e)
            return None

    await message.answer(f"Неверно введён параметр отправки письма {task_param!r}.")
    log.warning("Неверно введён параметр для получения отчёта {task_param!r}.", task_param=task_param)
    return None
