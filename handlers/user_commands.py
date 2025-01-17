from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from utils.common_utils import verify_string_as_filename, get_bot_for_schedule
from utils.handlers_utils import user_auth, send_email
# from utils.scheduler_utils.scheduler_actions import schedule_send_mail
from logger_config import log
import enums

from own_bot_exceptions import StringInputError, IntInputError

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

    await bot.send_message(chat_id=user_id, text='Начало обработки данных...')
    # выгрузка todoist
    todoist_result = await user.save_todoist_data()
    if todoist_result:
        await bot.send_message(chat_id=user_id, text=todoist_result)
    # расчёт показателей и сохранение в БД
    db_result = await user.indicators.calculate_save_indicators()
    if db_result[0]:
        await bot.send_message(chat_id=user_id, text=db_result[0])

    if db_result[1]:
        await bot.send_message(chat_id=user_id, text=db_result[1])


@router.message(Command('report_create'))
async def handler_report_create(message: types.Message, schedule_bot=None):
    """Команда получения отчётов"""
    # TODO REFACTOR
    user = await user_auth(message)
    if user is False:
        return

    # проверка задачи по расписанию
    bot = get_bot_for_schedule(message=message, schedule_bot=schedule_bot)
    user_id = message.from_user.id

    message_data = message.text.split(' ', 2)
    # валидация имени отчёта и типа отчёта # TODO выделить в функцию в handler_utils
    try:
        report_name = verify_string_as_filename(message_data[1].strip())
    except IndexError:
        report_name = None  # имя отчёта по умолчанию определяется в классе Report
    except StringInputError as e:
        await message.answer(text=f"Неверно введёно имя отчёта. {e.args[0]}")
        log.warning("Неверно введёно имя отчёта.  {errors}", errors={e.args[0]})
        return
    try:
        report_type = verify_string_as_filename(message_data[2].strip())
        await bot.send_message(chat_id=user_id, text=f'Тип отчёта: {report_type!r}:')
    except IndexError:
        report_type = enums.ReportType.FULL.value  # тип отчёта по умолчанию
        await bot.send_message(chat_id=user_id, text=f'Тип отчёта: {enums.ReportType.FULL.value!r}:')
    except StringInputError as e:
        await message.answer(text=f"Неверно введён тип отчёта. {e.args[0]}")
        log.warning("Неверно введён тип отчёта. {errors}", errors={e.args[0]})
        return
    # проверка существования типа отчёта
    if report_type not in enums.ReportType:
        bot.send_message(chat_id=user_id, text='Такого типа отчёта не существует. ')
        return
    report = await user.report_config(report_name=report_name, report_type=report_type)

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
            verify_string_as_filename(indicator)
        except StringInputError as e:
            await message.answer(text=f'Неверно введён показатель {indicator}. {e.args[0]}.')
            log.warning("Показатель {indicator} не прошёл валидацию. {traceback}.",
                        indicator=indicator,
                        traceback=e.args[0]
                        )
            return

    for value in values:
        try:
            int(value)
        except IntInputError as e:
            await message.answer(text=f'Неверно введёно значение показателя {value}. '
                                      f'Значение должно быть целым числом.')
            log.warning(f"Введено неверное значение показателя {value}. {e.args[0]}.")
            return

    indicators_dict = dict(zip(indicators, values))
    # верификация показателей
    verificated_dict = await user.indicators.verificate_indicators(indicators_dict)
    if verificated_dict.get('*failed'):
        await message.answer(text=f'Показателя {verificated_dict["*failed"]} не существует.')
        log.warning('Ввод несуществующего показателя {failed_indicator}',
                    failed_indicator=verificated_dict["*failed"])
        return

    # обновление показателей
    result = await user.indicators.manual_update_save_indicators(verificated_dict)
    log.info("Успешное обновление показателей {indicators} значениями {values} командой /update. Пользователь id={id} "
             "telegram_id={telegram_id}.",
             indicators=indicators, values=values,
             id=user.user_id, telegram_id=message.from_user.id)
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

    # TODO проверка какие показатели не были переданы в этот день и присвоение значений по умолчанию
    #  в зависимости от IndicatorParams

    # генерация и отправка отчёта
    await handler_report_create(message, schedule_bot)
    log.info("Успешный запуск команды /go. Пользователь id={id} telegram_id={telegram_id}.",
             id=user.user_id, telegram_id=message.from_user.id)


@router.message(Command('db'))
async def handler_db(message: types.Message):
    """Отправка копии файла БД на электронную почту"""
    user = await user_auth(message)
    if user is False:
        return
    # TODO добавить обработку варианта заполнения через sender.json
    from settings.mail_sender_config import receivers, files
    try:
        await send_email(receivers=receivers, files=files)
        await message.answer(text=f'"Письмо отправлено на: {receivers[0]}."')
        log.info("Письмо отправлено по ручной команде db на: {receiver}.",
                 receiver=receivers[0])
    except Exception as e:
        await message.answer(text=f'Ошибка отправки письма.')
        log.error("Ошибка при отправке письма ручной командой db: на: {receiver}."
                  "пользователем id={user_id.}, telegram_id={telegram_id}",
                  receiver=receivers[0],
                  user=user.user_id,
                  telegram_id=message.from_user.id)
        log.exception(e)
