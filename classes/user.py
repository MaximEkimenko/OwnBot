"""Класс пользователя."""
from typing import Self

import enums

from db.db_utils import user_db_utils, todoist_task_db_utils
from classes.report import Report
from classes.indicator import Indicator
from own_bot_exceptions import UserDoesNotExistError
from classes.todoist_task import TodoistTask
from classes.schedule_task import ScheduleTask
from classes.indicator_param import IndicatorParam
from db.db_utils.scheduler_db_utils import is_schedule_exists, get_scheduler_params


class User:
    """Пользователь."""

    __slots__ = (
        "indicator_params",
        "indicators",
        "schedules",
        "telegram_id",
        "todoist_tasks",
        "todoist_token",
        "user_id",
    )

    def __init__(self, telegram_id: int,
                 todoist_token: str | None = None,
                 user_id: int | None = None,
                 schedules: tuple[ScheduleTask | None] | None = None,
                 todoist_tasks: tuple[TodoistTask | None] | None = None,
                 ) -> None:
        """Инициализация пользователя."""
        self.telegram_id = telegram_id
        self.todoist_token = todoist_token
        self.user_id = user_id
        self.todoist_tasks = todoist_tasks
        self.schedules = schedules
        self.indicators = Indicator(user_id=self.user_id)
        self.indicator_params = IndicatorParam(user_id=self.user_id)

    @classmethod
    async def register(cls, telegram_id: int) -> int | None:
        """Регистрация пользователя."""
        return await user_db_utils.create_user(telegram_id=telegram_id)

    async def add_todoist_token(self, todoist_token: str) -> bool:
        """Добавление токена todoist - включение функционал учёта todoist."""
        # TODO добавить команду в интерфейсе
        await todoist_task_db_utils.save_todoist_tasks(todoist_token=todoist_token, user_id=self.user_id)
        return await user_db_utils.add_user_todoist_token(todoist_token=todoist_token, user_id=self.user_id)

    async def save_todoist_data(self) -> str:
        """Запуск выгрузки todois данных и загрузке в БД."""
        if not self.todoist_token:
            return "Чтобы начать пользоваться этим функционалом должен быть введён корректный todoist token."
        return await todoist_task_db_utils.save_todoist_tasks(todoist_token=self.todoist_token,
                                                              user_id=self.user_id)

    @classmethod
    async def auth(cls, telegram_id: int) -> Self:  # реализация фабричного метода
        """Авторизация пользователя по telegram_id."""
        user_data = await user_db_utils.get_user_data_by_telegram_id(telegram_id=telegram_id)
        if not user_data:
            raise UserDoesNotExistError(telegram_id=telegram_id)

        todoist_tasks = None
        schedules = None

        return User(
            telegram_id=user_data[telegram_id]["telegram_id"],
            user_id=user_data[telegram_id]["id"],
            todoist_token=user_data[telegram_id].get("todoist_token"),
            todoist_tasks=todoist_tasks,
            schedules=schedules,
        )

    async def report_config(self,
                            report_name: str | None = None,
                            report_type: enums.ReportType | None = None,
                            content: str | None = None) -> Report:
        """Инициализация отчёта."""
        return Report(
            user_id=self.user_id,
            name=report_name,
            report_type=report_type,
            content=content,
        )

    async def schedule_config(self,
                              name: str,
                              task_type: enums.TaskType | None = None,
                              schedule_params: dict | None = None,
                              user_telegram_data: dict | None = None) -> ScheduleTask:
        """Инициализация задачи по расписанию."""
        return ScheduleTask(
            user_id=self.user_id,
            name=name,
            task_type=task_type,
            schedule_params=schedule_params,
            user_telegram_data=user_telegram_data,
        )

    async def check_schedule_exists(self, task_name: str) -> bool:
        """Проверка существования задачи по расписанию."""
        return await is_schedule_exists(task_name, user_id=self.user_id)

    async def get_all_tasks(self) -> list:
        """Получение списка всех задач."""
        tasks = await get_scheduler_params(user_id=self.user_id)
        return [(line["name"],
                 line["user_id"],
                 line["task_type"],
                 line["schedule_params"]["day_of_week"],
                 line["schedule_params"]["hour"],
                 line["schedule_params"]["minute"],
                 line["schedule_params"]["task_kwargs"],
                 )
                for line in tasks]
