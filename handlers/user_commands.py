from aiogram import Router, types
from aiogram.filters import Command
from utils.common_utils import user_auth, verify_string_as_filename
from logger_config import log

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
async def handler_ind(message: types.Message):
    """Обработка ручного запуска расчёта показателей todoist данных"""
    user = await user_auth(message)
    if user is False:
        return

    await message.answer(text='Начало обработки данных...')
    # выгрузка todoist
    todoist_result = await user.save_todoist_data()
    if todoist_result:
        await message.answer(text=todoist_result)
    # расчёт показателей и сохранение в БД
    db_result = await user.indicators.calculate_save_indicators()
    if db_result[0]:
        await message.answer(text=db_result[0])

    if db_result[1]:
        await message.answer(text=db_result[1])


@router.message(Command('update'))
async def handler_update(message: types.Message):
    """Команда дл ручного обновления показателей"""
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





