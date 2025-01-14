import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from aiogram.enums.parse_mode import ParseMode

from config import settings
from logger_config import log

from handlers import router as main_router
from utils.scheduler_utils.setup_scheduler import setup_scheduler


# TODO
#  migrate from old version on the phone
#   добавить показатель cash (обновляться его через update аналогично kcals, steps)
#   обновление таблицы indicator_params с учётом cash indicator
#   заполнение данных из старой таблицы
#   создание requirements.txt
#   копирование на устройство установка окружения и зависимостей

# TODO V1.0:
#  tests, refactoring after
#  refactor with gpt (give him code and watch for result)
#  helps + docs + method description
#  docker, migrate from phone to server or cloud
#  new features with remaining file TODOS:
#  обработка метки @Achievement  report types, report settings interface, user settings interface,
#  scheduler settings interface etc

async def on_startup():  # функция выполняется при запуске бота
    log.info("Бот запушен.")


async def on_shutdown():
    log.info("Бот выключен.")


async def set_commands(bot: Bot):
    """Установка команд в меню клиента приложения телеграм"""
    commands = [BotCommand(command="/go", description="Выполнить расчёт, получить отчёт."),
                BotCommand(command="/tasksget", description="Получение списка всех запланированных задач.")
                ]
    await bot.set_my_commands(commands)


async def main():
    """Точка входа"""
    bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML)
              )
    dp = Dispatcher()
    dp.include_router(main_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(True)
    await set_commands(bot)  # установка команд
    await setup_scheduler(bot=bot)  # настройка расписания
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
