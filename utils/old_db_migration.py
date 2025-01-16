"""Скрипт для переноса данных со старой версии БД на новую"""
import asyncio
import sqlite3
from config import BaseDIR
from pathlib import Path
import datetime
from db.models import Indicator
from db.database import connection
from sqlalchemy.ext.asyncio import AsyncSession


from db.db_utils.indicator_db_utils import get_indicator_params_id_dict

DB_PATH = BaseDIR / Path('progress_tracker.db')


class Database:
    """Взаимодействие с старой версией БД progress_tracker"""
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        """Подключение к базе данных и создание курсора."""
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def execute_query(self, query: str, params=()) -> None:
        """Выполнение запроса с поддержкой параметров."""
        self.cursor.execute(query, params)
        self.connection.commit()

    def fetch_all(self, query: str, params=()) -> list:
        """Получение всех данных из запроса."""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query: str, params=()) -> list:
        """Получение одной записи из запроса."""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self) -> None:
        """Закрытие соединения с базой данных."""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


async def get_old_data():
    """Получение и подготовка старых данных показателей для копирования в новую БД """
    query = """
    SELECT date, 'book' AS indicator_name, book AS indicator_value FROM indicators
    UNION ALL
    SELECT date, 'audiobook', audiobook FROM indicators
    UNION ALL
    SELECT date, 'video', video FROM indicators
    UNION ALL
    SELECT date, 'steps', steps FROM indicators
    UNION ALL
    SELECT date, 'kcals', kcals FROM indicators
    UNION ALL
    SELECT date, 'cndx', cndx FROM indicators
    UNION ALL
    SELECT date, 'add_income', add_income FROM indicators
    UNION ALL
    SELECT date, 'study_done', study_done FROM indicators
    UNION ALL
    SELECT date, 'health_done', health_done FROM indicators
    UNION ALL
    SELECT date, 'wealth_done', money_done FROM indicators
    UNION ALL
    SELECT date, 'social_done', social_done FROM indicators
    UNION ALL
    SELECT date, 'studio_done', studio_done FROM indicators
    UNION ALL
    SELECT date, 'poms', poms FROM indicators;
    """
    indicator_params = await get_indicator_params_id_dict(user_id=1)
    with Database(db_name=DB_PATH) as db:
        rows = db.fetch_all(query)
        result = [
            {"date": datetime.datetime.strptime(row[0], '%d.%m.%Y').date(),
             "indicator_name": row[1],
             "indicator_value": row[2],
             "user_id": 1,
             "indicator_params_id": indicator_params[row[1]]
             }
            for row in rows
        ]

    return result


@connection
async def migrate_old_data(indicators_data: dict, session: AsyncSession) -> bool:
    """Копирование старых данных в новую ДБ"""
    try:
        indicators = [Indicator(**indicator) for indicator in indicators_data]
        session.add_all(indicators)
        await session.commit()
        return True
    except Exception as e:
        await session.rollback()
        print(e)
        return False


if __name__ == '__main__':
    data = asyncio.run(get_old_data())
    print(asyncio.run(get_old_data()))
    print(asyncio.run(migrate_old_data(data)))
    pass
