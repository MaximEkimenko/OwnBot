import asyncio
import datetime
from collections import defaultdict
from pprint import pprint
from typing import Sequence

from db.database import connection
from db.models import IndicatorParams
from db.models import Indicator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, exists
from config import BaseDIR
from pathlib import Path
import json
from logger_config import log
from sqlalchemy.exc import IntegrityError
from config import today


# CREATE
@connection
async def add_indicator_params_json(user_id: int, session: AsyncSession) -> bool:
    """Заполнение параметров показателя"""
    json_path = BaseDIR / Path('settings') / 'indicators.json'
    if not json_path.is_file():
        raise FileNotFoundError(f"Файл indicators.json не найден по пути {json_path}.")

    try:
        with open(json_path, mode='r', encoding='utf-8') as json_indicator:
            indicator_data = json.load(json_indicator)
            # indicator_data.update({'user_id': user_id})

        for line in indicator_data:
            line.update({'user_id': user_id})

    except Exception as e:
        log.error("Ошибка чтения файла indicators.json.")
        log.exception(e)
        raise e

    try:
        indicator_params = [IndicatorParams(**data) for data in indicator_data]
        session.add_all(indicator_params)
        await session.commit()

    except IntegrityError:
        log.warning('Такие показатели уже существуют.')
        return False

    return True


@connection
async def create_or_update_indicators(user_id: int, data: dict, session: AsyncSession) -> str:
    """Заполнение показателей из словаря data"""
    result_string = ''
    for indicator_name, indicator_value_dict in data.items():
        indicator_params_id = indicator_value_dict['params_id']
        indicator_value = indicator_value_dict['value']
        stmt = (select(Indicator.indicator_value)
                .where(Indicator.user_id == user_id,
                       Indicator.indicator_name == indicator_name,
                       Indicator.date == today)
                )
        result = await session.execute(stmt)
        exist_indicator_value = result.scalar_one_or_none()
        # если данные есть и они не изменились
        if exist_indicator_value == int(indicator_value):
            result_string += (f'Значение показателя {indicator_name} = {indicator_value}, '
                              f'для пользователя id={user_id} не изменилось.\n')
            log.debug(result_string)
            continue

        if exist_indicator_value is None:
            indicator = Indicator(
                date=today,
                user_id=user_id,
                indicator_name=indicator_name,
                indicator_params_id=indicator_params_id,
                indicator_value=indicator_value,

            )
            session.add(indicator)
            await session.commit()
            result_string += (f'Показатель {indicator_name} = {indicator_value}, '
                              f'для пользователя id={user_id} добавлен.\n')
            log.debug(result_string)
            continue
        else:
            stmt = (
                update(Indicator)
                .where(Indicator.user_id == user_id,
                       Indicator.indicator_name == indicator_name,
                       Indicator.date == today)
                .values(indicator_value=indicator_value)
            )
            await session.execute(stmt)
            await session.commit()
            result_string += (f'Показатель {indicator_name} = {indicator_value}, '
                              f'для пользователя id={user_id} обновлён.\n')
            log.debug(result_string)
            continue
    return result_string


# READ
@connection
async def get_indicator_params(params_filter: dict, session: AsyncSession) -> Sequence[IndicatorParams]:
    """Получение показателей по фильтру"""
    try:
        query = (select(IndicatorParams)
                 .where(*[getattr(IndicatorParams, field) == value for field, value in params_filter.items()]))

        result = await session.execute(query)
        params = result.scalars().all()
    except IntegrityError as e:
        log.error('Ошибка БД при получении показателей.')
        log.exception(e)
        raise e

    return params


async def get_literal_project_dict(user_id: int) -> dict:
    """Получение словаря параметров для расчёта по описанию"""
    db_data: Sequence[IndicatorParams] = \
        await get_indicator_params(params_filter={'description_based_method': True,
                                                  'user_id': user_id})

    result = defaultdict(dict)

    for data in db_data:
        project_name = data.project_name
        description_literal = data.description_literal
        indicator_name = data.indicator_name
        result[project_name][description_literal] = {'indicator_name': indicator_name, 'params_id': data.id}

    return dict(result)


async def get_project_indicator_dict(user_id: int):
    """Получение словаря параметров для расчёта по количеству"""
    db_data: Sequence[IndicatorParams] = await get_indicator_params(params_filter={'quantity_based_method': True,
                                                                                   'user_id': user_id})
    result = dict()
    for data in db_data:
        project_name = data.project_name
        indicator_name = data.indicator_name
        if project_name not in result:
            result[project_name] = {'indicator_name': indicator_name, 'params_id': data.id}

    return result


async def get_indicator_file_params_dict(user_id: int, file_method: str) -> dict:
    """Получение словаря параметров чтения файла"""
    db_data: Sequence[IndicatorParams] = await get_indicator_params(params_filter={'file_based_method': file_method,
                                                                                   'user_id': user_id})
    result = dict()
    for data in db_data:
        if data.file_read_param:
            indicator_name = data.indicator_name
            file_read_params = data.file_read_param
            params_id = data.id
            result[indicator_name] = {'file_read_params': file_read_params, 'params_id': params_id}

    return result


@connection
async def get_indicator_params_id_dict(session: AsyncSession, user_id: int) -> dict:
    """Получение словаря показатель - параметры показателя"""
    stmt = select(IndicatorParams).where(IndicatorParams.user_id == user_id)
    result = await session.execute(stmt)
    indicator_params = result.scalars().all()

    return {indicator.indicator_name: indicator.id for indicator in indicator_params}


if __name__ == '__main__':
    pass
    # asyncio.run(add_indicator_params_json())
    # print(asyncio.run(get_indicator_params(params_filter={'description_based_method': True})))
    # asyncio.run(get_literal_project_dict(user_id=1))
    asyncio.run(get_indicator_params_id_dict(user_id=1))
    # print(asyncio.run(create_or_update_indicators(user_id=1, data={'cndx': 1})))
