#  mail_server_token заполняется в .env файле
from config import BaseDIR
from pathlib import Path
mail_smpt_host = 'smtp.yandex.ru'
mail_smpt_port = 465
mail_sender_address = 'omzit-report@yandex.ru'

receivers = ('ekimenko.m@gmail.com', )

files = (str(BaseDIR / Path('ownbot.db')), )
