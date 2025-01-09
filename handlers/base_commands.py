from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from config import settings
from aiogram.types import FSInputFile
from openpyxl import load_workbook
from io import BytesIO
import re
from logger_config import log
from classes.user import User


router = Router(name=__name__)

@router.message(CommandStart())
async def handle_start(message: types.Message):

    text = 'Started'





    await message.answer(
        text=text,
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("help"))
async def handle_help(message: types.Message):
    """Инструкция пользователя"""
    # if await is_approved_doer_request(message, 'help'):
    #     text = 'Вызвана команда help пользователем'
    #     await message.answer(
    #         text=text,
    #     )
    # elif await is_admin_request(message, 'help'):
    #     text = 'Вызвана команда help админом'
    #     await message.answer(
    #         text=text,
    #     )











# async def get_file(message: types.Message) -> None:
#     """
#     Загружает файл отправленный боту, сохраняет в директории загрузки под тем же именем
#     """
#     now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
#     if message.from_user.id == admin_id:
#         if message.from_user.id == admin_id:
#             try:
#                 download_path = r'file_folder'
#                 file = await bot.get_file(message.document.file_id)
#                 await file.download(destination_file=os.path.join(download_path, message.document.file_name))
#                 await message.reply(text="Успешно загружено")
#                 logger.info(f"Успешно загружено {file['file_path']}, в директорию: {download_path}, в {now}")
#             except Exception as e:
#                 logger.error(f"Ошибка загрузка файла {now}")
#                 logger.exception(e)
#     else:
#         await message.answer("У вас нет доступа.")
#         logger.warning(f"Попытка доступа вызова команды без доступа сообщение: {message}, "
#                        f"пользователь telegram {message.from_user.id}, "
#                        f"дата {now}.")
#         await bot.send_message(chat_id=admin_id,
#                                text=f"Попытка доступа вызова команды без доступа сообщение: {message}, "
#                                     f"пользователь telegram {message.from_user.id}, "
#                                     f"дата {now}.")





@router.message(Command("info", prefix="!/"))
async def handle_info_command(message: types.Message):
    text = 'Вызвана команда info'
    await message.answer(
        text=text

    )