from aiogram import Bot, types
from config import settings
from handlers.user_commands import handler_go
from logger_config import log


async def send_reminder(*, bot: Bot, telegram_id: int, reminder_text: str):
    """Команда напоминания по расписанию"""
    await bot.send_message(telegram_id, reminder_text)


async def schedule_go(bot):
    """Запуск выгрузки с отчётом по расписанию"""
    # TODO заполнить из БД по данным telegram пользователя
    user = types.User(id=settings.SUPER_USER_TG_ID, first_name='username',
                      is_bot=False)
    chat = types.Chat(id=settings.SUPER_USER_TG_ID, type='private')
    message = types.Message.model_construct(from_user=user,
                                            chat=chat,
                                            date=0,
                                            message_id=1,
                                            text='scheduled_go_handler',
                                            )
    try:
        await handler_go(message, schedule_bot=bot)
    except Exception as e:
        log.error("Ошибка в запуске handler_go.")
        log.exception(e)
