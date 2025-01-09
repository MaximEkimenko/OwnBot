import enum


class TaskType(str, enum.Enum):
    """Типы задач."""
    REGULAR = 'регулярная'
    ONCE = 'разовая'
    DAILY = 'ежедневная'
    WEEKLY = 'еженедельная'
    REMINDER = 'напоминание'
    TASK = 'задача'


class ReportType(str, enum.Enum):
    """Типы отчетов."""
    FULL = 'полный'
    INDICATOR = 'показатель'
    GRAPH = 'график'


class FileBasedMethods(str, enum.Enum):
    """Методы обработки файлов"""
    PDF = 'pdf'
    XLSX = 'xlsx'

