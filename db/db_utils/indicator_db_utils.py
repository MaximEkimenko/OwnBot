"""Утилиты работы с БД для показателей (Indicator, Indicator Params)."""
import json
import asyncio
import datetime

from pathlib import Path
from collections import defaultdict
from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from config import BaseDIR, init_today
from db.models import Indicator, IndicatorParams
from db.database import connection
from logger_config import log


# CREATE
@connection
async def add_indicator_params_json(user_id: int, session: AsyncSession) -> bool:
    """Заполнение параметров показателя."""
    json_path = BaseDIR / Path("global_settings") / "indicators.json"
    # TODO обработать ошибку на уровне выше, вернуть пользователю соответствующее сообщение
    if not json_path.is_file():
        error_message = f"Файл indicators.json не найден по пути {json_path}."
        log.error(error_message)
        raise FileNotFoundError(error_message)

    try:
        with Path(json_path).open("r", encoding="utf-8") as json_indicator:
            indicator_data = json.load(json_indicator)

        for line in indicator_data:
            line.update({"user_id": user_id})

    except Exception as e:
        log.error("Ошибка чтения файла indicators.json.", exc_info=e)
        log.exception(e)

    try:
        indicator_params = [IndicatorParams(**data) for data in indicator_data]
        session.add_all(indicator_params)
        await session.commit()

    except IntegrityError:
        log.warning("Такие показатели уже существуют.")

        return False

    return True


@connection
async def create_indicator_params(user_id: int, data: dict, session: AsyncSession) -> str:
    """Добавление параметров показателя."""
    indicator_name = data.get("indicator_name")
    stmt = (
        select(IndicatorParams.indicator_name)
        .where(IndicatorParams.user_id == user_id,
               IndicatorParams.indicator_name == indicator_name)
    )

    result = await session.execute(stmt)
    exist_indicator = result.scalar_one_or_none()
    if exist_indicator:
        log.debug("Ввод существующего показателя пользователем {user_id} с именем {indicator_name} уже существует.",
                  user_id=user_id, indicator_name=indicator_name)
        return f"Показатель с именем {indicator_name} уже существует."

    project_name = data.get("project_name")
    stmt = (
        select(IndicatorParams.indicator_name)
        .where(IndicatorParams.user_id == user_id,
               IndicatorParams.project_name == project_name)
    )
    result = await session.execute(stmt)
    exist_project = result.scalars().all()
    if not exist_project:
        log.debug("Ввод несуществующего проекта пользователем {user_id} с именем {project_name}.",
                  user_id=user_id, project_name=project_name)
        return f"Проект с именем {project_name} не существует. Выберите существующий проект."

    indicator_params = IndicatorParams(indicator_name=data.get("indicator_name"),
                                       user_id=user_id,
                                       project_name=data.get("project_name"),
                                       label_name=data.get("label_name"),
                                       task_name=data.get("task_name"),
                                       description_literal=data.get("description_literal"),
                                       calc_as_average=data.get("calc_as_average"),
                                       project_track_based_method=data.get("project_track_based_method"),
                                       description_based_method=data.get("description_based_method"),
                                       quantity_based_method=data.get("quantity_based_method"),
                                       file_based_method=data.get("file_based_method"),
                                       label_track_based_method=data.get("label_track_based_method"),
                                       task_name_track_based_method=data.get("task_name_track_based_method"),
                                       file_read_param=data.get("file_read_param"),
                                       )
    session.add(indicator_params)
    await session.commit()
    log.debug("Показатель с именем {indicator_name} создан пользователем {user_id}.",
              user_id=user_id, indicator_name=indicator_name)
    return f"Показатель с именем {indicator_name} создан."


# UPDATE
@connection
async def create_or_update_indicators(user_id: int, data: dict, session: AsyncSession) -> str:
    """Заполнение показателей из словаря data."""
    today = init_today()
    result_string = ""
    for indicator_name, indicator_value_dict in data.items():
        indicator_params_id = indicator_value_dict["params_id"]
        indicator_value = indicator_value_dict["value"]
        stmt = (select(Indicator.indicator_value)
                .where(Indicator.user_id == user_id,
                       Indicator.indicator_name == indicator_name,
                       Indicator.date == today)
                )
        result = await session.execute(stmt)
        exist_indicator_value = result.scalar_one_or_none()
        # если данные есть и они не изменились
        if exist_indicator_value == int(indicator_value):
            result_string += f"Значение показателя {indicator_name} = {indicator_value} не изменилось.\n"
        # если нет данных - добавление
        elif exist_indicator_value is None:
            indicator = Indicator(
                date=today,
                user_id=user_id,
                indicator_name=indicator_name,
                indicator_params_id=indicator_params_id,
                indicator_value=indicator_value,
            )
            session.add(indicator)
            await session.commit()
            result_string += f"Показатель {indicator_name} = {indicator_value} добавлен.\n"
        else:  # иначе обновление
            stmt = (
                update(Indicator)
                .where(Indicator.user_id == user_id,
                       Indicator.indicator_name == indicator_name,
                       Indicator.date == today)
                .values(indicator_value=indicator_value)
            )
            await session.execute(stmt)
            await session.commit()
            result_string += f"Показатель {indicator_name} = {indicator_value} обновлён.\n"
    log.debug(result_string)
    return result_string


# READ
@connection
async def get_indicator_params(params_filter: dict, session: AsyncSession) -> Sequence[IndicatorParams]:
    """Получение показателей по фильтру."""
    try:
        query = (select(IndicatorParams)
                 .where(*[getattr(IndicatorParams, field) == value for field, value in params_filter.items()]))

        result = await session.execute(query)
        params = result.scalars().all()
    except IntegrityError as e:
        log.error("Ошибка БД при получении показателей.", exc_info=e)
        log.exception(e)
        raise

    return params


async def get_literal_project_dict(user_id: int) -> dict:
    """Получение словаря параметров для расчёта по описанию."""
    db_data: Sequence[IndicatorParams] = \
        await get_indicator_params(params_filter={"description_based_method": True,
                                                  "user_id": user_id})
    result = defaultdict(dict)
    for data in db_data:
        project_name = data.project_name
        description_literal = data.description_literal
        indicator_name = data.indicator_name
        result[project_name][description_literal] = {"indicator_name": indicator_name, "params_id": data.id}

    return dict(result)


async def get_project_indicator_dict(user_id: int) -> dict:
    """Получение словаря параметров для расчёта по количеству."""
    db_data: Sequence[IndicatorParams] = await get_indicator_params(params_filter={"quantity_based_method": True,
                                                                                   "user_id": user_id})
    result = {}
    for data in db_data:
        project_name = data.project_name
        indicator_name = data.indicator_name
        if project_name not in result:
            result[project_name] = {"indicator_name": indicator_name, "params_id": data.id}

    return result


async def get_indicator_file_params_dict(user_id: int, file_method: str) -> dict:
    """Получение словаря параметров для расчёта при чтении файла."""
    db_data: Sequence[IndicatorParams] = await get_indicator_params(params_filter={"file_based_method": file_method,
                                                                                   "user_id": user_id})
    result = {}
    for data in db_data:
        if data.file_read_param:
            indicator_name = data.indicator_name
            file_read_params = data.file_read_param
            params_id = data.id
            result[indicator_name] = {"file_read_params": file_read_params, "params_id": params_id}

    return result


@connection
async def get_indicator_params_id_dict(session: AsyncSession, user_id: int) -> dict:
    """Получение словаря показатель - параметры показателя."""
    stmt = select(IndicatorParams).where(IndicatorParams.user_id == user_id)
    result = await session.execute(stmt)
    indicator_params = result.scalars().all()

    return {indicator.indicator_name: indicator.id for indicator in indicator_params}


async def get_user_indicators(user_id: int) -> list:
    """Получение списка показателей пользователя."""
    indicators = await get_indicator_params(params_filter={"user_id": user_id})
    return [line.to_dict() for line in indicators]


@connection
async def get_added_indicators(user_id: int, date: datetime, session: AsyncSession) -> dict:
    """Получение заполненных показателей на дату date."""
    stmt = (select(Indicator)
            .where(Indicator.user_id == user_id,
                   Indicator.date == date)
            )
    result = await session.execute(stmt)
    return {line.indicator_name: line.indicator_value for line in result.scalars().all()}


if __name__ == "__main__":
    res = asyncio.run(get_added_indicators(user_id=1))
