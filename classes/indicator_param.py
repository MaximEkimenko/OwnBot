class IndicatorParam:
    """Параметры расчёта показателя"""
    def __init__(self, indicator_name: str,
                 project_name: str,
                 label_track_name: str = None,
                 label_calc_name: str = None,
                 track_by_name: bool = False,
                 track_by_project: bool = False,
                 calc_as_average: bool = False):
        self.indicator_name = indicator_name
        self.project_name = project_name
        self.label_track_name = label_track_name
        self.label_calc_name = label_calc_name
        self.track_by_name = track_by_name
        self.track_by_project = track_by_project
        self.calc_as_average = calc_as_average



