import json
from pathlib import Path

import enums
from aiogram import types
from config import BaseDIR
from logger_config import log
from own_bot_exceptions import CronWeekDayInputError, IntInputError, StringLengthError
from settings.mail_sender_config import files, receivers
from utils.common_utils import verify_cron_day_of_week, verify_integer, verify_string_length


# TODO V1.0
#  добавить отчёты по имени показателя в расписание при выборе task_param при task_type = REPORT


async def verify_input_create_scheduler_params(message: types.Message, task_elements: list) -> dict | None:
    """"Проверка ввода данных планирования задачи"""
    # TODO отрефачить всю функцию
    # тип задачи
    task_type_letter = task_elements[1]
    # словарь перевода пользовательских параметров в тип задачи
    task_type_translate_dict = enums.TaskType.get_task_type_translate_dict()
    # TODO переделать на проверку своего exception и ответом e.args[0] как остальные случаи?
    if task_type_letter not in task_type_translate_dict.keys():
        await message.answer(text=f"Тип задачи {task_type_letter!r} не существует. "
                                  f"Воспользуйтесь командой /help для справки.")
        log.warning("Ввод несуществующего символа типа задачи {task_type_letter!r} пользователем {user!r}",
                    task_type_letter=task_type_letter, user=message.from_user.id)
        return

    task_type = task_type_translate_dict[task_type_letter]

    # дни недели
    try:
        day_of_week = verify_cron_day_of_week(task_elements[2])
    except CronWeekDayInputError as e:
        await message.answer(text=e.args[0])
        log.warning("Введен неверный день недели. {day_of_week!r}",
                    day_of_week=task_elements[1],
                    errors=e.args[0])
        return

    # проверка значений часа и минут
    try:
        hour = verify_integer(task_elements[3])
    except IntInputError as e:
        await message.answer(text=e.args[0])
        log.warning("Ввод неверного числа. {errors!r}", errors=e.args[0])
        return
    try:
        minute = verify_integer(task_elements[4])
    except IntInputError as e:
        await message.answer(text=e.args[0])
        log.warning("Ввод неверного числа. {errors!r}", errors=e.args[0])
        return

    # проверка значения task_param и формирование параметров стратегии
    try:
        task_param = task_elements[5]
        telegram_id = message.from_user.id
        bot = message.bot

        match task_type:
            case task_type.REMINDER:  # напоминание:
                try:
                    task_text = verify_string_length(task_param, 1000)
                    task_kwargs = {"telegram_id": telegram_id, "task_text": task_text, "bot": bot}
                except StringLengthError as e:
                    await message.answer(text=e.args[0])
                    log.warning("Ввод слишком длинного текста. {errors!r}", errors=e.args[0])
                    return
            case task_type.REPORT:  # ежедневная отправка отчёта
                if task_param == "full":
                    task_kwargs = {"telegram_id": telegram_id, "bot": bot}
                # TODO
                #  elif функция_которая_сравнивает_task_param_и_все_показатели_возвращая_bool:
                #  в kwargs передаётся имя показателя дял выбора хендлера отчёта
                else:
                    await message.answer(text=f"Неверно введён параметр вида отчёта {task_param!r}.")
                    log.warning("Неверно введён параметр для получения отчёта {task_param!r}.", task_param=task_param)
                    return
            case task_type.EMAIL:  # отправка email
                if task_param == "conf":
                    task_kwargs = {"files": files, "receivers": receivers}

                elif task_param == "json":
                    try:
                        json_path = BaseDIR / Path("sender.json")
                        json_content = json.loads(json_path.read_text(encoding="utf-8"))
                        task_kwargs = {"files": json_content["files"], "receivers": json_content["receivers"]}
                    except Exception as e:
                        await message.answer(text=f"Ошибка заполнения файла {BaseDIR / Path('sender.json')!r}.")
                        log.error("Ошибка заполнения файла sender.json пользователем {user!r}.",
                                  user=telegram_id, exc_info=e)
                        return

                else:
                    await message.answer(text=f"Неверно введён параметр отправки письма {task_param!r}.")
                    log.warning("Неверно введён параметр для получения отчёта {task_param!r}.", task_param=task_param)
                    return
            case _:
                await message.answer(text=f"Неверный тип отчёта {task_type!r}.")
                log.warning("Неверный тип отчёта {task_type!r}.", task_type=task_type)
                return

    except IndexError:
        await message.answer("Введены не все параметры для настройки задачи.")
        log.warning("Введены не все параметры для настройки задачи пользователем: {user!r}.", user=message.from_user.id)
        return
    schedule_params = {
        "day_of_week": day_of_week,
        "hour": hour,
        "minute": minute,
        "task_type": task_type,
        "task_kwargs": task_kwargs
    }
    return schedule_params
