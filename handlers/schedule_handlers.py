"""Обработчики команд задач по расписанию."""
from aiogram import Router, types
from aiogram.filters import Command

from classes.user import User
from logger_config import log
from own_bot_exceptions import StringInputError, StringLengthError
from utils.common_utils import (
    verify_string_length,
    list_of_tuples_to_str,
    get_telegram_data_dict,
    verify_string_as_filename,
)
from utils.scheduler_utils.scheduler_params import validate_input_create_scheduler_params
from utils.scheduler_utils.scheduler_tasks_managment import (
    get_planned_jobs,
    delete_scheduler_task,
    add_or_update_scheduler_task,
)

router = Router(name=__name__)

# TODO
#  Добавить стратегии выбора видов ежедневного отчёта в verify_input_create_scheduler_params в зависимости
#  от task_param при task_type = REPORT
#  Допустимо оставить текущую логику по умолчанию (если пользователь не передал специальный параметр).


@router.message(Command("taskadd"))
async def handler_taskadd(message: types.Message, user: User) -> None:
    """Команда добавления / обновления задачи."""
    is_update = False
    user_telegram_id = message.from_user.id
    task_elements = message.text.split(maxsplit=6)[1:]  # строка параметров пользователя
    command_length = 6
    if len(task_elements) != command_length:
        await message.answer(text="Неверно введена команда /taskadd. Смотри /help.")
        log.warning("Несоответствие параметрам при команде /taskadd {text} "
                    "пользователем id={user}. Длина команды {command_length} элементов",
                    text=message.text, user=user.user_id, command_length=command_length,
                    )
        return

    # проверка имени задачи
    try:
        task_name = verify_string_as_filename(task_elements[0])
    except StringInputError as e:
        await message.answer(text=f"Неверно введено имя задачи. {e.args[0]}")
        log.warning("Ввод неверного имени задачи для показателя. {errors}", errors=e.args[0])
        return

    # получение и проверка данных задач
    schedule_params = await validate_input_create_scheduler_params(message, task_elements)
    if schedule_params is None:
        return

    # проверка существующей задачи оповещение об обновлении
    if await user.check_schedule_exists(task_name=task_name):
        is_update = True
        await message.answer(text=f"Задача {task_name!r} уже существует.\nЗадача будет обновлена.")
        log.info("Обновление существующей задачи {task} пользователем {user}",
                 user=user_telegram_id,
                 task=task_name)

    schedule_params.update({"id": task_name})
    # получение данных telegram
    user_telegram_data = get_telegram_data_dict(message)

    reminder = await user.schedule_config(
        name=task_name,
        task_type=schedule_params["task_type"],
        schedule_params=schedule_params,
        user_telegram_data=user_telegram_data,
    )
    try:
        # добавление задачи в планировщик
        add_or_update_scheduler_task(schedule_params=schedule_params,
                                     user_id=user.user_id,
                                     )
        # сохранение задачи в БД
        if schedule_params["task_kwargs"].get("bot"):
            schedule_params["task_kwargs"].pop("bot")  # удаление экземпляра бота перед записью в БД
        if is_update:
            await reminder.update_reminder()
        else:
            await reminder.create_reminder()
        task_type = schedule_params["task_type"].value
        await message.answer(text=f"Задача {task_name!r} с типом {task_type!r} успешно добавлена.")
        log.info("Задача {task} для пользователя {user} добавлена в БД успешно.",
                 task=task_name,
                 user=user_telegram_id)
    except Exception as e:
        await message.answer(text=f"Задача {task_name!r} не добавлена из-за ошибки. Попробуйте позже.")
        log.error("Ошибка добавления {task} для пользователя {user}.",
                  task=task_name,
                  user=user_telegram_id, exc_info=e)
        log.exception(e)


@router.message(Command("taskdel"))
async def taskdel(message: types.Message, user: User) -> None:
    """Команда удаления задачи."""
    user_telegram_id = message.from_user.id
    reminder_elements = message.text.split(maxsplit=2)[1:]  # строка команды с именем задачи
    # проверка имени задачи
    try:
        task_name = verify_string_length(reminder_elements[0], 255)
    except StringLengthError as e:
        await message.answer(text=e.args[0])
        log.warning("Ввод слишком длинного текста. {errors}", errors=e.args[0])
        return
    # проверка существования задачи
    if not await user.check_schedule_exists(task_name=task_name):
        await message.answer(text=f"Удаление невозможно: задача {task_name!r} не существует. ")
        log.warning("Ввод не существующей задачи {task} для удаления пользователем {user}",
                    user=user_telegram_id,
                    task=task_name)
        return
    # удаление задачи
    reminder = await user.schedule_config(
        name=task_name,
    )
    try:
        delete_scheduler_task(task_name=task_name, user_id=user.user_id)
        await reminder.delete_reminder()
        await message.answer(text=f"Задача {task_name!r} успешна удалено.")
        log.info("Задача {task} для пользователя {user} удалена успешно.",
                 task=task_name,
                 user=user_telegram_id)
    except Exception as e:
        await message.answer(text=f"Задача {task_name!r} не удалена из-за ошибки. Попробуйте позже.")
        log.error("Ошибка удаления задачи {task} для пользователя {user}.",
                  task=task_name,
                  user=user_telegram_id, exc_info=e)
        log.exception(e)


@router.message(Command("tasksget"))
async def tasksget(message: types.Message, user: User) -> None:
    """Получение всех задач пользователя."""
    db_tasks = await user.get_all_tasks()

    tasks = get_planned_jobs(db_tasks)
    if not tasks:
        await message.answer(text="У вас нет запланированных задач.")
        return
    await message.answer(text="Перечень ваших запланированных задач:")
    await message.answer(text=list_of_tuples_to_str(tasks))
    log.debug("Запрос списка запланированных задач пользователем {user_id}.",
              user_id=message.from_user.id)
