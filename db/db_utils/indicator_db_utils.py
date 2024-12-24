import asyncio
from collections import defaultdict
from typing import Sequence

from db.database import connection
from db.models import IndicatorParams

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from config import BaseDIR
from pathlib import Path
import json
from logger_config import log
from sqlalchemy.exc import IntegrityError


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
        result[project_name][description_literal] = indicator_name

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
            result[project_name] = indicator_name

    return result


if __name__ == '__main__':
    # asyncio.run(add_indicator_params_json())
    # asyncio.run(get_indicator_params(params_filter={'description_based_method': True}))
    asyncio.run(get_project_indicator_dict(user_id=1))
