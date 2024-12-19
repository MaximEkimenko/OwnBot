import asyncio
from typing import Dict
from indicator import Indicator
from report import Report
from logger_config import log
from config import settings
from db.database import connection
from db.db_utils import user_db_utils






class User:
    def __init__(self, telegram_id: int,
                 todoist_token: str | None = None,
                 user_id: int | None = None):
        self.telegram_id = telegram_id
        self.todoist_token = todoist_token
        self.user_id = user_id


    @classmethod
    async def register(cls, telegram_id: int) -> int | None:
        """Регистрация пользователя"""
        return await user_db_utils.create_user(telegram_id)

    async def add_todoist_token(self):
        """Добавление токена todoist - включение функционал учёта todoist"""
        return await user_db_utils.add_user_todoist_token(user_id=self.user_id, todoist_token=self.todoist_token)

    @classmethod
    async def auth(cls, telegram_id: int):  # реализация фабричного метода
        """Авторизация пользователя по telegram_id"""
        # user_data = await user_crud_utils.get_user_data_by_telegram_id(telegram_id=telegram_id)
        # # аутентификация
        # if not user_data:
        #     raise ValueError('Такого пользователя не существует.')
        # # авторизация
        # return cls(user_fio=user_data['user_fio'],
        #                      telegram_id=telegram_id,
        #                      telegram_data=user_data['telegram_data'],
        #                      user_role=enums.UserRole.ADMIN,
        #                      user_description=user_data['user_description'],
        #                      id=user_data['id'])




    async def save_todoist_data(self):
        """Сохранение todoist данных по API todoist"""



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
    asyncio.run()

