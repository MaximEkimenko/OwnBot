import PyPDF2
import re
from db.db_utils.indicator_db_utils import get_indicator_file_params_dict, create_or_update_indicators
from io import BytesIO


async def get_pdf_file_indicator_dict(user_id: int, file_data: BytesIO) -> tuple:
    """Получение показателя из файла pdf"""
    result_dict = dict()
    # словарь параметров
    indicator_params_dict = await get_indicator_file_params_dict(user_id=user_id, file_method='pdf')
    # чтение данных
    for indicator, params in indicator_params_dict.items():
        print(params)
        reader = PyPDF2.PdfReader(file_data)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        text = text.replace("\n", "")

        pattern = params[0]
        params_id = params[1]
        matches = re.findall(pattern, text)

        # расчёт
        matched_values = []
        for match in matches:
            matched_values.append(int(match))

        result_dict.update({indicator: sum(matched_values)})
        # result_dict[indicator] = sum(matched_values)

    return result_dict, params_id


async def pdf_indicator_to_db(user_id: int, file_data: BytesIO):
    """Сохранение показателей в БД из файла pdf"""
    pdf_based = await get_pdf_file_indicator_dict(user_id=user_id, file_data=file_data)
    await create_or_update_indicators(user_id, data=pdf_based)

