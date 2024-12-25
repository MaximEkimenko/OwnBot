import asyncio
import datetime
from collections import defaultdict
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
async def create_or_update_indicators(user_id: int, data: tuple, session: AsyncSession):
    """Заполнение показателей из словаря data"""
    today = datetime.date.today()
    indicators_dict = data[0]
    indicator_params_id = data[1]
    for indicator_name, indicator_value in indicators_dict.items():
        stmt = select(exists()
                      .where(Indicator.user_id == user_id,
                             Indicator.indicator_name == indicator_name,
                             Indicator.date == today)

                      )
        is_exist = await session.scalar(stmt)
        if not is_exist:
            print('NOT EXIST!')
            indicator = Indicator(user_id=user_id,
                                  indicator_name=indicator_name,
                                  indicator_params_id=indicator_params_id,
                                  indicator_value=indicator_value,
                                  date=today
                                  )
            session.add(indicator)
            await session.commit()
            return indicator.id
        else:
            print('EXIST!')
            stmt = (
                update(Indicator)
                .where(Indicator.user_id == user_id,
                       Indicator.indicator_name == indicator_name,
                       Indicator.date == today)
                .values(indicator_value=indicator_value)
            )
            await session.execute(stmt)
            await session.commit()







    # try:
    #     while True:
    #         secret_key = random.randint(100000, 999999)
    #         stmt = select(exists().where(SecretKey.secret_key == secret_key))
    #         is_exist = await session.scalar(stmt)
    #         if not is_exist:
    #             break
    #
    #     secret = SecretKey(secret_key=secret_key, secret_key_status=enums.SecretKeyStatus.ACTIVE)
    #     session.add(secret)
    #     await session.commit()
    #     logger.debug('Created secret key successfully.')
    #     return {'secret_key_id': secret.id, 'secret_key': secret.secret_key}
    # except SQLAlchemyError:
    #     logger.error('Error creating secret key.')
    #     return None


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
            result[indicator_name] = file_read_params, params_id


    return result


if __name__ == '__main__':
    pass
    # asyncio.run(add_indicator_params_json())
    # asyncio.run(get_indicator_params(params_filter={'description_based_method': True}))
    # print(asyncio.run(create_or_update_indicators(user_id=1, data={'cndx': 1})))
