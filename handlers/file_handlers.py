from aiogram import F, Router, types
from openpyxl import load_workbook

from classes.user import User
from logger_config import log

router = Router(name=__name__)


@router.message(F.document.mime_type == "application/pdf")
async def handle_get_pdf(message: types.Message, user: User):
    """Сохранение данных из загруженного файла PDF"""
    # user = await User.auth(message.from_user.id)
    # if user is False:
    #     return
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
async def handle_get_xlsx(message: types.Message, user: User):
    """Сохранение данных из загруженного файла XLSX"""
    # TODO NotImplemented
    # user = await User.auth(message.from_user.id)
    # if user is False:
    #     return
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
        cell_data = sheet["N14"].value
        print(cell_data)

    except Exception as e:
        await message.reply(f"Произошла ошибка: {e!s}")
