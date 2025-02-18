"""Основной конфиг приложения."""
import datetime

from pathlib import Path
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.types import BotCommand
from pydantic_settings import BaseSettings, SettingsConfigDict

from settings import timezones


class Settings(BaseSettings):
    """Настройки приложения."""

    BASE_DIR: Path = Path(__file__).parent
    DB_NAME: str
    BOT_TOKEN: str
    SUPER_USER_TG_ID: int
    MAIL_SERVER_TOKEN: str

    @property
    def db_url(self) -> str:
        """Url доступа к БД."""
        return rf"sqlite+aiosqlite:///{self.BASE_DIR}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", case_sensitive=False)


settings = Settings()
BaseDIR = settings.BASE_DIR
mail_server_token = settings.MAIL_SERVER_TOKEN
TIMEZONE = timezones.ASIA_OMSK
local_timezone = ZoneInfo(TIMEZONE)


first_day_to_report = datetime.date(year=2024, month=1, day=1)


def init_today() -> datetime:
    """Получение сегодня."""
    current_date = datetime.datetime.now(tz=local_timezone).date()
    return current_date - datetime.timedelta(days=0)


def init_timezone_offset() -> int:
    """Получение timezone смещения от UTC в часах."""
    now = datetime.datetime.now(tz=local_timezone)
    return int(now.utcoffset().seconds / (60 * 60))


async def set_bot_commands(bot: Bot) -> None:
    """Установка команд в меню клиента приложения телеграм."""
    commands = [BotCommand(command="/go", description="Выполнить расчёт, получить отчёт."),
                BotCommand(command="/tasksget", description="Получение списка всех запланированных задач."),
                BotCommand(command="/db", description="Отправка копии БД на электронную почту"),
                BotCommand(command="/help", description="Инструкция по использованию приложения."),
                ]
    await bot.set_my_commands(commands)
