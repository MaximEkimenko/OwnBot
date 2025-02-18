"""Конфигурационный файл для модуля рассылки по почте.

Mail_server_token заполняется в .env файле.
"""

from pathlib import Path

from config import BaseDIR

# TODO убрать перед push в репозиторий
mail_smpt_host = "smtp.yandex.ru"
mail_smpt_port = 465
mail_sender_address = "omzit-report@yandex.ru"

receivers = ("ekimenko.m@gmail.com", )

files = (str(BaseDIR / Path("ownbot.db")), )
