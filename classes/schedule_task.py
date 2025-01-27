"""Задачи по расписанию."""
from enums import TaskType
from db.db_utils.scheduler_db_utils import save_reminder_data, delete_reminder_data, update_reminder_data


class ScheduleTask:
    """Задача по расписанию."""

    __slots__ = ("name", "schedule_params", "task_type", "user_id", "user_telegram_data")

    def __init__(self, name: str,
                 user_id: int,
                 task_type: TaskType,
                 schedule_params: dict,
                 user_telegram_data: dict) -> None:
        """Инициализация задачи по расписанию."""
        self.name = name
        self.user_id = user_id
        self.task_type = task_type
        self.schedule_params = schedule_params
        self.user_telegram_data = user_telegram_data

    async def create_reminder(self) -> None:
        """Добавление напоминания."""
        await save_reminder_data(user_id=self.user_id,
                                 task_type=self.task_type,
                                 schedule_params=self.schedule_params,
                                 user_telegram_data=self.user_telegram_data)

    async def update_reminder(self) -> None:
        """Обновление напоминания."""
        await update_reminder_data(user_id=self.user_id,
                                   task_type=self.task_type,
                                   schedule_params=self.schedule_params,
                                   user_telegram_data=self.user_telegram_data)

    async def delete_reminder(self) -> None:
        """Удаление напоминания."""
        await delete_reminder_data(user_id=self.user_id, task_name=self.name)
