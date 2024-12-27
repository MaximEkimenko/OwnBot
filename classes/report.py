from datetime import datetime
from classes.indicator import Indicator
from enums import ReportType


class Report:
    """Отчёт"""
    def __init__(self,
                 start: datetime,
                 end: datetime,
                 name: str | None = None,
                 report_type: ReportType = ReportType.FULL):
        if not name:
            self.name = 'regular'
        else:
            self.name = self.validate_name(name)
        self.report_type = report_type
        self.start = start
        self.end = end

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






    def create(self, start: datetime, end: datetime):
        # Логика создания отчета
        self.start = start
        self.end = end


    def send(self, address: str):
        # Логика отправки отчета
        pass