# ruff: noqa
import json
import subprocess
import time

from pathlib import Path

import psutil


def run_subprocess(script_path: Path) -> None:
    """Запускает python скрипт script_path в его виртуальном окружении."""
    venv_path = Path(__file__).parent / Path(".venv")
    # Запускаем команду через shell
    subprocess.run(
        f"call {venv_path}\\Scripts\\activate.bat && python {script_path}",
        shell=True,
        check=True,
    )


def process_run_check(process_name: str = "python.exe",
                      target_file: Path = None,
                      process_bat_path: Path = None,
                      json_file_name: Path = Path("PID.json")) -> list:
    """Функция перезапускает процесс с именем process_name.

    Процесс запускается через bat файл process_bat_path или python скрипт target_file
    в случае если его PID нет в
    файле обратной связи json_file_name, который создает запускаемый процесс
    """
    if not target_file and not process_bat_path:
        raise ValueError("target_file or process_bat_path must be specified!")
    with json_file_name.open("r") as file:  # чтение файла обратной связи
        feedback_dict = json.load(file)
    is_running = False
    pid_list = []
    for process in psutil.process_iter():
        pid_list.append((process.pid, process.name()))
        if process.pid == feedback_dict["PID"] and feedback_dict["process_name"] == process_name:
            print(f"process {target_file} is running!")
            is_running = True
            break
    if not is_running:
        # os.startfile(process_bat_path)  # запуск bat файла
        run_subprocess(Path(target_file))  # запуск python скрипта
        print(f"\nPROCESS {target_file} restarted!\n")
    return pid_list


if __name__ == "__main__":
    _target_file = Path(__file__).parent / Path("insight_face_tst.py")
    while True:
        try:
            process_run_check(target_file=_target_file)
        except Exception as e:
            print(e)
        time.sleep(10)
