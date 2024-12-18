from datetime import datetime


class TodoistTask:
    def __init__(self, todoist_task: str, project: str, label: str, description: str, done_time: datetime):
        self.todoist_task = todoist_task
        self.project = project
        self.label = label
        self.description = description
        self.done_time = done_time

    def get_data(self, day: datetime):
        # Логика получения данных за день
        pass

    def data_to_db(self):
        # Логика сохранения данных в БД
        pass
