"""Модуль перезапуска процесса по PID."""
# TODO после тестов перенести в Detect project с отдельным venv python 3.12.8
import json
import time
import subprocess

from pathlib import Path

import psutil

from logger_config import log


def run_subprocess(script_path: Path) -> None:
    """Запускает python скрипт script_path в его виртуальном окружении."""
    venv_path = Path(__file__).parent / Path(".venv")
    subprocess.run([f"{venv_path}\\Scripts\\python.exe", script_path], check=True)


def process_run_check(process_name: str = "python.exe",
                      target_file: Path | None = None,
                      process_bat_path: Path | None = None,
                      json_file_name: Path = Path("PID.json")) -> list:
    """Функция перезапускает процесс с именем process_name.

    Процесс запускается через bat файл process_bat_path или python скрипт target_file
    в случае если его PID нет в
    файле обратной связи json_file_name, который создает запускаемый процесс
    """
    if not target_file and not process_bat_path:
        msg = "target_file or process_bat_path must be specified!"
        raise ValueError(msg)
    with json_file_name.open("r") as file:  # чтение файла обратной связи
        feedback_dict = json.load(file)
    is_running = False
    pid_list = []
    for process in psutil.process_iter():
        pid_list.append((process.pid, process.name()))
        if process.pid == feedback_dict["pid"] and feedback_dict["process_name"] == process_name:
            log.info("process {target_file} is running!", target_file=target_file)
            is_running = True
            break
    if not is_running:
        # os.startfile(process_bat_path)  # запуск bat файла
        # log.info("\Bat file {process_bat_path} used to start process!\n", process_bat_path=process_bat_path)
        run_subprocess(Path(target_file))  # запуск python скрипта
        log.info("\nPROCESS {target_file} restarted!\n", target_file=target_file)
    return pid_list


if __name__ == "__main__":
    _target_file = Path(__file__).parent / Path("insight_face_tst.py")
    while True:
        try:
            process_run_check(target_file=_target_file)
        except Exception as e:
            log.error("Error while running process.")
            log.exception(e)
        time.sleep(10)
