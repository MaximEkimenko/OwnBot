import io
import datetime

import pygal

from pygal.style import Style

from settings.report_config import date_label_freq, preferred_order, preferred_colors
from db.db_utils.report_db_utils import get_all_indicators_report_data
from utils.report_utils.report_css import full_report_css


async def create_full_html_report(user_id: int,
                                  start: datetime.date | None = None,
                                  end: datetime.date | None = None,
                                  ) -> io.BytesIO:
    """Построение отчётов"""
    indicator_data = await get_all_indicators_report_data(user_id=user_id, start=start, end=end)
    # сортировка по предпочтениям из файла report_config.py
    if preferred_order:
        indicator_data = dict(sorted(indicator_data.items(),
                                     key=lambda x:
                                     preferred_order.index(x[0]) if x[0] in preferred_order else len(preferred_order)))
    # формирование отчёта
    charts_list = []
    for indicator, value_dict in indicator_data.items():
        calc_as_average = value_dict.pop("calc_as_average")
        dates = sorted(value_dict.keys())
        sums = 0
        graph_data = []
        absolute_values = [entry["indicator_value"] for entry in value_dict.values()]
        if calc_as_average:
            for i, current_date in enumerate(dates, start=1):
                sums += value_dict[current_date]["indicator_value"]
                graph_data.append(sums / i)
        else:
            graph_data = absolute_values

        # текущее значение показателя
        current_indicator_value = graph_data[-1]
        # текущее абсолютное значение
        current_absolute_value = absolute_values[-1]

        custom_style = Style(
            colors=(preferred_colors.get(indicator, "black"),),
            stroke_width=3,
            value_font_size=10,
            major_label_font_size=10,
            label_font_size=10,
            dots_size=0,
        )

        timeline_chart = pygal.Line(x_label_rotation=90,
                                    show_minor_x_labels=False,
                                    style=custom_style,
                                    show_dots=False,
                                    )
        timeline_chart.title = (f'{indicator.upper()}: {start.strftime("%d.%m.%Y")}-{end.strftime("%d.%m.%Y")} '
                                f'(average value: {current_indicator_value:.2f}, '
                                f'absolute: {current_absolute_value:.2f})'
                                )
        timeline_chart.x_labels = [d.strftime("%d.%m.%y") for d in dates]

        # Добавляем данные
        timeline_chart.add("", graph_data)
        timeline_chart.x_labels_major = [dates[i].strftime("%d.%m.%y") for i in
                                         range(0, len(dates), max(1, len(dates) // date_label_freq))]
        timeline_chart.show_minor_y_labels = True
        charts_list.append(timeline_chart.render(is_unicode=True))

    # формирование результата
    buffer = io.BytesIO()
    html_content = "<html><head>"
    html_content += full_report_css
    html_content += "</head><body>"
    html_content += '<div class="charts-container">'
    for chart in charts_list:
        html_content += f'<div class="chart">{chart}</div>'
    html_content += "</div></body></html>"

    # отправка результата потоком
    buffer.write(html_content.encode("utf-8"))
    buffer.seek(0)

    return buffer
