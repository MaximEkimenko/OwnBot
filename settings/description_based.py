"""Конфигурационный файл для методики расчёта на основе todoist description."""
# TODO
#  NotImplemented
#  Файл заменён indicators.json
#  Удалить в случае не надобности
# имена показателей

# Показатели на основе заполнения описания в задаче todoist:
# словарь соответствия названия проекта todoist буквы в описании задачи и названия показателя
projects_keys = {
    "Study": {"B": "book", "A": "audiobook", "V": "video"},
    "Wealth": {"M": "add_income", "P": "poms"},
}
# Пример использования:
# В описании к задаче ставится соответствующего проекта литерал и численное значение показателя без пробелов: A30.
# После выполнения задачи показатель будет прочитан.
# Одинаковые показатели в разных задачах по одному и тому же проекту и литералу складываются внутри одной даты.
# То есть если вы закрыли 3 задачи проекта Study с литералом B: B30, B10, B2, то показатель book, за текущий день в
# проекте Study будет равен 22
indicator_params = [
    {
        "indicator_name": "book",
        "project_name": "Study",
        # "label_name": "",
        # "task_name": "",
        "description_literal": "B",

        "calc_as_average": True,
        "project_track_based_method": True,
        "description_based_method": True,
        "quantity_based_method": False,
        "file_based_method": False,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },
    {
        "indicator_name": "audiobook",
        "project_name": "Study",
        # "label_name": "",
        # "task_name": "",
        "description_literal": "A",

        "calc_as_average": True,
        "project_track_based_method": True,
        "description_based_method": True,
        "quantity_based_method": False,
        "file_based_method": False,
        "label_track_based_method": False,
        "task_name_track_based_method": False,

    },
    {
        "indicator_name": "video",
        "project_name": "Study",
        # "label_name": "",
        # "task_name": "",
        "description_literal": "V",

        "calc_as_average": True,
        "project_track_based_method": True,
        "description_based_method": True,
        "quantity_based_method": False,
        "file_based_method": False,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },
    {
        "indicator_name": "steps",
        "project_name": "Health",
        # "label_name": "",
        # "task_name": "",
        # "description_literal": "",

        "calc_as_average": True,
        "project_track_based_method": False,
        "description_based_method": False,
        "quantity_based_method": False,
        "file_based_method": True,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },
    {
        "indicator_name": "kcals",
        "project_name": "Health",
        # "label_name": "",
        # "task_name": "",
        # "description_literal": "",

        "calc_as_average": True,
        "project_track_based_method": False,
        "description_based_method": False,
        "quantity_based_method": False,
        "file_based_method": True,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },
    {
        "indicator_name": "add_income",
        "project_name": "Wealth",
        # "label_name": "",
        # "task_name": "",
        # "description_literal": "",

        "calc_as_average": True,
        "project_track_based_method": False,
        "description_based_method": False,
        "quantity_based_method": False,
        "file_based_method": True,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },
    {
        "indicator_name": "cndx",
        "project_name": "Wealth",
        # "label_name": "",
        # "task_name": "",
        # "description_literal": "",

        "calc_as_average": False,
        "project_track_based_method": False,
        "description_based_method": False,
        "quantity_based_method": False,
        "file_based_method": True,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },
    {
        "indicator_name": "poms",
        "project_name": "Wealth",
        # "label_name": "",
        # "task_name": "",
        "description_literal": "P",

        "calc_as_average": True,
        "project_track_based_method": True,
        "description_based_method": True,
        "quantity_based_method": False,
        "file_based_method": False,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },
    {
        "indicator_name": "study_done",
        "project_name": "Study",
        # "label_name": "",
        # "task_name": "",
        # "description_literal": "P",

        "calc_as_average": True,
        "project_track_based_method": False,
        "description_based_method": False,
        "quantity_based_method": True,
        "file_based_method": False,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },
    {
        "indicator_name": "health_done",
        "project_name": "Health",
        # "label_name": "",
        # "task_name": "",
        # "description_literal": "P",

        "calc_as_average": True,
        "project_track_based_method": False,
        "description_based_method": False,
        "quantity_based_method": True,
        "file_based_method": False,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },
    {
        "indicator_name": "wealth_done",
        "project_name": "Wealth",
        # "label_name": "",
        # "task_name": "",
        # "description_literal": "P",

        "calc_as_average": True,
        "project_track_based_method": False,
        "description_based_method": False,
        "quantity_based_method": True,
        "file_based_method": False,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },
    {
        "indicator_name": "social_done",
        "project_name": "Social",
        # "label_name": "",
        # "task_name": "",
        # "description_literal": "P",

        "calc_as_average": True,
        "project_track_based_method": False,
        "description_based_method": False,
        "quantity_based_method": True,
        "file_based_method": False,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },
    {
        "indicator_name": "studio_done",
        "project_name": "Studio",
        # "label_name": "",
        # "task_name": "",
        # "description_literal": "P",

        "calc_as_average": True,
        "project_track_based_method": False,
        "description_based_method": False,
        "quantity_based_method": True,
        "file_based_method": False,
        "label_track_based_method": False,
        "task_name_track_based_method": False,
    },

]

# json_path = BaseDIR / Path('settings') / 'indicators.json'
# json_data = json.loads(json_path.read_text())
# print(json_data, type(json_data))
