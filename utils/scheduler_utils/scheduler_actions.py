from aiogram import Bot, types
from handlers.user_commands import handler_go
from logger_config import log
import aiosmtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from settings.mail_sender_config import mail_smpt_host, mail_smpt_port, mail_sender_address
from config import mail_server_token, today


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
        report_handler = handler_go

        await report_handler(message, schedule_bot=bot)
    except Exception as e:
        log.error("Ошибка в запуске handler_go.", exc_info=e)
        log.exception(e)


async def schedule_send_mail(files: tuple, receivers: tuple) -> bool:
    """Функция создания задачи по расписанию отправки письма получателями из receivers с файлами files"""
    for file in files:
        if not Path(file).exists():
            log.error("Файл {file} не найден.", file=file)
            raise FileNotFoundError

    from_address = mail_sender_address
    password = mail_server_token
    for receiver in receivers:
        try:
            mail_message = MIMEMultipart()
            mail_message['From'] = from_address
            mail_message['To'] = receiver
            mail_message['Subject'] = f'send files {Path(files[0]).name}-{today}'

            for file in files:
                if Path(file).is_file():
                    filename = Path(file).name
                    ctype = 'application/octet-stream'
                    maintype, subtype = ctype.split('/', 1)
                    with open(file, 'rb') as fp:
                        mime_file = MIMEBase(maintype, subtype)
                        mime_file.set_payload(fp.read())
                        encoders.encode_base64(mime_file)
                    mime_file.add_header('Content-Disposition', 'attachment', filename=filename)
                    mail_message.attach(mime_file)

            await aiosmtplib.send(
                mail_message,
                hostname=mail_smpt_host,
                port=mail_smpt_port,
                username=from_address,
                password=password,
                use_tls=True
            )
            log.info("Письмо отправлено: {receiver}.", receiver=receiver)

        except Exception as e:
            log.error("Ошибка при отправке {receiver}.", receiver=receiver, exc_info=e)
            log.exception(e)
            return False
    return True
