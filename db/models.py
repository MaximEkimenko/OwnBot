from sqlalchemy import ForeignKey, BIGINT, TIMESTAMP, DATETIME, UniqueConstraint
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
    indicator_params: Mapped[list["IndicatorParams"]] = relationship("IndicatorParams",
                                                                     back_populates="user")


class Indicator(Base):
    """Модель показателей"""
    date: Mapped[datetime] = mapped_column(DATETIME)
    user_id: Mapped[int] = mapped_column(ForeignKey('usermodel.id'))
    indicator_name: Mapped[str] = mapped_column(unique=True)
    params: Mapped[dict | None] = mapped_column(JSON)
    user: Mapped[UserModel] = relationship("UserModel", back_populates="indicators")

    indicator_params_id: Mapped[int] = mapped_column(ForeignKey('indicatorparams.id'))
    indicator_params: Mapped['IndicatorParams'] = relationship("IndicatorParams", back_populates="indicator")

    # для каждого пользователя indicator_name уникален
    __table_args__ = (
        UniqueConstraint('user_id', 'indicator_name', name='uq_user_indicator'),
    )


class IndicatorParams(Base):
    """Модель параметров для расчёта показателей"""
    indicator_name: Mapped[str]  # имя показателя
    # имя проекта для реализации расчёта по имени проекта
    project_name: Mapped[str] = mapped_column(nullable=True)
    # имя метки для реализации методики расчёта по метке
    label_name: Mapped[str] = mapped_column(nullable=True)
    # имя задачи для реализации методики расчёта по задаче
    task_name: Mapped[str] = mapped_column(nullable=True)
    # литерал описания для реализации методики расчёта на основании описания
    description_literal: Mapped[str] = mapped_column(nullable=True, unique=True)

    # методика расчёта показателя по среднему (показатель является средней величиной)
    calc_as_average: Mapped[bool] = mapped_column(default=False)
    # методика расчёта на основании имени проекта
    project_track_based_method: Mapped[bool] = mapped_column(default=False)
    # методика расчёта на основании описания
    description_based_method: Mapped[bool] = mapped_column(default=False)
    # методика расчёта на основании количества выполненных задач
    quantity_based_method: Mapped[bool] = mapped_column(default=False)
    # методика расчёта на основании данных внешних файлов
    file_based_method: Mapped[bool] = mapped_column(default=False)
    # методика расчёта по имени метки
    label_track_based_method: Mapped[bool] = mapped_column(default=False)
    # методика расчёта по имени задачи
    task_name_track_based_method: Mapped[bool] = mapped_column(default=False)

    indicator: Mapped['Indicator'] = relationship("Indicator", back_populates="indicator_params")

    user_id: Mapped[int] = mapped_column(ForeignKey('usermodel.id'))
    user: Mapped[UserModel] = relationship("UserModel", back_populates="indicator_params")

    # для каждого пользователя indicator_name уникален
    __table_args__ = (
        UniqueConstraint('user_id', 'indicator_name', name='uq_user_indicator'),
    )



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
