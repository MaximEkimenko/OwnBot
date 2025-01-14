class EmptyValueInputError(ValueError):
    """Исключение для ввода пустого значения"""


class StringInputError(ValueError):
    """Исключение для ввода некорректного ввода значения строки"""


class IntInputError(ValueError):
    """Исключение для ввода некорректного ввода значения integer"""


class UserDoesNotExistError(ValueError):
    """Исключение для несуществующего пользователя"""


class CronWeekDayInputError(ValueError):
    """Исключение для некорректного ввода значения интервалов cron day_of_week"""


class StringLengthError(ValueError):
    """"Исключение для превышения длины строки"""


class TwoItersLengthError(Exception):
    """Исключение для сравнения длины двух Iterable"""


class SameTokenError(Exception):
    """Исключение при обновлении токена без изменений"""
