"""Исключения OwnBot."""


class EmptyValueInputError(ValueError):
    """Исключение для ввода пустого значения."""

    def __init__(self) -> None:
        """Инициализация текста исключения."""
        super().__init__("Значение не может быть пустым.")


class StringInputError(ValueError):
    """Исключение для ввода некорректного значения строки."""

    def __init__(
            self,
            *,
            invalid_chars: str | None = None,
            max_length: int | None = None,
            base_name: str | None = None,
    ) -> None:
        """Инициализация текста исключения."""
        messages = []

        if invalid_chars:
            messages.append(f"Строка содержит недопустимые символы: {invalid_chars}")
        if max_length:
            messages.append(f"Строка слишком длинная. Максимальная длина: {max_length} символов.")
        if base_name:
            messages.append(f"Строка {base_name} зарезервирована.")

        # Если ни одно из условий не сработало, добавляем сообщение по умолчанию
        if not messages:
            messages.append("Строка не должна начинаться или заканчиваться пробелами или точками.")

        # Объединяем все сообщения в одну строку
        error_message = " ".join(messages)
        super().__init__(error_message)


class IntInputError(ValueError):
    """Исключение для ввода некорректного ввода значения integer."""

    def __init__(self, number: str | int | float) -> None:
        """Инициализация текста исключения."""
        super().__init__(f"Неверно введено число: {number!r}.")


class UserDoesNotExistError(ValueError):
    """Исключение для несуществующего пользователя."""

    def __init__(self, telegram_id: int) -> None:
        """Инициализация текста исключения."""
        super().__init__(f"Зарегистрированного пользователя с {telegram_id} не существует.")


class CronWeekDayInputError(ValueError):
    """Исключение для некорректного ввода значения интервалов cron day_of_week."""

    def __init__(self) -> None:
        """Инициализация текста исключения."""
        msg = ("Неверно введен день недели. Требуется значение от 0(понедельник) "
               "до 6(воскресенье). "
               "Или интервал чисел в виде 0-6.")
        super().__init__(msg)


class StringLengthError(ValueError):
    """Исключение для превышения длины строки."""

    def __init__(self, str_length: int) -> None:
        """Инициализация текста исключения."""
        super().__init__(f"Текстовая строка слишком длинная. Максимальная длина: {str_length!r} символов.")


class TwoItersLengthError(Exception):
    """Исключение для сравнения длины двух Iterable."""


class SameTokenError(Exception):
    """Исключение при обновлении токена без изменений."""

    def __init__(self) -> None:
        """Инициализация текста исключения."""
        super().__init__("Данный todoist token уже ведён. Введите новый.")


class UnknownTaskTypeError(Exception):
    """Исключение для неизвестного типа задачи по расписанию."""
