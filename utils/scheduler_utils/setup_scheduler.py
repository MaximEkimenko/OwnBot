from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import settings
from utils.scheduler_utils.schedule_actions import schedule_send_reminder, schedule_go


def setup_scheduler(bot):
    """Настройщик расписания"""

    scheduler = AsyncIOScheduler()
    # добавление задачи типа reminder
    # TODO получение настроек задач типа reminder из БД
    reminder_settings = [
        {
            "trigger": 'cron', "day_of_week": "mon-sun", "hour": 12, "minute": 2,
            "id": "send_private",
            "reminder_text": "text_first_reminder"
        },
        {
            "trigger": 'cron', "day_of_week": "mon-sun", "hour": 12, "minute": 1,
            "id": "send_private_2",
            "reminder_text": "text_second_reminder which is very long!"
        }
    ]
    common_kwargs = {'bot': bot}
    reminder_kwargs = dict()
    # установка задачи типа reminder
    for reminder_setting in reminder_settings:
        reminder_kwargs.update(common_kwargs |
                               {"telegram_id": settings.SUPER_USER_TG_ID,
                                "reminder_text": reminder_setting.pop("reminder_text")}
                               )
        scheduler.add_job(schedule_send_reminder, replace_existing=True,
                          **reminder_setting,
                          misfire_grace_time=60,
                          kwargs=reminder_kwargs)
    # добавление задачи типа action
    # TODO получение настроек задач типа action из БД
    action_settings = {"trigger": 'cron', "day_of_week": "mon-sun", "hour": 15, "minute": 48,
                       "id": 'action_1'
                       }

    # установка задачи типа task
    scheduler.add_job(schedule_go, replace_existing=True,
                      **action_settings,
                      misfire_grace_time=60,
                      kwargs=common_kwargs)

    # запуск планировщика
    scheduler.start()
