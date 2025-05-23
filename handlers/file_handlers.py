"""Обработчики получения файлов."""
from typing import TYPE_CHECKING

from aiogram import F, Router, types
from openpyxl import load_workbook

from logger_config import log

if TYPE_CHECKING:
    from classes.user import User

router = Router(name=__name__)


@router.message(F.document.mime_type == "application/pdf")
async def handle_get_pdf(message: types.Message, user: "User") -> None:
    """Сохранение данных из загруженного файла PDF."""
    # проверка расширения
    file_name = message.document.file_name
    if not file_name.endswith(".pdf"):
        await message.reply(f"Файл: {file_name} должен быть .pdf")
    # чтение файла
    try:
        file_id = message.document.file_id
        bot = message.bot
        file = await bot.get_file(file_id)
        file_data = await bot.download_file(file.file_path)
    except Exception as e:
        log.error("Ошибка чтения данных pdf.", exc_info=e)
        await message.reply("Ошибка чтения данных pdf.")
        return

    # сохранение значений показателя
    try:
        result = await user.indicators.pdf_save_indicators(file_data)
        await message.reply(result)
    except Exception as e:
        await message.reply("Произошла ошибка при сохранении данных показателя.")
        log.error("Произошла ошибка при сохранении данных показателя.", exc_info=e)
        log.exception(e)


@router.message(F.document.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
async def handle_get_xlsx(message: types.Message, user: "User") -> None:  # noqa ARG001
    """Сохранение данных из загруженного файла XLSX."""
    # TODO NotImplemented
    file_name = message.document.file_name
    if not file_name.endswith(".xlsx"):
        await message.reply(f"Файл: {file_name} должен быть .xlsx")

    try:
        # получение объекта книги excel
        file_id = message.document.file_id
        bot = message.bot
        file = await bot.get_file(file_id)
        file_data = await bot.download_file(file.file_path)
        workbook = load_workbook(filename=file_data)

        # Получение данных из ячейки
        sheet = workbook.active
        cell_data = sheet["N14"].value  # noqa F841

    except Exception as e:
        await message.reply(f"Произошла ошибка: {e!s}")
