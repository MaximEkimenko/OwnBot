import asyncio
import datetime

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from config import settings
from utils.common_utils import user_auth, verify_string_as_filename, get_bot_for_schedule
from logger_config import log
import enums

router = Router(name=__name__)


@router.message(Command('savetd'))
async def handler_savetd(message: types.Message):
    """Обработка ручного запуска сохранения todoist данных"""
    user = await user_auth(message)
    if user is False:
        return

    await message.answer(text='Начало выгрузки и сохранения задач todoist...')
    result = await user.save_todoist_data()
    await message.answer(result)


@router.message(Command('ind'))
async def handler_ind(message: types.Message, schedule_bot=None):
    """Обработка ручного запуска расчёта показателей todoist данных"""
    user = await user_auth(message)
    if user is False:
        return

    # проверка задачи по расписанию
    bot = get_bot_for_schedule(message, schedule_bot)
    user_id = message.from_user.id

    # await message.answer(text='Начало обработки данных...')
    await bot.send_message(chat_id=user_id, text='Начало обработки данных...')
    # выгрузка todoist
    todoist_result = await user.save_todoist_data()
    if todoist_result:
        # await message.answer(text=todoist_result)
        await bot.send_message(chat_id=user_id, text=todoist_result)
    # расчёт показателей и сохранение в БД
    db_result = await user.indicators.calculate_save_indicators()
    if db_result[0]:
        # await message.answer(text=db_result[0])
        await bot.send_message(chat_id=user_id, text=db_result[0])

    if db_result[1]:
        # await message.answer(text=db_result[1])
        await bot.send_message(chat_id=user_id, text=db_result[1])


@router.message(Command('report_create'))
async def handler_report_create(message: types.Message, schedule_bot=None):
    """Команда получения отчётов"""
    user = await user_auth(message)
    if user is False:
        return

    # проверка задачи по расписанию
    bot = get_bot_for_schedule(message=message, schedule_bot=schedule_bot)
    user_id = message.from_user.id

    message_data = message.text.split(' ', 2)
    # валидация имени отчёта и типа отчёта # TODO выделить в функцию
    try:
        report_name = await verify_string_as_filename(message_data[1].strip())
    except IndexError:
        report_name = None  # имя отчёта по умолчанию определяется в классе Report
        await bot.send_message(chat_id=user_id, text='Имя отчёта по умолчанию.')
    try:
        report_type = await verify_string_as_filename(message_data[2].strip())
        await bot.send_message(chat_id=user_id, text=f'Тип отчёта {report_type!r}.')
    except IndexError:
        report_type = enums.ReportType.FULL.value  # тип отчёта по умолчанию
        await bot.send_message(chat_id=user_id, text=f'Тип отчёта по '
                                                     f'умолчанию: {enums.ReportType.FULL.value!r}.')
    # проверка существования типа отчёта
    if report_type not in enums.ReportType:
        bot.send_message(chat_id=user_id, text='Такого типа отчёта не существует. ')
        return
    report = await user.reports_config(report_name=report_name, report_type=report_type)

    async with ChatActionSender.upload_document(bot=bot, chat_id=message.chat.id):
        file = await report.create()
    await bot.send_document(chat_id=user_id, document=types.BufferedInputFile(file=file.getvalue(),
                                                                              filename=f'{report.name}.html'))
    log.info(f'Отчёт успешно отравлен пользователю id={user.user_id} '
             f'{message.from_user.full_name}.')
    report.content = file.getvalue()
    await report.save()


@router.message(Command('update'))
async def handler_update(message: types.Message):
    """Команда для ручного обновления показателей"""
    user = await user_auth(message)
    if user is False:
        return
    command_elements = message.text.split()[1:]  # строка параметров
    # валидация ввода
    if len(command_elements) % 2 != 0:
        await message.answer(text='Неверно введена команда /update. '
                                  'Вид команды /update:\nпоказатель1 значение1 показатель2 значение2.')
        log.warning(f'Несоответствие показателей значениям при команден /update {message.text} '
                    f'пользователем id={user.user_id}.')
        return

    indicators = command_elements[::2]
    values = command_elements[1::2]

    for indicator in indicators:
        try:
            await verify_string_as_filename(indicator)
        except ValueError as e:
            await message.answer(text=f'Неверно введён показатель {indicator}. {e.args[0]}.')
            log.warning(f"Показатель {indicators} не прошёл валидацию. {e.args[0]}.")
            return

    for value in values:
        try:
            int(value)
        except ValueError as e:
            await message.answer(text=f'Неверно введёно значение показателя {value}. '
                                      f'Значение должно быть целым числом.')
            log.warning(f"Введено неверное значение показателя {value}. {e.args[0]}.")
            return

    indicators_dict = dict(zip(indicators, values))
    # верификация показателей
    verificated_dict = await user.indicators.verificate_indicators(indicators_dict)
    if verificated_dict.get('*failed'):
        await message.answer(text=f'Показателя {verificated_dict["*failed"]} не существует.')
        log.warning(f'Ввод несуществующего показателя {verificated_dict["*failed"]}')
        return

    # обновление показателей
    result = await user.indicators.manual_update_save_indicators(verificated_dict)
    await message.answer(result)
    return


@router.message(Command('go'))
async def handler_go(message: types.Message, schedule_bot=None):
    """Выгрузка todoist, сохранение в БД, расчёт показателей, генерация отчёта, отправка отчёта"""
    user = await user_auth(message)
    if user is False:
        return
    # расчёт показателей
    await handler_ind(message, schedule_bot)
    # генерация отчёта
    await handler_report_create(message, schedule_bot)


@router.message(Command('test'))
async def handler_test(bot):
    now = datetime.datetime.now()
    user = types.User(id=settings.SUPER_USER_TG_ID, first_name='username',
                      last_name='', is_bot=False)
    chat = types.Chat(id=settings.SUPER_USER_TG_ID, type='')
    message = types.Message(from_user=user, chat=chat,
                            date=now, message_id=1234, text='/go', bot=bot)

    try:
        await handler_ind(message)
    except Exception as e:
        log.exception(e)


if __name__ == '__main__':
    pass
    # asyncio.run(handler_test())
