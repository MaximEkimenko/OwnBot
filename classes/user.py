from typing import Dict
from indicator import Indicator
from report import Report
from logger_config import log


class User:
    def __init__(self, telegram_id: int, telegram_token: str, todoist_token: str):
        self.telegram_id = telegram_id
        self.telegram_token = telegram_token
        self.todoist_token = todoist_token

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



    def get_user_data(self) -> Dict:
        # Логика получения данных пользователя
        return {
            "telegram_id": self.telegram_id,
            "telegram_token": self.telegram_token,
            "todoist_token": self.todoist_token
        }

    def get_indicator(self, name: str) -> Indicator:
        # Логика получения индикатора по имени
        pass

    def get_report(self, name: str) -> Report:
        # Логика получения отчета по имени
        pass

    def indicators_config(self):
        # Логика настройки индикаторов
        pass

    def reports_config(self):
        # Логика настройки отчетов
        pass

    def plan_tasks(self):
        # Логика планирования задач
        pass


if __name__ == '__main__':
    log.debug('Starting')
