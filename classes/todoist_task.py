from datetime import datetime
# TODO NotImplemented


class TodoistTask:
    """Задача Todoist"""
    def __init__(self, task: str,
                 project: str,
                 labels: str | None,
                 description: str | None,
                 completed_at: datetime,
                 priority: str):
        self.task = task
        self.project = project
        self.labels = labels
        self.description = description
        self.completed_at = completed_at
        self.priority = priority
