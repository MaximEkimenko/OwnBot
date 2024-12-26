from openpyxl import load_workbook
from aiogram import Router, types, F
from classes.user import User
from logger_config import log

router = Router(name=__name__)


@router.message(F.document.mime_type == "application/pdf")
async def handle_get_pdf(message: types.Message):
    # инициализация пользователя
    user = await User.auth(message.from_user.id)
    # проверка расширения
    file_name = message.document.file_name
    if not file_name.endswith('.pdf'):
        await message.reply(f"Файл: {file_name} должен быть .pdf")
    # чтение файла
    try:
        file_id = message.document.file_id
        bot = message.bot
        file = await bot.get_file(file_id)
        file_data = await bot.download_file(file.file_path)
    except Exception as e:
        log.error('Ошибка чтения данных pdf.')
        log.exception(e)
        await message.reply(f'Ошибка чтения данных pdf.')
        return

    # сохранение значений показателя
    try:
        result = await user.indicators.pdf_save_indicators(file_data)
        await message.reply(result)
    except Exception as e:
        await message.reply(f"Произошла ошибка при сохранении данных показателя.")
        log.error(f"Произошла ошибка при сохранении данных показателя.")
        log.exception(e)


@router.message(F.document.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
async def handle_get_xlsx(message: types.Message):
    # инициализация пользователя
    # TODO Implementation
    # проверка расширения
    file_name = message.document.file_name
    if not file_name.endswith('.xlsx'):
        await message.reply(f"Файл: {file_name} должен быть .xlsx")

    try:
        # получение объекта книги excel;
        file_id = message.document.file_id
        bot = message.bot
        file = await bot.get_file(file_id)
        file_data = await bot.download_file(file.file_path)
        workbook = load_workbook(filename=file_data)
        # передача методу пользователя workbook

        # Логика расчёта cndx
        sheet = workbook.active
        sum = sheet['N14'].value
        print(sum)


    except Exception as e:
        print(e)
        await message.reply(f"Произошла ошибка: {str(e)}")