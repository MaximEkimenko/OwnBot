"""Команды пользователя."""
import random

from aiogram import Bot, Router, types
from aiohttp import ClientSession
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender

import enums

from classes.user import User
from logger_config import log
from own_bot_exceptions import IntInputError, StringInputError
from utils.common_utils import get_bot_for_schedule, verify_string_as_filename
from utils.handlers_utils import send_email

router = Router(name=__name__)


@router.message(Command("register"))
async def handler_register(message: types.Message) -> None:
    """Регистрация нового пользователя."""
    user = await User.register(message.from_user.id)
    if not user:
        await message.answer(text=f"Данный пользователь {message.from_user.id} уже зарегистрирован.")
        log.warning(f"Попытка регистрации пользователя {message.from_user.id}, который уже зарегистрирован.")
        return

    log.success(f"Пользователь {message.from_user.id} успешно зарегистрирован.")
    await message.answer(text="Вы успешно зарегистрировались.")


@router.message(Command("add_token"))
async def handler_add_token(message: types.Message, user: User) -> None:
    """Обработка добавления Todoist токена пользователя."""
    command_elements = message.text.split()[1:]
    if len(command_elements) > 1:
        await message.answer(text="Неверное количество параметров. Пример: /add_token `строка токена`")
        log.warning(f"Неверный ввод Todoist токена {message.from_user.id}, "
                    f"который не указал токен.")
        return
    try:
        token = verify_string_as_filename(message.text.split(maxsplit=1)[1])
    except StringInputError as e:
        await message.answer(text=f"Неверно введён токен.\n{e.args[0]}")
        log.warning(f"Неверно введён токен пользователем {message.from_user.id}, ")
        return
    else:
        await message.answer(text=f"Todoist token успешно добавлен пользователем "
                                  f"{message.from_user.id}.")
        log.success(f"Todoist token успешно обновлён {message.from_user.id}, "
                    f"который не указал токен.")
        await user.add_todoist_token(token)


@router.message(Command("add_indicators"))
async def handler_add_indicators(message: types.Message, user: User) -> None:
    """Обработка добавления показателей пользователя из файла json."""
    result = await user.add_params_json()
    if not result:
        await message.answer(text="Показатели не добавлены, либо уже существуют. Проверьте файл json.")
        return

    log.debug(f"Пользователь {user.user_id} добавил показатели из файла json.")
    await message.answer(text="Показатели успешно добавлены.")


@router.message(Command("savetd"))
async def handler_savetd(message: types.Message, user: User) -> None:
    """Обработка ручного запуска сохранения todoist данных."""
    await message.answer(text="Начало выгрузки и сохранения задач todoist...")
    result = await user.save_todoist_data()
    await message.answer(result)


@router.message(Command("ind"))
async def handler_ind(message: types.Message, schedule_bot: Bot = None, user: User = None) -> bool:
    """Обработка ручного запуска расчёта показателей todoist данных."""
    # проверка задачи по расписанию
    bot = get_bot_for_schedule(message, schedule_bot)
    user_id = message.from_user.id
    await bot.send_message(chat_id=user_id, text="Начало обработки данных...")
    # выгрузка todoist
    todoist_result = await user.save_todoist_data()
    if todoist_result is None:
        await bot.send_message(chat_id=user_id, text="Ошибка todoist, попробуйте ещё раз.")
        return False
    await bot.send_message(chat_id=user_id, text=todoist_result)
    # расчёт показателей и сохранение в БД
    db_result = await user.indicators.calculate_save_indicators()
    # description based
    if db_result[0]:
        await bot.send_message(chat_id=user_id, text=db_result[0])
    # quantity based
    if db_result[1]:
        await bot.send_message(chat_id=user_id, text=db_result[1])
    # default values
    if db_result[2]:
        await bot.send_message(chat_id=user_id, text="Заполнение значениями по умолчанию:")
        await bot.send_message(chat_id=user_id, text=db_result[2])
    return True


@router.message(Command("report_create"))
async def handler_report_create(message: types.Message,
                                schedule_bot: Bot = None, user: User = None) -> None:
    """Команда получения отчётов."""
    # TODO REFACTOR all function
    bot = get_bot_for_schedule(message=message, schedule_bot=schedule_bot)
    user_id = message.from_user.id

    message_data = message.text.split(" ", 2)
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
        await bot.send_message(chat_id=user_id, text=f"Тип отчёта: {report_type!r}:")
    except IndexError:
        report_type = enums.ReportType.FULL.value  # тип отчёта по умолчанию
        await bot.send_message(chat_id=user_id, text=f"Тип отчёта: {enums.ReportType.FULL.value!r}:")
    except StringInputError as e:
        await message.answer(text=f"Неверно введён тип отчёта. {e.args[0]}")
        log.warning("Неверно введён тип отчёта. {errors}", errors={e.args[0]})
        return
    # проверка существования типа отчёта
    if report_type not in enums.ReportType:
        await bot.send_message(chat_id=user_id, text="Такого типа отчёта не существует. ")
        return
    report = await user.report_config(report_name=report_name, report_type=report_type)

    async with ChatActionSender.upload_document(bot=bot, chat_id=message.chat.id):
        file = await report.create()
    await bot.send_document(chat_id=user_id, document=types.BufferedInputFile(file=file.getvalue(),
                                                                              filename=f"{report.name}.html"))
    log.info(f"Отчёт успешно отравлен пользователю id={user.user_id} "
             f"{message.from_user.full_name}.")
    report.content = file.getvalue()
    await report.save()


@router.message(Command("update"))
async def handler_update(message: types.Message, user: User) -> None:
    """Команда для ручного обновления показателей."""
    command_elements = message.text.split()[1:]  # строка параметров
    # валидация ввода
    if len(command_elements) % 2 != 0:
        await message.answer(text="Неверно введена команда /update. "
                                  "Вид команды /update:\nпоказатель1 значение1 показатель2 значение2.")
        log.warning(f"Несоответствие показателей значениям при команден /update {message.text} "
                    f"пользователем id={user.user_id}.")
        return

    indicators = command_elements[::2]
    values = command_elements[1::2]

    for indicator in indicators:
        try:
            verify_string_as_filename(indicator)
        except StringInputError as e:
            await message.answer(text=f"Неверно введён показатель {indicator}. {e.args[0]}.")
            log.warning("Показатель {indicator} не прошёл валидацию. {traceback}.",
                        indicator=indicator,
                        traceback=e.args[0],
                        )
            return

    for value in values:
        try:
            int(value)
        except IntInputError as e:
            await message.answer(text=f"Неверно введёно значение показателя {value}. "
                                      f"Значение должно быть целым числом.")
            log.warning(f"Введено неверное значение показателя {value}. {e.args[0]}.")
            return

    indicators_dict = dict(zip(indicators, values, strict=False))
    # верификация показателей
    verificated_dict = await user.indicators.verificate_indicators(indicators_dict)
    if verificated_dict.get("*failed"):
        await message.answer(text=f'Показателя {verificated_dict["*failed"]} не существует.')
        log.warning("Ввод несуществующего показателя {failed_indicator}",
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


@router.message(Command("go"))
async def handler_go(message: types.Message, user: User, schedule_bot: Bot = None) -> None:
    """Выгрузка todoist, сохранение в БД, расчёт показателей, генерация отчёта, отправка отчёта."""
    # расчёт показателей
    is_ok_download_and_calculation = await handler_ind(message, schedule_bot, user=user)
    if is_ok_download_and_calculation is False:
        return
    # генерация и отправка отчёта
    await handler_report_create(message, schedule_bot, user=user)
    log.info("Успешный запуск команды /go. Пользователь id={id} telegram_id={telegram_id}.",
             id=user.user_id, telegram_id=message.from_user.id)


@router.message(Command("db"))
async def handler_db(message: types.Message, user: User) -> None:
    """Отправка копии файла БД на электронную почту."""
    # TODO добавить обработку варианта заполнения через sender.json
    from settings.mail_sender_config import files, receivers
    try:
        await send_email(receivers=receivers, files=files)
        await message.answer(text=f'"Письмо отправлено на: {receivers[0]}."')
        log.info("Письмо отправлено по ручной команде db на: {receiver}.",
                 receiver=receivers[0])
    except Exception as e:
        await message.answer(text="Ошибка отправки письма.")
        log.error("Ошибка при отправке письма ручной командой db: на: {receiver}."
                  "пользователем id={user_id.}, telegram_id={telegram_id}",
                  receiver=receivers[0],
                  user=user.user_id,
                  telegram_id=message.from_user.id)
        log.exception(e)


@router.message(Command("joke"))
async def handler_joke(message: types.Message, user: User) -> None:
    """Команда получения шутки из API http://rzhunemogu.ru/FAQ.aspx."""
    type_codes = (1, 4, 5, 8, 11, 14, 15, 18)
    type_of_joke = random.choice(type_codes)
    joke_url = f"http://rzhunemogu.ru/RandJSON.aspx?CType={type_of_joke}"
    async with ClientSession() as session, session.get(url=joke_url) as response:
        text = await response.text()
    text = (
        text.replace("content", "")
        .replace("{", "")
        .replace("}", "")
        .replace('"', "")
        .replace(":", "")
    )
    try:
        await message.reply(text=text)
    except Exception as e:
        log.error(f"Ошибка при отправке шутки пользователю id={user.user_id}")
        log.exception(e)
        await message.reply(text="Не найдено, попробуйте ещё раз.")
    else:
        log.debug(f"Шутка успешно отправлена пользователю id={user.user_id}")

