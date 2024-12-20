import asyncio
from typing import Dict
from indicator import Indicator
from report import Report
from todoist_task import TodoistTask
from schedule_task import ScheduleTask
from logger_config import log
from config import settings
from db.database import connection
from db.db_utils import user_db_utils, todoist_task_db_utils


class User:
    def __init__(self, telegram_id: int,
                 todoist_token: str | None = None,
                 user_id: int | None = None,
                 reports: tuple[Report | None] = None,
                 schedules: tuple[ScheduleTask | None] = None,
                 todoist_tasks: tuple[TodoistTask | None] = None,
                 indicators: tuple[Indicator | None] = None
                 ):
        self.telegram_id = telegram_id
        self.todoist_token = todoist_token
        self.user_id = user_id
        self.todoist_tasks = todoist_tasks
        self.reports = reports
        self.schedules = schedules
        self.indicators = indicators

    @classmethod
    async def register(cls, telegram_id: int) -> int | None:
        """Регистрация пользователя"""
        return await user_db_utils.create_user(telegram_id)

    async def add_todoist_token(self, todoist_token: str) -> bool:
        """Добавление токена todoist - включение функционал учёта todoist"""
        await todoist_task_db_utils.save_todoist_tasks(todoist_token=todoist_token, user_id=self.user_id)
        return await user_db_utils.add_user_todoist_token(todoist_token=todoist_token, user_id=self.user_id)

    async def save_todoist_data(self) -> bool:
        """Запуск выгрузки todois данных и загрузке в БД"""
        if not self.todoist_token:
            return False
        return await todoist_task_db_utils.save_todoist_tasks(todoist_token=self.todoist_token,
                                                              user_id=self.user_id)

    @classmethod
    async def auth(cls, telegram_id: int):  # реализация фабричного метода
        """Авторизация пользователя по telegram_id"""
        user_data = await user_db_utils.get_user_data_by_telegram_id(telegram_id=telegram_id)
        todoist_tasks = None
        reports = None
        schedules = None
        indicators = None
        if task_data := user_data[telegram_id].get('todoisttask'):
            todoist_tasks = tuple([TodoistTask(task=data['task'],
                                               project=data['project'],
                                               labels=data['labels'],
                                               description=data['description'],
                                               completed_at=data['completed_at'],
                                               priority=data['priority']
                                               ) for data in task_data])

        if task_data := user_data[telegram_id].get('report'):
            reports = tuple([Report
                             (name=data['name'],
                              report_type=data['report_type'],
                              start=data['start'],
                              end=data['end'],
                              ) for data in task_data])

        if schedules_data := user_data[telegram_id].get('scheduletask'):
            schedules = tuple([
                ScheduleTask(name=data['name'],
                             task_type=data['task_type'],
                             schedule=data['schedule'],
                             action=data['action'],
                             ) for data in schedules_data
            ])

        # TODO получить данные показателей
        #  инициализировать экземпляр Indicators
        #  отдать в класс USER

        indicators = None

        return User(
            telegram_id=user_data[telegram_id]['telegram_id'],
            user_id=user_data[telegram_id]['id'],
            todoist_token=user_data[telegram_id].get('todoist_token'),
            todoist_tasks=todoist_tasks,
            schedules=schedules,
            reports=reports,
            indicators=indicators
        )

    def get_user_data(self) -> Dict:
        """ Логика получения данных пользователя """

    def indicators_config(self):
        """Логика настройки индикаторов"""
        pass

    def reports_config(self):
        """Логика настройки отчетов"""

    def plan_tasks(self):
        """Логика планирования задач"""
        pass


if __name__ == '__main__':
    _user = asyncio.run(User.auth(settings.SUPER_USER_TG_ID))

    print(_user.indicators)
