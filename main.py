import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from aiogram.enums.parse_mode import ParseMode

from datetime import datetime
from config import settings

from logger_config import log

from handlers import router as main_router


async def on_startup():  # функция выполняется при запуске бота
    log.info(f"bot online {datetime.now()}")


async def on_shutdown():
    log.info(f"bot offline {datetime.now()}")


async def main():

    bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML)
              )
    dp = Dispatcher()
    dp.include_router(main_router)
    dp.startup.register(on_startup)

    await bot.delete_webhook(True)
    await dp.start_polling(bot)

    dp.startup.register(on_shutdown)


if __name__ == '__main__':
    asyncio.run(main())
