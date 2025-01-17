from aiogram import types
from classes.user import User
from logger_config import log
from own_bot_exceptions import UserDoesNotExistError
import aiosmtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from settings.mail_sender_config import mail_smpt_host, mail_smpt_port, mail_sender_address
from config import mail_server_token, init_today




async def user_auth(message: types.Message) -> User | bool:
    """Аутентификация пользователя"""
    command_name = message.text.split()[0]
    try:
        user = await User.auth(message.from_user.id)
    except UserDoesNotExistError:
        log.warning('Попытка доступа к команде '
                    '{command_name} пользователем: '
                    '{full_name}, '
                    'telegram_id={id}.',
                    command_name=command_name,
                    full_name=message.from_user.full_name,
                    id=message.from_user.id)
        return False
    return user


async def send_email(receivers: tuple, files: tuple) -> bool:
    """Функция отправки письма получателями из receivers с файлами files"""
    today = init_today()
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
