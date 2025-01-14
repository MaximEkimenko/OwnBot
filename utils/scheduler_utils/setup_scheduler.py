from logger_config import log
from utils.scheduler_utils.scheduler_actions import schedule_send_reminder, schedule_go
from db.db_utils.scheduler_db_utils import get_all_users_scheduler_params
from utils.scheduler_utils.scheduler_manager import scheduler


async def setup_scheduler(bot):
    """Настройщик расписания при запуске бота"""
    tasks = await get_all_users_scheduler_params()
    reminder_settings = []
    action_settings = []
    for task in tasks:
        if task["task_type"].name == "REMINDER":
            task_params = {
                "trigger": "cron",
                "day_of_week": task["schedule_params"]["day_of_week"],
                "hour": task["schedule_params"]["hour"],
                "minute": task["schedule_params"]["minute"],
                "id": task["schedule_params"]["id"] + str(task["user_id"]),
                "reminder_text": task["schedule_params"]["text"],
                "telegram_id": task["user_telegram_data"]["from_user"]["id"],
            }
            reminder_settings.append(task_params)
        if task["task_type"].name == "TASK":
            task_params = {
                "trigger": "cron",
                "day_of_week": task["schedule_params"]["day_of_week"],
                "hour": task["schedule_params"]["hour"],
                "minute": task["schedule_params"]["minute"],
                "id": task["schedule_params"]["id"] + str(task["user_id"]),
                "telegram_id": task["user_telegram_data"]["from_user"]["id"],
            }
            action_settings.append(task_params)

    common_kwargs = {'bot': bot}
    reminder_kwargs = dict()
    action_kwargs = dict()
    # добавление задачи типа reminder
    for reminder_setting in reminder_settings:
        reminder_kwargs.update(common_kwargs |
                               {"telegram_id": reminder_setting.pop("telegram_id"),
                                "reminder_text": reminder_setting.pop("reminder_text")}
                               )
        scheduler.add_job(schedule_send_reminder, replace_existing=True,
                          **reminder_setting,
                          misfire_grace_time=60,
                          kwargs=reminder_kwargs)
    # установка задачи типа task
    for action_setting in action_settings:
        action_kwargs.update(common_kwargs | {"telegram_id": action_setting.pop("telegram_id")})
        scheduler.add_job(schedule_go, replace_existing=True,
                          **action_setting,
                          misfire_grace_time=60,
                          kwargs=action_kwargs)
    # запуск планировщика
    try:
        scheduler.start()
        log.debug("Планировщик успешно запущен.")
    except Exception as e:
        log.error("Ошибка при запуске планировщика.", exc_info=e)
