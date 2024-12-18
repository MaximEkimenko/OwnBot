from datetime import datetime
from indicator import Indicator
from enums import ReportType


class Report:
    """Отчёт"""
    def __init__(self, name: str, report_type: ReportType, start: datetime, end: datetime):
        self.name = name
        self.type = report_type
        self.start = start
        self.end = end
        self.indicators = []

    def create(self, start: datetime, end: datetime, indicators: list[Indicator]):
        # Логика создания отчета
        self.start = start
        self.end = end
        self.indicators = indicators

    def send(self, address: str):
        # Логика отправки отчета
        pass