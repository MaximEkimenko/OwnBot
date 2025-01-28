"""Перечисления."""
import enum


class TaskType(str, enum.Enum):
    """Типы задач."""

    REMINDER = "напоминание"
    REPORT = "ежедневный отчёт"
    EMAIL = "отправка почты"

    @classmethod
    def get_task_type_translate_dict(cls) -> dict:
        """Словарь перевода пользовательских параметров в тип задачи."""
        return {"r": cls.REMINDER,  # напоминание
                "g": cls.REPORT,  # ежедневный отчёт
                "m": cls.EMAIL}  # отправка почты

    def __str__(self) -> str:
        """Value в строку."""
        return self.value


class ReportType(str, enum.Enum):
    """Типы отчетов."""

    FULL = "полный"
    INDICATOR = "показатель"
    GRAPH = "график"


class FileBasedMethods(str, enum.Enum):
    """Методы обработки файлов."""

    PDF = "pdf"
    XLSX = "xlsx"
