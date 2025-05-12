"""Тестовая версия видеонаблюдения с распознаванием лиц с помощью InsightFace."""
# TODO после тестов перенести в Detect project с отдельным venv python 3.12.8
import os
import json
import time
import datetime
import subprocess

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from io import TextIOWrapper
from pathlib import Path

import cv2
import numpy as np
import psutil

from insightface.app import FaceAnalysis

from logger_config import log

LOCAL_TZ = datetime.timezone(datetime.timedelta(hours=-time.timezone / 3600))


def feedback_json_create(json_pid_file_path: Path = Path("PID.json")) -> str:
    """Функция создает json файл обратной связи json_file_path c pid, PPID и именем процесса."""
    pid = os.getpid()  # id процесса
    parent_pid = os.getppid()  # id для родительского процесса
    feedback_list = {"datetime": str(datetime.datetime.now(tz=LOCAL_TZ)), "pid": pid, "parent_pid": parent_pid,
                     "process_name": psutil.Process(pid).name()}
    try:
        with json_pid_file_path.open("w") as jsonfile:
            jsonfile.write(json.dumps(feedback_list))
            result = "Feedback json created successfully.\n"
        log.debug("Feedback json updated...")
    except Exception as e:
        log.error("Error while creating feedback json")
        log.exception(e)
        result = f"error while creating feedback json: {e}"
    return result


def check_new_embedings(directory: Path = Path(r"D:\projects\OmzitDetect\fio_pictures")) -> bool:
    """Проверяет наличие новых эмбеддингов в папке с видеофрагментами."""
    embedings_file = Path("embeddings.json")
    if not embedings_file.exists():
        log.warning("No embeddings file.")
        return True

    # файл для хранения количества файлов фото
    sum_file = Path("count_image_files.txt")
    if not sum_file.exists():
        sum_file.write_text(str(0))

    # Подсчитайте файлы с расширениями .png или .jpg
    count_image_files = sum(
        1 for file in directory.rglob("*")
        if file.is_file() and file.suffix.lower() in {".jpg"}
    )
    # предыдущее количество файлов
    prev_count_image_files = int(sum_file.read_text())

    if int(count_image_files) != int(prev_count_image_files):
        sum_file.write_text(str(count_image_files))
        # удаление старого файла embedings
        embedings_file.unlink()
        log.warning("Pictures files has changed.")
        return True
    log.debug("No new embeddings. Starting recognition service. \n")
    return False


def load_embeddings(embeddings_file: Path = Path("embeddings.json")) -> dict:
    """Загружает предвычисленные эмбеддинги из файла."""
    with embeddings_file.open("r") as f:
        face_database = json.load(f)

    for name, encoding in face_database.items():
        face_database[name] = np.array(encoding)  # Преобразуем обратно в массив NumPy
    return face_database


def get_stream_url() -> Path:
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


def show_video_stream(model_name: str = "buffalo_l") -> None:
    """Функция для показа видео-потока с распознаванием лиц."""
    # Инициализация InsightFace
    app = FaceAnalysis(name=model_name,
                       providers=["CPUExecutionProvider"])  # Используем CPU (замените на GPU, если доступно)
    # app = FaceAnalysis(name="buffalo_l", providers=["CUDAExecutionProvider"])
    # det_size_small = (320, 320)
    # det_size_average = (640, 640)
    app.prepare(ctx_id=0, det_size=(1280, 1280))

    # чтение ссылки на видео-поток из файла
    file = Path(get_stream_url())
    stream_request = file.read_text()

    # Загружаем предвычисленные эмбеддинги
    face_database = load_embeddings(Path("embeddings.json"))
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
            log.warning("Аварийное завершение видеопотока.")
            break

        # InsightFace
        faces = app.get(frame)

        for face in faces:
            recognitions += 1
            # Проверяем, находится ли лицо в пределах области видимости
            left, top, right, bottom = map(int, face.bbox)
            log.debug("quality frame: {qa}", qa=face.det_score)

            if face.bbox[2] - face.bbox[0] < 30 or face.bbox[3] - face.bbox[1] < 30:  # Пропуск малых размеров
                log.debug("SKIP small frame.\n")
                continue

            # Получаем эмбеддинг лица
            face_encoding = face.normed_embedding

            # Сравниваем с базой данных
            distances = np.linalg.norm(known_encodings - face_encoding, axis=1)

            best_match_index = np.argmin(distances)
            time_mark = datetime.datetime.now(tz=LOCAL_TZ).timestamp()

            name = "Unknown"

            best_match_koef = float(distances[best_match_index])

            if best_match_koef < 1.26:
                name = known_names[best_match_index]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Определяем путь для сохранения в зависимости от коэффициента совпадения
                base_path = Path(__file__).parent / "videocap"
                match best_match_koef:
                    case koef if koef <= 0.6:
                        save_path = base_path / "best"
                        quantity_of_good_frames += 1
                        log.success("BEST FRAMES: ({quantity_of_good_frames}, {recognitions}) {best_match_koef}",
                                    quantity_of_good_frames=quantity_of_good_frames,
                                    recognitions=recognitions,
                                    best_match_koef=best_match_koef)
                    case koef if koef <= 0.99:
                        save_path = base_path / "1"
                        quantity_of_good_frames += 1
                        log.success("1 FRAMES: ({quantity_of_good_frames}, {recognitions}) {best_match_koef}",
                                    quantity_of_good_frames=quantity_of_good_frames,
                                    recognitions=recognitions,
                                    best_match_koef=best_match_koef)
                    case koef if koef <= 1.11:
                        save_path = base_path / "1_1"
                        quantity_of_good_frames += 1
                        log.success("1_1 FRAMES: ({quantity_of_good_frames}, {recognitions}) {best_match_koef}",
                                    quantity_of_good_frames=quantity_of_good_frames,
                                    recognitions=recognitions,
                                    best_match_koef=best_match_koef)
                    case koef if koef <= 1.21:
                        save_path = base_path / "1_2"
                        quantity_of_good_frames += 1
                        log.debug("1_2 FRAMES: ({quantity_of_good_frames}, {recognitions}) {best_match_koef}",
                                  quantity_of_good_frames=quantity_of_good_frames,
                                  recognitions=recognitions,
                                  best_match_koef=best_match_koef)
                    case _:
                        save_path = base_path

                # Сохраняем кадр
                filename = save_path / f"{name}_{time_mark}.png"

                # сохранение результата
                cv2.imwrite(str(filename), frame)

            # Рисуем прямоугольник и подпись
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            log.debug("RECOGNIZED {name}, ({quantity_of_good_frames}, {recognitions}), {best_match_koef}\n",
                      name=name, quantity_of_good_frames=quantity_of_good_frames, recognitions=recognitions,
                      best_match_koef=best_match_koef)

        # Показываем кадр
        cv2.namedWindow("Video Stream", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Video Stream", 1280, 720)
        cv2.imshow("Video Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


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
        log.info("Файл {embeddings_file} уже существует.", embeddings_file=embeddings_file)
        return

    log.debug("New embeddings file will be created...\n")

    # Инициализация InsightFace
    app = FaceAnalysis(name=model_name, providers=["CPUExecutionProvider"])  # Выбор модели
    det_size_small = (320, 320)
    # det_size_average = (640, 640)
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
                    log.warning("Failed to load image: {image_file}", image_file=image_file)
                    continue

                # Обнаружение лиц
                faces = app.get(image)
                if len(faces) == 0:
                    log.warning("Failed to detect faces in image: {image_file}", imaget_file=image_file)
                    continue

                # Добавляем первый найденный эмбеддинг
                face_encoding = faces[0].normed_embedding.tolist()  # Преобразуем в список для JSON
                face_encodings_for_person.append(face_encoding)

        # Сохраняем эмбеддинги для текущего человека
        if face_encodings_for_person:
            face_database[person_name] = face_encodings_for_person
        else:
            log.warning("For person {person_name} not found any faces.", person_name=person_name)

    # Сохранение эмбеддингов в JSON-файл
    with embeddings_file.open("w") as json_file:
        json_file: TextIOWrapper
        json.dump(face_database, json_file)
        log.debug("Embeddings saved to {embeddings_file}.", embeddings_file=embeddings_file)


if __name__ == "__main__":
    fio_path = Path(r"D:\projects\OmzitDetect\fio_pictures")
    models = ["buffalo_l", "buffalo_m", "buffalo_s", "antelopev2"]

    if check_new_embedings(directory=fio_path):
        create_embeddings_from_folders(database_path=fio_path, model_name=models[0])

    # создание файла обратной связи
    feedback_json_create()

    # TODO сделать перезапуск видеопотока через json обратной связи
    show_video_stream(model_name=models[0])
