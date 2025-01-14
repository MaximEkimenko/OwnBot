from aiogram import Bot, types
from handlers.user_commands import handler_go
from logger_config import log


async def schedule_send_reminder(*, bot: Bot, telegram_id: int, reminder_text: str) -> None:
    """Функция создания напоминания по расписанию"""
    await bot.send_message(telegram_id, reminder_text)


async def schedule_go(bot: Bot, telegram_id: int, **kwargs) -> None:
    """Функция создания выгрузки с отчётом по расписанию"""
    user = types.User(id=telegram_id, first_name='username',
                      is_bot=False)
    chat = types.Chat(id=telegram_id, type='private')
    message = types.Message.model_construct(from_user=user,
                                            chat=chat,
                                            date=0,
                                            message_id=1,
                                            text='scheduled_go_handler',
                                            )
    try:
        await handler_go(message, schedule_bot=bot)
    except Exception as e:
        log.error("Ошибка в запуске handler_go.", exc_info=e)
