from datetime import datetime


class TodoistTask:
    def __init__(self, task: str, project: str, labels: str | None, description: str | None,
                 completed_at: datetime, priority: str):
        self.task = task
        self.project = project
        self.labels = labels
        self.description = description
        self.completed_at = completed_at
        self.priority = priority

    def get_data(self, day: datetime):
        # Логика получения данных за день
        pass

    def data_to_db(self):
        # Логика сохранения данных в БД
        pass
