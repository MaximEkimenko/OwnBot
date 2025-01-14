from aiogram import Router, types
from aiogram.filters import CommandStart, Command

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: types.Message):
    """Команда старт"""


@router.message(Command("help"))
async def handle_help(message: types.Message):
    """Инструкция пользователя"""
