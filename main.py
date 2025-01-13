import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from aiogram.enums.parse_mode import ParseMode
from datetime import datetime


from config import settings

from logger_config import log

from handlers import router as main_router
from utils.scheduler_utils.setup_scheduler import setup_scheduler


# TODO
#  scheduler:
#  чтение данных scheduler для запуска расписания
#  делать перезапуск расписания по команде пользователя
#  добавить показатель cash заполнять его update, построить на него график перезаполнить показатели
#  переписать логи на %s строки при logging и {} строки при loguru
#  переписать все свои raise на собственные exceptions (начать с валидатров)
#  удалить log.exception(e), добавить log(text, exc_info=e)
#  добавить команду вывода списка всех своих напоминаний
#  migrate from old version on the phone
#  small todos in files + refactor + exceptions
#  refactor with gpt (give him code and watch for result)
#  tests
#  helps + docs + method description
#  docker, migrate from phone to server or cloud
#  new features: report types, report settings interface, user settings interface, scheduler settings interface

async def on_startup():  # функция выполняется при запуске бота
    log.info(f"bot online {datetime.now()}")


async def on_shutdown():
    log.info(f"bot offline {datetime.now()}")


async def set_commands(bot: Bot):
    """Установка команд в меню"""
    commands = [BotCommand(command="/go", description="Выполнить расчёт, получить отчёт.")]
    await bot.set_my_commands(commands)


async def main():
    """Точка входа"""
    bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML)
              )
    dp = Dispatcher()
    dp.include_router(main_router)
    dp.startup.register(on_startup)

    await bot.delete_webhook(True)
    await set_commands(bot)
    setup_scheduler(bot=bot)  # Настройка расписания
    await dp.start_polling(bot)


    dp.startup.register(on_shutdown)


if __name__ == '__main__':
    asyncio.run(main())
