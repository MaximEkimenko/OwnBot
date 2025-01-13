import asyncio

from db.db_utils.scheduler_db_utils import (save_reminder_data, is_schedule_exists,
                                            update_reminder_data, delete_reminder_data, get_scheduler_params)
from enums import TaskType

# TODO переименовать везде reminder в task


class ScheduleTask:
    def __init__(self, name: str,
                 user_id: int,
                 task_type: TaskType,
                 schedule_params: dict,
                 user_telegram_data: dict):
        self.name = name
        self.user_id = user_id
        self.task_type = task_type
        self.schedule_params = schedule_params
        self.user_telegram_data = user_telegram_data

    @classmethod
    async def check_schedule_exists(cls, task_name, user_id):
        """Проверка существования задачи"""
        return await is_schedule_exists(task_name, user_id=user_id)

    async def create_reminder(self):
        """Добавление напоминания"""
        await save_reminder_data(user_id=self.user_id,
                                 task_type=self.task_type,
                                 schedule_params=self.schedule_params,
                                 user_telegram_data=self.user_telegram_data)

    async def update_reminder(self):
        """Обновление напоминания"""
        await update_reminder_data(user_id=self.user_id,
                                   schedule_params=self.schedule_params,
                                   user_telegram_data=self.user_telegram_data)

    async def delete_reminder(self):
        """Удаление напоминания"""
        await delete_reminder_data(user_id=self.user_id, task_name=self.name)


    async def get_all_tasks(self):
        """Получение всех задач"""
        tasks = await get_scheduler_params(user_id=self.user_id)
        # TODO !!!!!
        return [(line["name"],
                 line["task_type"],
                 line["schedule_params"]["days_of_week"],
                 line["schedule_params"]["hour"],
                 line["schedule_params"]["minute"],
                 line["schedule_params"]["text"],
                 )

                for line in tasks]


if __name__ == '__main__':
    _schedule_params = {}
    _user_telegram_data = {}
    sch = ScheduleTask(name='tst_name',
                       user_id=1,  # replace with actual user id
                       task_type=TaskType.REMINDER,
                       schedule_params=_schedule_params,
                       user_telegram_data=_user_telegram_data)
    asyncio.run(sch.create_reminder())
