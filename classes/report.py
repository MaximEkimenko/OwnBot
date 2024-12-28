import datetime
import io

from enums import ReportType
from utils.report_utils import reports_creation
from db.db_utils.report_db_utils import save_report_data
import enums
from config import first_day_to_report, today


class Report:
    """Отчёт"""
    def __init__(self,
                 user_id: int | None,
                 name: str | None = None,
                 start: datetime.date | None = None,
                 end: datetime.date | None = None,
                 content: str | None = None,
                 report_type: ReportType | None = ReportType.FULL, ):
        if not name:
            self.name = 'regular'
        else:
            self.name = self.validate_name(name)
        self.report_type = report_type
        if start is None:
            self.start = first_day_to_report
        if end is None:
            self.end = today
        self.user_id = user_id
        self.content = content

    @staticmethod
    def validate_name(name: str) -> str:
        r"""
        Валидация имени отчёта.
        Запрещены следующие символы: _!&"\/:|<>*?
        """
        banned_symbols = r'_!&"\/:|<>*?'
        for symbol in name:
            if symbol in banned_symbols:
                raise ValueError(symbol, banned_symbols)
        return name

    async def create(self) -> io.BytesIO:
        """Создание отчёта"""
        if enums.ReportType.FULL:
            return await reports_creation.create_full_html_report(user_id=self.user_id,
                                                                  start=self.start,
                                                                  end=self.end,
                                                                  )

    async def save(self):
        """Сохранение отчёта"""
        await save_report_data(self.to_dict())

    async def get(self):
        # TODO
        """Получение существующего отчёта по имени"""

    def to_dict(self):
        # атрибуты в словарь
        return self.__dict__
