"""Подсчёт строк кода в .py файлах в корневой директории"""
import os

from pathlib import Path
from collections.abc import Iterable

exclude_dirs = ("venv", "misc",  "migration")


def strings_count(directory: Path) -> Iterable[tuple]:
    for root, dirs, files in os.walk(directory):
        for ban in exclude_dirs:
            if ban in dirs:
                dirs.remove(ban)
        for file in files:
            count = 0
            if os.path.join(root, file).endswith(".py"):
                curr_file = open(os.path.join(root, file), encoding="utf-8")
                for line in curr_file.readlines():
                    if not (line == "\n" or line.strip().startswith(('"', "#", "'"))):
                        count += 1
                path = Path.joinpath(Path(root), Path(file))
                yield path, count


BASE_DIR: Path = Path(__file__).parent
total = 0
result = []
for element in strings_count(directory=BASE_DIR):
    total += element[1]
    result.append(f'Файл "{Path(element[0].relative_to(BASE_DIR.parent))}": строк кода - {element[1]}')

result_string = "\n".join(result)
print("\n".join(result))
print(total)

with open("statistics.txt", "w", encoding="utf-8") as _file:
    _file.write(result_string)
    _file.write(f"\nВсего: файлов: {len(result)}, строк: {total}.")
