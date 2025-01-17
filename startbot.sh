#!/bin/bash
# Перемещаемся в директорию с проектом
cd ~/python/ownbot

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем main.py
python main.py

# Деактивируем виртуальное окружение после завершения работы
deactivate