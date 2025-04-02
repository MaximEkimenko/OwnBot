"""Тестовая версия видеонаблюдения с распознаванием лиц с помощью InsightFace."""
# ruff: noqa
import json

import time
import datetime
import subprocess

from io import TextIOWrapper
from pathlib import Path

import cv2
import numpy as np

from insightface.app import FaceAnalysis
from sympy.physics.units.util import quantity_simplify

# trassir servers
server3 = "192.168.9.60"
server4 = "192.168.9.200"
server5 = "192.168.9.59"

# trassir data
user_mame = "SDK"
user_password = "mr78jaeK9l720Yu"
chanel_guid = "jzR1xGgm"
video_stream_port = 25575
rtsp_video_streaming = 554
framerate = 100
server_port = 25571


def check_new_embedings(directory: Path = Path(r"D:\projects\OmzitDetect\fio_pictures")) -> bool:
    """Проверяет наличие новых эмбеддингов в папке с видеофрагментами."""

    embedings_file = Path("embeddings.json")
    if not embedings_file.exists():
        print("No embeddings file.")
        return True

    # файл для хранения количества файлов фото
    sum_file = Path('count_image_files.txt')
    if not sum_file.exists():
        sum_file.write_text(str(0))

    # Подсчитайте файлы с расширениями .png или .jpg
    count_image_files = sum(
        1 for file in directory.rglob("*")
        if file.is_file() and file.suffix.lower() in {".jpg"}
    )
    print(count_image_files)
    # предыдущее количество файлов
    prev_count_image_files = int(sum_file.read_text())

    if int(count_image_files) != int(prev_count_image_files):
        sum_file.write_text(str(count_image_files))
        # удаление старого файла embedings
        embedings_file.unlink()
        print("Pictures files has changed.")
        return True
    print("No new embeddings. Starting recognition service.")
    return False


def load_embeddings(embeddings_file: str = "embeddings.json") -> dict:
    """Загружает предвычисленные эмбеддинги из файла."""
    with open(embeddings_file) as f:
        face_database = json.load(f)

    for name, encoding in face_database.items():
        face_database[name] = np.array(encoding)  # Преобразуем обратно в массив NumPy
    return face_database


def get_stream_url():
    """Получение сслыки на видео-поток из python 3.9 и запись в файл."""
    # Запуск скрипта на Python 3.9
    script_path = r"D:\projects\OmzitDetect\create_stream_request.py"
    py39path = r"D:\projects\OmzitDetect\venv\Scripts\python.exe"
    result = subprocess.run(
        [py39path, script_path],  # Укажите путь к python3.9 и скрипту
        capture_output=True,
        text=True, check=False,
    )

    result = result.stdout.strip()
    file = Path("stream_url.txt").resolve()
    file.write_text(result)
    return file


def show_video_stream(k_limit: float = 1.0, model_name: str = "buffalo_l") -> None:
    """Функция для показа видео-потока с распознаванием лиц."""
    wide_fio_pictures = True
    chanel_pre_dining = "jzR1xGgm"
    chanel_sob = "WvQJrWMU"
    chanel_rod = "lseFtTI8"
    chanel_tuh = "xfNy7Fzu"
    chanel_dining = "XZ1Xs7w0"

    # Инициализация InsightFace
    # antelopev2
    app = FaceAnalysis(name=model_name,
                       providers=['CPUExecutionProvider'])  # Используем CPU (замените на GPU, если доступно)
    # app = FaceAnalysis(name="buffalo_l", providers=["CUDAExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(1280, 1280))

    # чтение ссылки на видео-поток из файла
    file = Path(get_stream_url())
    stream_request = file.read_text()

    # Загружаем предвычисленные эмбеддинги
    face_database = load_embeddings("embeddings.json")
    known_names = []
    known_encodings = []

    for name, encodings in face_database.items():
        for encoding in encodings:
            known_names.append(name)
            known_encodings.append(np.array(encoding))
    known_encodings = np.array(known_encodings)

    # Открываем видеопоток
    cap = cv2.VideoCapture(stream_request)
    quantity_of_good_frames = 0
    recognitions = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Аварийное завершение видеопотока.")
            break

        # Определяем границы области видимости
        height, width = frame.shape[:2]
        x_limit = int(width * k_limit)

        # Рисуем красный прямоугольник для области видимости
        cv2.rectangle(frame, (0, 0), (x_limit, height), (0, 0, 255), 2)

        # Обнаруживаем лица с помощью InsightFace
        faces = app.get(frame)

        for face in faces:
            recognitions += 1
            # Проверяем, находится ли лицо в пределах области видимости
            left, top, right, bottom = map(int, face.bbox)
            if left > x_limit:
                continue  # Пропускаем лица за пределами области

            if face.det_score < 0.9:  # Пропускаем лица с низкой уверенностью
                print("quality frame:", face.det_score)
            pic_width = face.bbox[2] - face.bbox[0]
            pic_height = face.bbox[3] - face.bbox[1]
            if pic_width < 50 or pic_height < 50:  # Минимальный размер лица
                print(f"SMALL FACE SIZE: {(float(pic_width), float(pic_height))}")

            if pic_width < 30 or pic_height < 30:  # Пропуск малых размеров
                print("SKIP small frame.\n")
                continue

            # Получаем эмбеддинг лица
            face_encoding = face.normed_embedding

            # Сравниваем с базой данных
            distances = np.linalg.norm(known_encodings - face_encoding, axis=1)

            best_match_index = np.argmin(distances)
            time_mark = datetime.datetime.now().timestamp()

            name = "Unknown"

            best_match_koef = float(distances[best_match_index])
            if best_match_koef < 1.3:  # Оптимальное пороговое значение
                name = known_names[best_match_index]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                # Сохраняем кадр
                filename = Path(__file__).parent / Path("videocap") / Path(f"{name}_{time_mark}.png")
                if best_match_koef <= 1.21:
                    quantity_of_good_frames += 1
                    print(f"GOOD FRAMES: ({quantity_of_good_frames}, {recognitions}) {best_match_koef=:.2f}")
                    filename = (Path(__file__).parent
                                / Path("videocap")
                                / Path("1_2")
                                / Path(f"{name}_{time_mark}.png"))
                elif best_match_koef <= 1.11:
                    filename = (Path(__file__).parent
                                / Path("videocap")
                                / Path("1_1")
                                / Path(f"{name}_{time_mark}.png"))
                elif best_match_koef <= 0.99:
                    filename = (Path(__file__).parent
                                / Path("videocap")
                                / Path("1")
                                / Path(f"{name}_{time_mark}.png"))
                elif best_match_koef <= 0.6:
                    filename = (Path(__file__).parent
                                / Path("videocap")
                                / Path("best")
                                / Path(f"{name}_{time_mark}.png"))

                # сохранение результата
                cv2.imwrite(str(filename), frame)

            # Рисуем прямоугольник и подпись
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            print(f"RECOGNIZED {name}, ({quantity_of_good_frames}, {recognitions}), {best_match_koef=:.2f}\n")

        # Показываем кадр
        cv2.namedWindow("Video Stream", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Video Stream", 1280, 720)
        cv2.imshow("Video Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    # except Exception as e:
    #     print(f"Произошла ошибка: {e}")


def create_embeddings_from_folders(
        database_path: Path = Path(__file__).parent / Path("fio_pictures"),
        embeddings_file: Path = Path("embeddings.json"),
        model_name: str = "buffalo_l",  # Выбор модели (buffalo_l, buffalo_s и т.д.)
) -> None:
    """Создаёт и сохраняет эмбеддинги лиц из изображений в подпапках указанной папки с использованием InsightFace.
    Каждая подпапка соответствует одному человеку.
    """
    # Проверка существования файла эмбеддингов
    if embeddings_file.exists():
        print(f"Файл {embeddings_file} уже существует.")
        return

    print("New embeddings file will be created...\n")

    # Инициализация InsightFace
    app = FaceAnalysis(name=model_name, providers=["CPUExecutionProvider"])  # Выбор модели
    det_size_small = (320, 320)
    det_size_average = (640, 640)
    app.prepare(ctx_id=0, det_size=det_size_small)

    face_database = {}  # Словарь для хранения эмбеддингов

    # Проход по всем подпапкам (каждая подпапка соответствует одному человеку)
    for person_folder in database_path.iterdir():
        if not person_folder.is_dir():  # Пропускаем файлы, если они не являются папками
            continue

        person_name = person_folder.name
        face_encodings_for_person = []

        # Обрабатываем все изображения в подпапке
        for image_file in person_folder.iterdir():
            if image_file.suffix.lower() in [".jpg", ".jpeg", ".png"]:  # Поддерживаемые форматы
                # Загрузка изображения
                image = cv2.imread(str(image_file))
                if image is None:
                    print(f"Failed to load image: {image_file}")
                    continue

                # Обнаружение лиц
                faces = app.get(image)
                if len(faces) == 0:
                    print(f"Failed to detect faces in image: {image_file}")
                    continue

                # Добавляем первый найденный эмбеддинг
                face_encoding = faces[0].normed_embedding.tolist()  # Преобразуем в список для JSON
                face_encodings_for_person.append(face_encoding)

        # Сохраняем эмбеддинги для текущего человека
        if face_encodings_for_person:
            face_database[person_name] = face_encodings_for_person
        else:
            print(f"For person {person_name} not found any faces.")

    # Сохранение эмбеддингов в JSON-файл
    with embeddings_file.open("w") as json_file:
        json_file: TextIOWrapper
        json.dump(face_database, json_file)
        print(f"Embeddings saved to {embeddings_file}.")


if __name__ == "__main__":
    fio_path = Path(r"D:\projects\OmzitDetect\fio_pictures")
    models = ["buffalo_l", "buffalo_m", "buffalo_s", "antelopev2"]

    if check_new_embedings(directory=fio_path):
        create_embeddings_from_folders(database_path=fio_path, model_name=models[0])

    # TODO сделать перезапуск видеопотока через json обратной связи
    show_video_stream(k_limit=1.0, model_name=models[0])
