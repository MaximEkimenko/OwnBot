from aiogram import Bot, types
from handlers.user_commands import handler_go
from logger_config import log
from utils.handlers_utils import send_email


async def schedule_send_reminder(bot: Bot, telegram_id: int, task_text: str) -> None:
    """Функция создания напоминания по расписанию"""
    await bot.send_message(telegram_id, task_text)


async def schedule_every_day_report(bot: Bot, telegram_id: int) -> None:
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
        # TODO V1.0 выбирать handler отправки отчёта в зависимости от условия. Условие определяет пользователь.
        #  То есть подставляются разные обработчики отправки отчёта в зависимости от настроек пользователя.
        report_handler = handler_go

        await report_handler(message, schedule_bot=bot)
    except Exception as e:
        log.error("Ошибка в запуске handler_go.", exc_info=e)
        log.exception(e)


async def schedule_send_mail(files: tuple, receivers: tuple) -> bool:
    """Функция создания задачи по расписанию отправки письма получателями из receivers с файлами files"""
    return await send_email(files=files, receivers=receivers)
