"""Точка вхожа в приложение."""
import asyncio
import threading

from asyncio.exceptions import CancelledError

from aiogram import Bot, Dispatcher
from aiogram.utils.backoff import BackoffConfig
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from config import settings, set_bot_commands
from handlers import router as main_router
from logger_config import log
from middlewares.middlewares import AuthMiddleware
from utils.scheduler_utils.setup_scheduler import setup_scheduler

# TODO V1.0:
# TODO найти лучшее решение передачи даты начала отчёта по умолчанию в файле config.py first_day_to_report
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


def start_scheduler_in_thread(bot: Bot, loop: asyncio.AbstractEventLoop) -> None:
    """Запуск планировщика в отдельном потоке."""

    def run_scheduler() -> None:
        asyncio.run_coroutine_threadsafe(setup_scheduler(bot), loop)

    thread = threading.Thread(target=run_scheduler, daemon=False)
    thread.start()


async def on_startup(bot: Bot) -> None:  # функция выполняется при запуске бота
    """Функция на выполнение при запуске бота."""
    await bot.send_message(chat_id=settings.SUPER_USER_TG_ID, text="Бот вышел online.")
    log.info("Бот запушен.")
    # запуск планировщика
    # await setup_scheduler(bot=bot)
    # Запуск планировщика в отдельном потоке
    start_scheduler_in_thread(bot=bot, loop=asyncio.get_event_loop())


async def on_shutdown(bot: Bot) -> None:
    """Функция на выполнение при отключении бота."""
    await bot.send_message(chat_id=settings.SUPER_USER_TG_ID, text="Бот offline.")
    log.info("Бот выключен.")


async def main() -> None:
    """Точка входа."""
    bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML),
              )
    try:
        dp = Dispatcher()
        dp.include_router(main_router)
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        await bot.delete_webhook(drop_pending_updates=True)
        await set_bot_commands(bot)  # установка команд
        dp.update.middleware(AuthMiddleware())  # добавление middleware

        backoff_config = BackoffConfig(
            max_delay=30,
            min_delay=2,
            factor=2,
            jitter=0.5,
        )
        await dp.start_polling(bot, polling_timeout=30, backoff_config=backoff_config)
    except (KeyboardInterrupt, CancelledError):
        log.debug("Бот остановлен принудительной командой.")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
