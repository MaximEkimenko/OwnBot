"""Базовые команды telegram."""
from aiogram import Router, types
from aiogram.filters import Command, CommandStart

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: types.Message) -> None:
    """Команда старт."""
    start_text = """\nВас приветствует бот для учёта показателей эффективности.\n
Введите /help для получения инструкции по использованию.\n
                  """
    await message.answer(text=start_text)


@router.message(Command("help"))
async def handle_help(message: types.Message) -> None:
    """Инструкция приложения."""
    help_text = """\nДля регистрации воспользуйтесь командой /register.\n
Команда для ручного обновления показателей:
`/update показатель1 значение1 показатель2 значение2`\n
Полную инструкцию можно найти на: https://github.com/MaximEkimenko/OwnBot.\n
    """

    await message.answer(text=help_text)

