from aiogram import Router, types
from aiogram.filters import Command
from utils.common_utils import (user_auth,
                                verify_string_as_filename,
                                verify_string_length,
                                list_of_tuples_to_str)
from logger_config import log
import enums
from own_bot_exceptions import StringInputError, StringLengthError
from utils.handlers_utils import verify_schedule_params, get_telegram_data_dict
from utils.scheduler_utils.scheduler_tasks_managment import add_or_update_scheduler_task, delete_scheduler_task


router = Router(name=__name__)

# TODO
#  Сейчас при выполнении команды /taskadd использованием напоминания создастся задача напоминание
#  TaskType.REMINDER, а без неё задача TaskType.TASK,  причём только на schedule_go, которая реализует
#  handler_go. То есть функция, которая реализует планируемую задачу зависит от типа задачи, который
#  зависит от наличия текста напоминания. Необходимо изменить эту логику и сделать зависимость выбора
#  функции которая реализует задачу по расписанию от параметра выдающегося пользователем
#  - Добавить хендлеров (ручных команд пользователя), которые обрабатывают другие задачи;
#  - Добавить в schedule_go список этих хендлеров;
#  - Дать пользователю параметр, который выбирает нужный хендлер для планирования в расписание из
#    schedule_go;
#  Допустимо оставить текущую логику по умолчанию (если пользователь не передал специальный параметр).


@router.message(Command('taskadd'))
async def handler_taskadd(message: types.Message):
    """Команда добавления задачи"""
    user = await user_auth(message)
    if user is False:
        return
    user_telegram_id = message.from_user.id
    reminder_elements = message.text.split(maxsplit=5)[1:]  # строка параметров cron
    # проверка имени задачи
    try:
        task_name = verify_string_as_filename(reminder_elements[0])
    except StringInputError as e:
        await message.answer(text=f"Неверно введено имя задачи. {e.args[0]}")
        log.warning("Ввод неверного имени задачи для показателя. {errors}", errors=e.args[0])
        return
    # проверка существующей задачи
    if await user.check_schedule_exists(task_name=task_name):
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
    # обновление типа на напоминание если есть текст задачи
    # TODO
    task_type = enums.TaskType.REMINDER if schedule_params["text"] else enums.TaskType.TASK
    reminder = await user.schedule_config(
        name=task_name,
        task_type=task_type,
        schedule_params=schedule_params,
        user_telegram_data=user_telegram_data
    )
    try:
        # добавление задачи в планировщик
        add_or_update_scheduler_task(schedule_params=schedule_params,
                                     user_id=user.user_id,
                                     telegram_id=message.from_user.id,
                                     bot=message.bot,
                                     task_type=task_type)
        # сохранение задачи в БД
        await reminder.create_reminder()
        await message.answer(text=f"Задача {task_name!r} успешно добавлена.")
        log.info("Задача {task} для пользователя {user} добавлена в БД успешно.",
                 task=task_name,
                 user=user_telegram_id)
    except Exception as e:
        await message.answer(text=f"Задача {task_name!r} не добавлена из-за ошибки. Попробуйте позже.")
        log.error("Ошибка добавления {task} для пользователя {user}.",
                  task=task_name,
                  user=user_telegram_id, exc_info=e)


@router.message(Command('taskupd'))
async def taskupd(message: types.Message):
    """Команда обновления задачи"""
    user = await user_auth(message)
    if user is False:
        return
    user_telegram_id = message.from_user.id
    reminder_elements = message.text.split(maxsplit=5)[1:]  # строка параметров cron
    # проверка имени задачи
    try:
        task_name = verify_string_as_filename(reminder_elements[0])
    except StringInputError as e:
        await message.answer(text=f"Неверно введено имя задачи. {e.args[0]}")
        log.warning("Ввод неверного имени задачи. {errors}", errors=e.args[0])
        return
    # проверка существующей задачи
    if not await user.check_schedule_exists(task_name=task_name):
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
    # обновление типа на напоминание если есть текст задачи
    task_type = enums.TaskType.REMINDER if schedule_params["text"] else enums.TaskType.TASK
    reminder = await user.schedule_config(
        name=task_name,
        task_type=enums.TaskType.REMINDER,
        schedule_params=schedule_params,
        user_telegram_data=user_telegram_data
    )
    try:
        # добавление задачи в планировщик
        add_or_update_scheduler_task(schedule_params=schedule_params,
                                     user_id=user.user_id,
                                     telegram_id=message.from_user.id,
                                     bot=message.bot,
                                     task_type=task_type)
        # сохранение в БД
        await reminder.update_reminder()
        await message.answer(text=f"Задача {task_name!r} успешно обновлена в БД.")
        log.info("Задача {task} для пользователя {user} обновлена успешно.",
                 task=task_name,
                 user=user_telegram_id)
    except Exception as e:
        await message.answer(text=f"Задача {task_name!r} не обновлена из-за ошибки. Попробуйте позже.")
        log.error("Ошибка обновления {task} для пользователя {user}.",
                  task=task_name,
                  user=user_telegram_id, exc_info=e)


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
    if not await user.check_schedule_exists(task_name=task_name):
        await message.answer(text=f"Удаление невозможно: задача {task_name!r} не существует. ")
        log.warning("Ввод не существующей задачи {task} для удаления пользователем {user}",
                    user=user_telegram_id,
                    task=task_name)
        return
    # удаление задачи
    reminder = await user.schedule_config(
        name=task_name
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


@router.message(Command('tasksget'))
async def tasksget(message: types.Message):
    """Получение всех задач пользователя"""
    user = await user_auth(message)
    if user is False:
        return
    tasks = await user.get_all_tasks()
    if not tasks:
        await message.answer(text="У вас нет запланированных задач.")
        return
    await message.answer(text="Перечень ваших запланированных задач:")
    await message.answer(text=list_of_tuples_to_str(tasks))
    log.debug("Запрос списка запланированных задач пользователем {user_id}.",
              user_id=message.from_user.id)
