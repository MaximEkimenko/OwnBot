"""Обработка команд управления задачами по расписанию."""
from logger_config import log
from utils.scheduler_utils.scheduler_actions import (
    schedule_send_mail,
    schedule_send_reminder,
    schedule_every_day_report,
)
from utils.scheduler_utils.scheduler_manager import scheduler


def add_or_update_scheduler_task(schedule_params: dict, user_id: int) -> None:
    """Добавление / обновление задачи по расписанию при изменении, добавлении данных задачи пользователем."""
    # словарь стратегий планирования в зависимости от типа задачи
    task_type = schedule_params["task_type"]
    task_kwargs = schedule_params["task_kwargs"]
    actions = {
        task_type.REPORT: schedule_every_day_report,
        task_type.REMINDER: schedule_send_reminder,
        task_type.EMAIL: schedule_send_mail,
    }

    # добавление задачи
    task_id = schedule_params["id"] + str(user_id)
    # удаление существующей задачи
    job = scheduler.get_job(task_id)
    if job:
        scheduler.remove_job(task_id)

    scheduler.add_job(
        actions[task_type],
        trigger="cron",
        day_of_week=schedule_params["day_of_week"],
        hour=schedule_params["hour"],
        minute=schedule_params["minute"],
        id=task_id,
        misfire_grace_time=60 * 2,
        kwargs=task_kwargs,
        jobstore="default",
    )
    log.info("Задача:{task_id} запланирована успешно для пользователя:{user}, "
             "тип:{task_type}.",
             task_type=task_type.name, user=user_id, task_id=task_id)


def delete_scheduler_task(task_name: str, user_id: int) -> None:
    """Удаление задачи по расписанию."""
    task_id = task_name + str(user_id)
    job = scheduler.get_job(task_id)
    if job:
        scheduler.remove_job(task_id)
    log.info("Задача:{task_id} удалена успешно для пользователя:{user}.",
             user=user_id, task_id=task_id)


def get_planned_jobs(db_tasks: list) -> list:
    """Все запланированные задачи."""
    # список id задач пользователя из БД
    tasks_id = [str(task[0]) + str(task[1]) for task in db_tasks]
    # запланированные задачи пользователя
    return [
        (
            job.id[:-1],
            str(job.trigger),
            job.next_run_time.strftime("%d.%m.%Y %H:%M:%S"),
        )
        for job in scheduler.get_jobs()
        if job.id in tasks_id
            ]
