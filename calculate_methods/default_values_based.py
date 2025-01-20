import asyncio
import datetime
from collections import defaultdict
from db.db_utils.indicator_db_utils import (get_user_indicators,
                                            get_added_indicators,
                                            create_or_update_indicators)
from config import init_today
from logger_config import log


async def get_default_values_dict(user_id: int) -> str:
    """Получение словаря задач для заполнения значений по умолчанию"""
    today = init_today()
    yesterday = today - datetime.timedelta(days=1)
    # показатели пользователя
    user_indicators = await get_user_indicators(user_id)
    # показатели добавленные сегодня
    today_added_indicators = await get_added_indicators(user_id, date=today)
    # показатели добавленные вчера
    yesterday_added_indicators = await get_added_indicators(user_id, date=yesterday)
    default_values_dict = defaultdict(lambda: {'value': 0, 'params_id': None})
    for indicator_param in user_indicators:
        if indicator_param["indicator_name"] not in today_added_indicators:
            indicator_name = indicator_param["indicator_name"]
            params_id = indicator_param["id"]
            if not indicator_param["calc_as_average"]:
                try:
                    default_values_dict[indicator_name]['value'] = yesterday_added_indicators[indicator_name]
                except KeyError as e:
                    log.error("Не найден показатель {indicator_name} за вчерашний день для пользователя "
                              "{user_id}. Присвоено значение 0",
                              indicator_name=indicator_name,
                              user_id=user_id
                              )
                    log.exception(e)
                    default_values_dict[indicator_name]['value'] = 0
            default_values_dict[indicator_name]['params_id'] = params_id
    return await create_or_update_indicators(data=dict(default_values_dict), user_id=user_id)


if __name__ == "__main__":
    asyncio.run(get_default_values_dict(1))
