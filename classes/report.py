import datetime
import io

from enums import ReportType
from utils.report_utils import reports_creation
from db.db_utils.report_db_utils import save_report_data
from config import first_day_to_report, today

# TODO V1.0:
#       - Добавить функцию получения отчёта сохранённого в БД
#       - Подробный отчёт по определённой метке (или ввести показатель, который попадёт в общий отчёт?)
#       - Добавить тип отчёта по одному показателю
#       - Добавить выбор интервала времени from start to end при формировании отчёта, вместо импорта из конфига
#       - Добавить получение файла excel c данными всей таблицы показателей для пользователя
#       - Добавить получение файла excel с данными всех таблиц для пользователя


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
            self.name = name
        self.report_type = report_type
        if start is None:
            self.start = first_day_to_report
        if end is None:
            self.end = today
        self.user_id = user_id
        self.content = content

    async def create(self) -> io.BytesIO:
        """Создание отчёта"""
        if ReportType.FULL:
            return await reports_creation.create_full_html_report(user_id=self.user_id,
                                                                  start=self.start,
                                                                  end=self.end, )

    async def save(self):
        """Сохранение отчёта"""
        await save_report_data(self.to_dict())

    def to_dict(self):
        """ Атрибуты в словарь """
        return self.__dict__
