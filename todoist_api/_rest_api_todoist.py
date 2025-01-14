# TODO пример получения данных по todoist api другим способом
#  удалить если нет надобности
# api = TodoistAPI(token)  # объект TODOISTa
# projects = api.get_projects()

# tasks = []
# for index, project in enumerate(projects):
#     response = api.get_completed_items(project_id=project.id, limit=10)
#     for api_task in response.items:
#         task = {
#             'task': api_task.content,
#             'project': project.name,
#             'project_id': api_task.project_id,
#             'user_id': api_task.user_id,
#             'labels': api_task.labels,
#             'description': api_task.description,
#             'completed_at': api_task.completed_at,
#             'added_at': api_task.added_at,
#             'id': api_task.id,
#             'priority': api_task.priority,
#             'due': api_task.due
#         }
#         tasks.append(task.copy())
#     if not response.has_more:
#         break
# #
# # pprint(tasks)
# for task in tasks:
#     project = task['project']
#     task_content = task['task']
#     done_date = parse(task['completed_at'])
#     print(project, task_content, done_date)
#
# return tasks