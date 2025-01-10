import asyncio

from db.db_utils.scheduler_db_utils import save_reminder_data
from enums import TaskType


class ScheduleTask:
    def __init__(self, name: str,
                 user_id: int,
                 task_type: TaskType,
                 schedule_params: dict,
                 telegram_user_data: dict):
        self.name = name
        self.user_id = user_id
        self.task_type = task_type
        self.schedule_params = schedule_params
        self.telegram_user_data = telegram_user_data

    # {
    #     "trigger": 'cron', "day_of_week": "mon-sun", "hour": 12, "minute": 2,
    #     "id": "send_private",
    #     "reminder_text": "text_first_reminder"
    # },
    # {
    #     "trigger": 'cron', "day_of_week": "mon-sun", "hour": 12, "minute": 1,
    #     "id": "send_private_2",
    #     "reminder_text": "text_second_reminder which is very long!"
    # }

    async def create_reminder(self):
        """Добавление напоминания"""
        await save_reminder_data(user_id=self.user_id,
                                 schedule_params=self.schedule_params,
                                 telegram_user_data=self.telegram_user_data)

    async def update_reminder(self):
        """Обновление напоминания"""

    async def delete_reminder(self):
        """Удаление напоминания"""

    async def create_task(self):
        """Добавление задачи"""

    async def update_task(self):
        """Обновление задачи"""

    async def delete_task(self):
        """Удаление задачи"""


if __name__ == '__main__':
    _schedule_params = {}
    _telegram_user_data = {}
    sch = ScheduleTask(name='tst_name',
                       user_id=1,  # replace with actual user id
                       task_type=TaskType.REMINDER,
                       schedule_params=_schedule_params,
                       telegram_user_data=_telegram_user_data)
    asyncio.run(sch.create_reminder())
