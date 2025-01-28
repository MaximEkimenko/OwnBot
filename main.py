"""Точка вхожа в приложение."""
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from config import settings, set_bot_commands
from handlers import router as main_router
from logger_config import log
from middlewares.middlewares import AuthMiddleware
from utils.scheduler_utils.setup_scheduler import setup_scheduler

# TODO V1.0:
#  tests, refactoring after
#  refactor with gpt (give him code and watch for result)
#  helps + docs + method description
#  docker, migrate from phone to server or cloud
#  new features with remaining file TODOS:
#  обработка метки @Achievement  report types, report settings interface, user settings interface,
#  scheduler settings interface etc
#  обработка ошибки отсутствия первоначального заполнения IndicatorParams, подробная инструкция настройки,
#  в том числе настройки стилей отчётов
#  попробовать запустить самому по инструкции на другом устройстве с другими показателями


bot = Bot(token=settings.BOT_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML),
          )


async def on_startup() -> None:  # функция выполняется при запуске бота
    """Функция на выполнение при запуске бота."""
    await bot.send_message(chat_id=settings.SUPER_USER_TG_ID, text="Бот вышел online.")
    log.info("Бот запушен.")
    # запуск планировщика
    await setup_scheduler(bot=bot)


async def on_shutdown() -> None:
    """Функция на выполнение при отключении бота."""
    await bot.send_message(chat_id=settings.SUPER_USER_TG_ID, text="Бот offline.")
    log.info("Бот выключен.")


async def main() -> None:
    """Точка входа."""
    dp = Dispatcher()
    dp.include_router(main_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(bot)  # установка команд
    dp.update.middleware(AuthMiddleware())  # добавление middleware
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
