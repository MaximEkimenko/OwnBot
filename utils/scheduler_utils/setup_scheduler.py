from collections.abc import Callable

from logger_config import log
from db.db_utils.scheduler_db_utils import get_all_users_scheduler_params
from utils.scheduler_utils.scheduler_actions import (
    schedule_send_mail,
    schedule_send_reminder,
    schedule_every_day_report,
)
from utils.scheduler_utils.scheduler_manager import scheduler


def set_job(action_func: Callable, settings: dict, job_kwargs: dict) -> None:
    """Добавление задачи в расписание"""
    scheduler.add_job(action_func,
                      replace_existing=True,
                      **settings,
                      misfire_grace_time=60 * 2,
                      kwargs=job_kwargs,
                      jobstore="default",
                      )


async def setup_scheduler(bot):
    """Настройщик расписания при запуске бота"""
    tasks = await get_all_users_scheduler_params()  # все задачи из БД
    reminder_settings = []
    report_settings = []
    email_settings = []

    for task in tasks:
        match task["task_type"].name:
            case "REMINDER":
                task_params = {
                    "trigger": "cron",
                    "day_of_week": task["schedule_params"]["day_of_week"],
                    "hour": task["schedule_params"]["hour"],
                    "minute": task["schedule_params"]["minute"],
                    "id": task["schedule_params"]["id"] + str(task["user_id"]),
                    "task_text": task["schedule_params"]["task_kwargs"]["task_text"],
                    "telegram_id": task["user_telegram_data"]["from_user"]["id"],
                }
                reminder_settings.append(task_params)
            case "REPORT":
                task_params = {
                    "trigger": "cron",
                    "day_of_week": task["schedule_params"]["day_of_week"],
                    "hour": task["schedule_params"]["hour"],
                    "minute": task["schedule_params"]["minute"],
                    "id": task["schedule_params"]["id"] + str(task["user_id"]),
                    "telegram_id": task["user_telegram_data"]["from_user"]["id"],
                }
                report_settings.append(task_params)
            case "EMAIL":
                task_params = {
                    "trigger": "cron",
                    "day_of_week": task["schedule_params"]["day_of_week"],
                    "hour": task["schedule_params"]["hour"],
                    "minute": task["schedule_params"]["minute"],
                    "id": task["schedule_params"]["id"] + str(task["user_id"]),
                    "receivers": task["schedule_params"]["task_kwargs"]["receivers"],
                    "files": task["schedule_params"]["task_kwargs"]["files"],
                }
                email_settings.append(task_params)

    # добавление задачи типа REMINDER
    for reminder_setting in reminder_settings:
        reminder_kwargs = {"bot": bot,
                           "telegram_id": reminder_setting.pop("telegram_id"),
                           "task_text": reminder_setting.pop("task_text")}
        set_job(action_func=schedule_send_reminder, settings=reminder_setting, job_kwargs=reminder_kwargs)
    # добавление задачи типа REPORT
    for report_setting in report_settings:
        report_kwargs = {"bot": bot,
                         "telegram_id": report_setting.pop("telegram_id")}
        set_job(action_func=schedule_every_day_report, settings=report_setting, job_kwargs=report_kwargs)
    # добавление задачи типа EMAIL
    for email_setting in email_settings:
        email_kwargs = {"receivers": email_setting.pop("receivers"),
                        "files": email_setting.pop("files")}
        set_job(action_func=schedule_send_mail, settings=email_setting, job_kwargs=email_kwargs)

    try:
        scheduler.start()
        log.debug("Планировщик успешно запущен.")
    except Exception as e:
        log.error("Ошибка при запуске планировщика.", exc_info=e)
        log.exception(e)
