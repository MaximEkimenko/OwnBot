from datetime import datetime
from indicator import Indicator
from enums import ReportType


class Report:
    """Отчёт"""
    def __init__(self, name: str,
                 start: datetime,
                 end: datetime,
                 report_type: ReportType = ReportType.FULL):
        self.name = name
        self.report_type = report_type
        self.start = start
        self.end = end

    def create(self, start: datetime, end: datetime):
        # Логика создания отчета
        self.start = start
        self.end = end


    def send(self, address: str):
        # Логика отправки отчета
        pass