"""Методика расчёта по данных из файла pdf."""
import re

from io import BytesIO

import PyPDF2

from db.db_utils.indicator_db_utils import create_or_update_indicators, get_indicator_file_params_dict


async def get_pdf_file_indicator_dict(user_id: int, file_data: BytesIO) -> dict:
    """Получение показателя из файла pdf."""
    result_dict = {}
    # словарь параметров
    indicator_params_dict = await get_indicator_file_params_dict(user_id=user_id, file_method="pdf")
    # чтение данных
    for indicator, params in indicator_params_dict.items():
        reader = PyPDF2.PdfReader(file_data)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        text = text.replace("\n", "")

        pattern = params["file_read_params"]
        params_id = params["params_id"]
        matches = re.findall(pattern, text)

        # расчёт
        matched_values = [int(match) for match in matches]

        result_dict.update({indicator: {"value": sum(matched_values), "params_id": params_id}})

    return result_dict


async def pdf_indicator_to_db(user_id: int, file_data: BytesIO) -> str:
    """Сохранение показателей в БД из файла pdf."""
    pdf_based = await get_pdf_file_indicator_dict(user_id=user_id, file_data=file_data)
    return await create_or_update_indicators(user_id=user_id, data=pdf_based)
