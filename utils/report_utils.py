import asyncio

import pygal
from db.db_utils.report_db_utils import get_all_indicators_report_data
from pygal.style import Style

async def create_html_report():
    """Построение отчётов"""
    all_data = await get_all_indicators_report_data(user_id=1)


    # # Извлекаем данные для построения графика
    # TODO график без средних
    # dates = list(data['video'].keys())
    # values = [entry['indicator_value'] for entry in data['video'].values()]
    #
    # # Создаем график
    # timeline_chart = pygal.Line(x_label_rotation=45, show_minor_x_labels=False)
    # timeline_chart.title = 'Indicator Values Over Time'
    # timeline_chart.x_labels = [d.strftime('%Y-%m-%d') for d in dates]
    # timeline_chart.add('Video', values)
    #
    # # Сохраняем график в файл и открываем его
    # timeline_chart.render_to_file('video_chart.svg')
    # print("График сохранён как video_chart.svg")

    charts_list = []
    # print(all_data)
    for indicator, value_dict in all_data.items():
        # print(value_dict)
        # Извлекаем данные для построения графика
        dates = sorted(value_dict.keys())
        sums = 0
        averages = []

        for i, current_date in enumerate(dates, start=1):
            sums += value_dict[current_date]['indicator_value']
            averages.append(sums / i)

        # Последнее значение для заголовка
        last_value = averages[-1]

        # Создаём кастомную тему
        custom_style = Style(
            colors=('green',),  # Основной цвет линии и пороговой линии
            stroke_width=2,                # Толщина линии
            value_font_size=10,            # Размер шрифта для значений
            major_label_font_size=10,      # Размер шрифта для главных меток
            label_font_size=10,            # Размер шрифта для остальных меток
            dots_size=4                    # Размер точек
        )
        #

        # Создаем график с использованием кастомной темы
        timeline_chart = pygal.Line(x_label_rotation=90, show_minor_x_labels=False, style=custom_style)
        timeline_chart.title = f'Average {indicator} value over time (current: {last_value:.2f})'
        timeline_chart.x_labels = [d.strftime('%d.%m.%y') for d in dates]

        # Добавляем данные
        timeline_chart.add(f'{indicator}', averages)


        # Пример меток и надписей на графике
        timeline_chart.x_labels_major = [dates[i].strftime('%d.%m.%y') for i in range(0, len(dates), max(1, len(dates)//10))]
        timeline_chart.show_minor_y_labels = True
        # timeline_chart.show_minor_x_labels = False

        # Сохраняем график в файл и открываем его
        # timeline_chart.render_to_file('video_chart.svg')
        charts_list.append(timeline_chart)

        # import pygal
        # from pygal.style import Style
        #
        # # Создаем первый график
        # chart1 = pygal.Line(style=custom_style)
        # chart1.title = 'First Chart'
        # chart1.add('Series 1', [1, 3, 5, 7])
        #
        # # Создаем второй график
        # chart2 = pygal.Bar(style=custom_style)
        # chart2.title = 'Second Chart'
        # chart2.add('Series 2', [2, 4, 6, 8])
        #
        # # Объединяем графики в один HTML
        with open('combined_charts.html', 'w') as f:
            for chart in charts_list:
                f.write(chart.render(is_unicode=True))
                f.write('<br>')
                # f.write(chart2.render(is_unicode=True))


if __name__ == "__main__":
    asyncio.run(create_html_report())

    # report_name='regular'
    # create_full_diagram_report(report_name='regular', indicator_name='cndx')

