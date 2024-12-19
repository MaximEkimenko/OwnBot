from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent
    DB_NAME: str
    BOT_TOKEN: str
    TODOIST_TOKEN: str
    SUPER_USER_TG_ID: int

    @property
    def db_url(self):
        return rf'sqlite+aiosqlite:///{self.BASE_DIR}/{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", case_sensitive=False)


settings = Settings()
BaseDIR = settings.BASE_DIR
TIME_ZONE = 6

if __name__ == "__main__":
    print(settings.BASE_DIR)

