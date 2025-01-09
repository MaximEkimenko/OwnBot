
from enums import TaskType



class ScheduleTask:
    def __init__(self, name: str, task_type: TaskType, schedule_params: dict,
                 telegram_user_data: dict):
        self.name = name
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

    # TODO
    async def create_reminder(self):
        """Добавление напоминания"""

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


