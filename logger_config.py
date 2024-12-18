from loguru import logger
import os
from config import BaseDIR

console_format = "<green>{time:HH:mm:ss}</green> | " \
                 "<level>{level: <8}</level> | " \
                 "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - " \
                 "<level>{message}</level>"

LOG_DIR = BaseDIR / "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logger.remove()  # Удаляем стандартный обработчик (иначе будет дублирование)

# Вывод логов в консоль
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="DEBUG",
    colorize=True,
    format=console_format
)

# Вывод логов в JSON-файл с ротацией и сжатием
JSON_LOG_FILE = os.path.join(LOG_DIR, "log.json")

logger.add(
    JSON_LOG_FILE,
    rotation="10 MB",         # Ротация по размеру файла
    compression="zip",        # Сжатие старых логов
    level="DEBUG",            # Уровень логирования
    serialize=True,           # Логи в формате JSON
    enqueue=True,              # Асинхронная запись
)

log = logger

