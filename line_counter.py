"""Подсчёт строк кода в .py файлах в корневой директории."""
import os

from pathlib import Path
from collections.abc import Iterable


def strings_count(directory: Path) -> Iterable[tuple]:
    """Подсчёт строк в директории."""
    exclude_dirs = ("venv", "misc", "migration")
    for root, dirs, files in os.walk(directory):
        for ban in exclude_dirs:
            if ban in dirs:
                dirs.remove(ban)
        for file in files:
            count = 0
            full_path = Path(root) / file
            if str(full_path).endswith(".py"):
                with Path.open(full_path, encoding="utf-8") as current_file:
                    for line in current_file.readlines():
                        if not (line == "\n" or line.strip().startswith(('"', "#", "'"))):
                            count += 1
                path = Path.joinpath(Path(root), Path(file))
                yield path, count


def create_statistics_file() -> str:
    """Создание файла статистики по строкам кода."""
    base_dir: Path = Path(__file__).parent
    total = 0
    result = []
    for element in strings_count(directory=base_dir):
        total += element[1]
        result.append(f'Файл "{Path(element[0].relative_to(base_dir.parent))}": строк кода - {element[1]}')

    result_string = "\n".join(result)
    result_string += f"\n Всего строк кода: {total}"
    statistics_file = Path("statistics.txt")
    with Path.open(statistics_file, "w", encoding="utf-8") as _file:
        _file.write(result_string)
        _file.write(f"\nВсего: файлов: {len(result)}, строк: {total}.")

    return result_string


if __name__ == "__main__":
    create_statistics_file()
