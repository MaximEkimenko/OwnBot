import asyncio
import datetime
from pprint import pprint
from collections import defaultdict

from config import today, first_day_to_report
from logger_config import log

from db.models import Indicator, IndicatorParams
from db.database import connection
from db.models import Report as ReportModel

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession


@connection
async def get_all_indicators_report_data(user_id,
                                         session: AsyncSession,
                                         start: datetime.date | None = None,
                                         end: datetime.date | None = None,
                                         ) -> dict:
    """Получение данных для отчёта"""
    result_dict = defaultdict(dict)
    stmt = (
        select(
            Indicator.id,
            Indicator.date,
            Indicator.indicator_name,
            Indicator.indicator_value,
            IndicatorParams.calc_as_average
        )
        .join(Indicator.indicator_params)
        .where(Indicator.user_id == user_id)
        .filter(Indicator.date.between(start, end))
    )
    result = await session.execute(stmt)
    report_data = result.mappings()

    for data in report_data:
        indicator_name = data['indicator_name']
        date = data['date']
        indicator_value = data['indicator_value']
        calc_as_average = data['calc_as_average']
        result_dict[indicator_name].update({
            'calc_as_average': calc_as_average,
            date: {'indicator_value': indicator_value},
        })

    return dict(result_dict)


@connection
async def save_report_data(data: dict, session: AsyncSession) -> None:
    """Сохранение отчёта"""
    stmt = select(exists().where(ReportModel.name == data.get('name')))
    result = await session.execute(stmt)
    is_exists = result.scalar()
    if is_exists:
        log.debug(f'Отчёт {data.get('name')} уже существует.')
        return

    try:
        report = ReportModel(**data)
        session.add(report)
        await session.commit()
        log.debug(f'Данные отчёта сохранены {data["name"]}.')
    except Exception as e:
        await session.rollback()
        log.error(f'Ошибка при сохранении отчёта.')
        log.exception(e)


# TODO delete if not used
# @connection
# async def get_full_report_data(user_id,
#                           session: AsyncSession,
#                           start: datetime.date | None = None,
#                           end: datetime.date | None = None,
#                           ) -> list:
#     """Получение данных для отчёта"""
#     result_dict = defaultdict(dict)
#     start_date = first_day_to_report if start is None else start
#     end_date = today if end is None else end
#     stmt = (
#         select(
#             Indicator,
#             # Indicator.id,
#             # Indicator.date,
#             # Indicator.indicator_name,
#             # Indicator.indicator_value,
#             # IndicatorParams.calc_as_average
#             IndicatorParams
#         )
#         .join(Indicator.indicator_params)
#         .where(Indicator.user_id == user_id)
#         .filter(Indicator.date.between(start_date, end_date))
#     )
#     result = await session.execute(stmt)
#     report_data = result.mappings()
#     # report_data = result.scalars().all()
#
#     for data in report_data:
#         # pprint(data[0].to_dict())
#         # pprint(data[1].to_dict())
#         # result_dict[data[0].indicator_name].update({data[0].date: data[0].to_dict() })
#                                                     # | data[0].indicator_params.to_dict()})
#
#
#         # print(data[0].indicator_params.to_dict())
#         # result_dict[data.indicator_name].update({data.date: data.to_dict()})
#
#     pprint(result_dict)
#
#     return list(report_data)


if __name__ == '__main__':
    # asyncio.run(get_all_indicators_report_data(user_id=1))
    asyncio.run(save_report_data(data={'name':1}))
    # save_report_data
