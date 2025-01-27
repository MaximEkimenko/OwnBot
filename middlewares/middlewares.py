from typing import Any
from collections.abc import Callable, Awaitable

from aiogram import BaseMiddleware, types
from aiogram.types import TelegramObject

from logger_config import log
from utils.handlers_utils import user_auth


class AuthMiddleware(BaseMiddleware):
    """Аутентификация пользователя"""

    async def __call__(self,
                       handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
                       event: types.Message,
                       data: dict[str, Any]) -> Any:
        if event.message:
            message: types.Message = event.message
            user = await user_auth(message)
            if user is False:
                return None
            data["user"] = user
            data["bot"] = event.bot
            log.debug("Сообщение зарегистрированного пользователя {user_id}.",
                      user_id=user.telegram_id)

            return await handler(event, data)
