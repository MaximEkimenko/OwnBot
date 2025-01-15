from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import datetime


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent
    DB_NAME: str
    BOT_TOKEN: str
    TODOIST_TOKEN: str
    SUPER_USER_TG_ID: int
    MAIL_SERVER_TOKEN: str

    @property
    def db_url(self):
        return rf'sqlite+aiosqlite:///{self.BASE_DIR}/{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", case_sensitive=False)


settings = Settings()
BaseDIR = settings.BASE_DIR
mail_server_token = settings.MAIL_SERVER_TOKEN
TIME_ZONE = 6
today = datetime.date.today() - datetime.timedelta(days=0)
# TODO найти лучшее решение передачи даты начала отчёта по умолчанию
first_day_to_report = datetime.date(year=2024, month=1, day=1)

if __name__ == "__main__":
    print(settings)

