from utils.scheduler_utils.scheduler_manager import scheduler
from utils.scheduler_utils.scheduler_actions import schedule_send_reminder, schedule_go
from aiogram import Bot
import enums
from logger_config import log


def add_or_update_scheduler_task(schedule_params: dict, user_id: int, telegram_id: int, task_type: enums.TaskType, bot: Bot):
    """Добавление / обновление задачи по расписанию при изменении, добавлении данных задачи пользователем"""
    task_id = schedule_params["id"] + str(user_id)
    # удаление существующей задачи
    job = scheduler.get_job(task_id)
    if job:
        scheduler.remove_job(task_id)

    # словарь функций выполняющих задачи
    actions = {task_type.TASK: schedule_go,
               task_type.REMINDER: schedule_send_reminder}

    kwargs = {"telegram_id": telegram_id,
              "reminder_text": schedule_params.get("text"),
              "bot": bot}

    scheduler.add_job(
        actions[task_type],
        trigger="cron",
        day_of_week=schedule_params["day_of_week"],
        hour=schedule_params["hour"],
        minute=schedule_params["minute"],
        id=task_id,
        misfire_grace_time=60,
        kwargs=kwargs
    )
    log.info("Задача:{task_id} запланирована успешно для пользователя:{user}, "
             "тип:{task_type}.",
             task_type=task_type.name, user=user_id, task_id=task_id)


def delete_scheduler_task(task_name: str, user_id: int) -> None:
    """Удаление задачи по расписанию"""
    task_id = task_name + str(user_id)
    job = scheduler.get_job(task_id)
    if job:
        scheduler.remove_job(task_id)
    log.info("Задача:{task_id} удалена успешно для пользователя:{user}.",
             user=user_id, task_id=task_id)
