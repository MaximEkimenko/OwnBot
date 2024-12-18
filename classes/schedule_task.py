from typing import Callable
from enums import TaskType


class ScheduleTask:
    def __init__(self, name: str, task_type: TaskType, schedule: str, action: Callable):
        self.name = name
        self.task_type = task_type
        self.schedule = schedule
        self.action = action
