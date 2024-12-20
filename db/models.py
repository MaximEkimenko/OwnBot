from sqlalchemy import ForeignKey, BIGINT, TIMESTAMP, DATETIME
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime

from .database import Base
from enums import TaskType, ReportType


class UserModel(Base):
    """Модель пользователя"""
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    todoist_token: Mapped[str] = mapped_column(nullable=True)

    indicators: Mapped[list["Indicator"]] = relationship("Indicator", back_populates="user")
    tasks: Mapped[list["ScheduleTask"]] = relationship("ScheduleTask", back_populates="user")
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="user")
    todoist_tasks: Mapped[list["TodoistTask"]] = relationship("TodoistTask", back_populates="user")


class Indicator(Base):
    """Модель показателей"""
    date: Mapped[datetime] = mapped_column(DATETIME)
    user_id: Mapped[int] = mapped_column(ForeignKey('usermodel.id'))
    indicator_name: Mapped[str] = mapped_column(unique=True)
    params: Mapped[dict | None] = mapped_column(JSON)
    user: Mapped[UserModel] = relationship("UserModel", back_populates="indicators")
    indicator_params: Mapped[list["IndicatorParams"]] = relationship("IndicatorParams",
                                                                     back_populates="indicator"
                                                                     )


class IndicatorParams(Base):
    """Модель параметров для расчёта показателей"""
    indicator_name: Mapped[str] = mapped_column(unique=True)
    calc_as_average: Mapped[bool] = mapped_column(default=False)
    project_name: Mapped[str]
    label_track_name: Mapped[str] = mapped_column(nullable=True)
    label_calc_name: Mapped[str] = mapped_column(nullable=True)
    track_by_name: Mapped[bool] = mapped_column(default=False)
    track_by_project: Mapped[bool] = mapped_column(default=False)

    indicator_id: Mapped[int] = mapped_column(ForeignKey('indicator.id'))
    indicator: Mapped[Indicator] = relationship("Indicator", back_populates="indicator_params")


class ScheduleTask(Base):
    """Модель задания по расписанию"""
    name: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('usermodel.id'))
    task_type: Mapped[TaskType] = mapped_column(default=TaskType.ONCE)
    schedule: Mapped[str]
    action: Mapped[str]

    user: Mapped[UserModel] = relationship("UserModel", back_populates="tasks")


class Report(Base):
    """Модель отчётов"""
    name: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('usermodel.id'))
    report_type: Mapped[ReportType] = mapped_column(default=ReportType.FULL)
    start: Mapped[datetime] = mapped_column(TIMESTAMP)
    end: Mapped[datetime] = mapped_column(TIMESTAMP)

    user: Mapped[UserModel] = relationship("UserModel", back_populates="reports")

    def __repr__(self):
        return self.__tablename__

class TodoistTask(Base):
    """Модель задач Todoist"""
    user_id: Mapped[int] = mapped_column(ForeignKey('usermodel.id'))
    task_item_id: Mapped[int]  # уникальный ключ item записи todoist api
    project_id: Mapped[int]  # id проекта
    task_id: Mapped[int]  # id задачи НЕ УНИКАЛЬНО для повторяющихся задач
    added_at: Mapped[datetime] = mapped_column(TIMESTAMP)  # дата добавления задачи в todoist
    task: Mapped[str] = mapped_column()
    project: Mapped[str] = mapped_column(nullable=True)
    labels: Mapped[str] = mapped_column(nullable=True)
    priority: Mapped[int] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    completed_at: Mapped[datetime] = mapped_column(TIMESTAMP)

    user: Mapped[UserModel] = relationship("UserModel", back_populates="todoist_tasks")

    def __repr__(self):
        return self.__tablename__
