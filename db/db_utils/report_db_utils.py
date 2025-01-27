"""Утилиты работы с БД для отчётов."""
import datetime

from collections import defaultdict

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Report as ReportModel
from db.models import Indicator, IndicatorParams
from db.database import connection
from logger_config import log


@connection
async def get_all_indicators_report_data(user_id: int,
                                         session: AsyncSession,
                                         start: datetime.date | None = None,
                                         end: datetime.date | None = None,
                                         ) -> dict:
    """Получение данных для отчёта."""
    result_dict = defaultdict(dict)
    stmt = (
        select(
            Indicator.id,
            Indicator.date,
            Indicator.indicator_name,
            Indicator.indicator_value,
            IndicatorParams.calc_as_average,
        )
        .join(Indicator.indicator_params)
        .where(Indicator.user_id == user_id)
        .filter(Indicator.date.between(start, end))
    )
    result = await session.execute(stmt)
    report_data = result.mappings()

    for data in report_data:
        indicator_name = data["indicator_name"]
        date = data["date"]
        indicator_value = data["indicator_value"]
        calc_as_average = data["calc_as_average"]
        result_dict[indicator_name].update({
            "calc_as_average": calc_as_average,
            date: {"indicator_value": indicator_value},
        })

    return dict(result_dict)


@connection
async def save_report_data(data: dict, session: AsyncSession) -> None:
    """Сохранение отчёта."""
    stmt = select(exists().where(ReportModel.name == data.get("name")))
    result = await session.execute(stmt)
    is_exists = result.scalar()
    if is_exists:
        log.debug("Отчёт {name} уже существует.", name=data.get("name"))
        return

    try:
        report = ReportModel(**data)
        session.add(report)
        await session.commit()
        log.debug("Данные отчёта {name} сохранены.", name=data["name"])
    except Exception as e:
        await session.rollback()
        log.error("Ошибка при сохранении отчёта.", exc_info=e)
        log.exception(e)
        raise
