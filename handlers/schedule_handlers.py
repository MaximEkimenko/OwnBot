from aiogram import Router, types
from aiogram.filters import Command
from utils.common_utils import user_auth, verify_string_as_filename, verify_string_length
from logger_config import log
import enums
from classes.schedule_task import ScheduleTask
from own_bot_exceptions import StringInputError, StringLengthError
from handlers.handler_utils import verify_schedule_params, get_telegram_data_dict

router = Router(name=__name__)


@router.message(Command('taskadd'))
async def handler_taskadd(message: types.Message):
    """Команда добавления задачи"""
    user = await user_auth(message)
    if user is False:
        return
    user_telegram_id = message.from_user.id
    # TODO расширить функционал добавления параметров cron
    reminder_elements = message.text.split(maxsplit=5)[1:]  # строка параметров cron
    # проверка имени задачи
    try:
        task_name = verify_string_as_filename(reminder_elements[0])
    except StringInputError as e:
        await message.answer(text=f"Неверно введено имя задачи. {e.args[0]}")
        log.warning("Ввод неверного имени задачи для показателя. {errors}", errors=e.args[0])
        return
    # проверка существующей задачи
    if await ScheduleTask.check_schedule_exists(task_name=task_name, user_id=user.user_id):
        await message.answer(text=f"Задача {task_name!r} уже существует. "
                                  f"Воспользуйтесь командой /remuapd.")
        log.warning("Ввод существующей задачи {task} для добавления пользователем {user}",
                    user=user_telegram_id,
                    task=task_name)
        return
    # получение и проверка данных графика задач
    schedule_params = await verify_schedule_params(message, reminder_elements)
    if not schedule_params:
        return
    schedule_params.update({"id": task_name})
    # получение данных telegram
    user_telegram_data = get_telegram_data_dict(message)
    # сохранение данных
    if schedule_params["text"]:  # обновление типа на напоминание если есть текст задачи
        task_type = enums.TaskType.REMINDER
    else:
        task_type = enums.TaskType.TASK
    reminder = await user.schedule_config(
        name=task_name,
        task_type=task_type,
        schedule_params=schedule_params,
        user_telegram_data=user_telegram_data
    )
    try:
        await reminder.create_reminder()
        await message.answer(text=f"Задача {task_name!r} успешно добавлена.")
        log.info("Задача {task} для пользователя {user} добавлена успешно.",
                 task=task_name,
                 user=user_telegram_id)
    except Exception as e:
        await message.answer(text=f"Задача {task_name!r} не добавлена из-за ошибки. Попробуйте позже.")
        log.error("Ошибка добавления {task} для пользователя {user}.",
                  task=task_name,
                  user=user_telegram_id, exc_info=e)
    # TODO
    # перезапуск setup_scheduler при изменении / добавлении настроек пользователем


@router.message(Command('taskupd'))
async def taskupd(message: types.Message):
    """Команда обновления задачи"""
    user = await user_auth(message)
    if user is False:
        return
    user_telegram_id = message.from_user.id
    # TODO расширить функционал добавления параметров cron
    reminder_elements = message.text.split(maxsplit=5)[1:]  # строка параметров cron
    # проверка имени задачи
    try:
        task_name = verify_string_as_filename(reminder_elements[0])
    except StringInputError as e:
        await message.answer(text=f"Неверно введено имя задачи. {e.args[0]}")
        log.warning("Ввод неверного имени задачи. {errors}", errors=e.args[0])
        return
    # проверка существующей задачи
    if not await ScheduleTask.check_schedule_exists(task_name=task_name, user_id=user.user_id):
        await message.answer(text=f"Задача {task_name!r} не существует. "
                                  f"Воспользуйтесь командой /remadd.")
        log.warning("Ввод не существующей задачи {task} для обновления пользователем {user}",
                    user=user_telegram_id,
                    task=task_name)
        return
    # получение и проверка данных графика задач
    schedule_params = await verify_schedule_params(message, reminder_elements)
    if not schedule_params:
        return
    schedule_params.update({"id": task_name})
    # получение данных telegram
    user_telegram_data = get_telegram_data_dict(message)
    # обновление данных
    reminder = await user.schedule_config(
        name=task_name,
        task_type=enums.TaskType.REMINDER,
        schedule_params=schedule_params,
        user_telegram_data=user_telegram_data
    )
    try:
        await reminder.update_reminder()
        await message.answer(text=f"Задача {task_name!r} успешно обновлена.")
        log.info("Задача {task} для пользователя {user} обновлена успешно.",
                 task=task_name,
                 user=user_telegram_id)
    except Exception as e:
        await message.answer(text=f"Задача {task_name!r} не обновлена из-за ошибки. Попробуйте позже.")
        log.error("Ошибка обновления {task} для пользователя {user}.",
                  task=task_name,
                  user=user_telegram_id, exc_info=e)
    # TODO
    # перезапуск setup_scheduler при изменении / добавлении настроек пользователем


@router.message(Command('taskdel'))
async def taskdel(message: types.Message):
    """Команда удаления задачи"""
    user = await user_auth(message)
    if user is False:
        return
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
    if not await ScheduleTask.check_schedule_exists(task_name=task_name, user_id=user.user_id):
        await message.answer(text=f"Удаление невозможно задача {task_name!r} не существует. ")
        log.warning("Ввод не существующей задачи {task} для удаления пользователем {user}",
                    user=user_telegram_id,
                    task=task_name)
        return
    # удаление задачи
    reminder = await user.schedule_config(
        name=task_name
      )
    try:
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

    # TODO
    # перезапуск setup_scheduler при изменении / добавлении настроек пользователем


@router.message(Command('showtasks'))
async def showtasks(message: types.Message):
    """"""



