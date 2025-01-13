from aiogram import Router

from handlers.base_commands import router as base_commands_router
from handlers.user_commands import router as user_commands_router
from handlers.file_handlers import router as file_handlers_router
from handlers.schedule_handlers import router as schedule_handlers_router

router = Router(name=__name__)

router.include_routers(base_commands_router,
                       user_commands_router,
                       file_handlers_router,
                       schedule_handlers_router,
                       )
