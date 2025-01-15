from aiogram import types
from classes.user import User
from logger_config import log
from own_bot_exceptions import UserDoesNotExistError


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
