import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from aiogram.enums.parse_mode import ParseMode
from aiogram import types
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import settings

from logger_config import log

from handlers import router as main_router


# TODO
#  scheduler
#  migrate from old version on the phone
#  small todos in files + refactor + exceptions
#  refactor with gpt (give him code and watch fo result)
#  tests
#  helps + docs + method description
#  docker, migrate from phone to server or cloud
#  new features: report types, user settings interface


async def on_startup():  # функция выполняется при запуске бота
    log.info(f"bot online {datetime.now()}")


async def on_shutdown():
    log.info(f"bot offline {datetime.now()}")


# TODO scheduler перенести куда надо
async def set_commands(bot: Bot):
    """Установка команд в меню"""
    commands = [BotCommand(command="/go", description="Выполнить расчёт, получить отчёт.")]
    await bot.set_my_commands(commands)


async def scheduled_go(bot: Bot):
    """Команда /go по расписанию"""
    await bot.send_message(chat_id=settings.SUPER_USER_TG_ID, text='WORKED!')


def setup_scheduler():
    """Настройщик расписания"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_go, "cron", hour=14, minute=40)
    scheduler.start()


async def main():
    """Точка входа"""
    bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML)
              )
    dp = Dispatcher()
    dp.include_router(main_router)
    dp.startup.register(on_startup)

    setup_scheduler()  # Настройка расписания
    await bot.delete_webhook(True)
    await set_commands(bot)

    await dp.start_polling(bot)

    dp.startup.register(on_shutdown)


if __name__ == '__main__':
    asyncio.run(main())
