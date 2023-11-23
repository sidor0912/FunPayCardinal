"""
Проверка на обновления.
"""
from logging import getLogger
from locales.localizer import Localizer
import requests
import os
import zipfile
import shutil
import json


logger = getLogger("FPC.update_checker")
localizer = Localizer()
_ = localizer.translate

HEADERS = {
    "accept": "application/vnd.github+json"
}


class Release:
    """
    Класс, описывающий релиз.
    """
    def __init__(self, name: str, description: str, sources_link: str, exe_link: str):
        """
        :param name: название релиза.
        :param description: описание релиза (список изменений).
        :param sources_link: ссылка на архив с исходниками.
        :param exe_link: ссылка на архив с exe.
        """
        self.name = name
        self.description = description
        self.sources_link = sources_link
        self.exe_link = exe_link


# Получение данных о новом релизе
def get_tags() -> list[str] | None:
    """
    Получает все теги с GitHub репозитория.

    :return: список тегов.
    """
    try:
        response = requests.get("https://api.github.com/repos/sidor0912/FunPayCardinal/tags", headers=HEADERS)
        if not response.status_code == 200:
            logger.debug(f"Update status code is {response.status_code}!")
            return None
        json_response = response.json()
        tags = [i.get("name") for i in json_response]
        return tags or None
    except:
        logger.debug("TRACEBACK", exc_info=True)
        return None


def get_next_tag(tags: list[str], current_tag: str):
    """
    Ищет след. тег после переданного.
    Если не находит текущий тег, возвращает первый.
    Если текущий тег - последний, возвращает None.

    :param tags: список тегов.
    :param current_tag: текущий тег.

    :return: след. тег / первый тег / None
    """
    try:
        curr_index = tags.index(current_tag)
    except ValueError:
        return tags[len(tags)-1]

    if not curr_index:
        return None
    return tags[curr_index-1]


def get_release(tag: str) -> Release | None:
    """
    Получает данные о релизе.

    :param tag: тег релиза.

    :return: данные релиза.
    """
    try:
        response = requests.get(f"https://api.github.com/repos/sidor0912/FunPayCardinal/releases/tags/{tag}",
                                headers=HEADERS)
        if not response.status_code == 200:
            logger.debug(f"Update status code is {response.status_code}!")
            return None
        json_response = response.json()
        name = json_response.get("name")
        description = json_response.get("body")
        sources = json_response.get("zipball_url")
        assets = json_response.get("assets")
        exe = assets[0].get("browser_download_url")
        return Release(name, description, sources, exe)
    except:
        logger.debug("TRACEBACK", exc_info=True)
        return None


def get_new_release(current_tag) -> int | Release:
    """
    Проверяет на наличие обновлений.

    :param current_tag: тег текущей версии.

    :return: объект релиза или код ошибки:
        1 - произошла ошибка при получении списка тегов.
        2 - текущий тег является последним.
        3 - не удалось получить данные о релизе.
    """
    tags = get_tags()
    if tags is None:
        return 1

    next_tag = get_next_tag(tags, current_tag)
    if next_tag is None:
        return 2

    release = get_release(next_tag)
    if release is None:
        return 3
    return release


#  Загрузка нового релиза
def download_zip(url: str) -> int:
    """
    Загружает zip архив с обновлением в файл storage/cache/update.zip.

    :param url: ссылка на zip архив.

    :return: 0, если архив с обновлением загружен, иначе - 1.
    """
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open("storage/cache/update.zip", 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return 0
    except:
        logger.debug("TRACEBACK", exc_info=True)
        return 1


def extract_update_archive() -> str | int:
    """
    Разархивирует скачанный update.zip.

    :return: название папки с обновлением (storage/cache/update/<папка с обновлением>) или 1, если произошла ошибка.
    """
    try:
        if os.path.exists("storage/cache/update/"):
            shutil.rmtree("storage/cache/update/", ignore_errors=True)
        os.makedirs("storage/cache/update")

        with zipfile.ZipFile("storage/cache/update.zip", "r") as zip:
            folder_name = zip.filelist[0].filename
            zip.extractall("storage/cache/update/")
        return folder_name
    except:
        logger.debug("TRACEBACK", exc_info=True)
        return 1


def zipdir(path, zip_obj):
    """
    Рекурсивно архивирует папку.

    :param path: путь до папки.
    :param zip_obj: объект zip архива.
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            zip_obj.write(os.path.join(root, file),
                          os.path.relpath(os.path.join(root, file),
                                          os.path.join(path, '..')))


def create_backup() -> int:
    """
    Создает резервную копию с папками storage и configs.

    :return: 0, если бэкап создан успешно, иначе - 1.
    """
    try:
        with zipfile.ZipFile("backup.zip", "w") as zip:
            zipdir("storage", zip)
            zipdir("configs", zip)
        return 0
    except:
        logger.debug("TRACEBACK", exc_info=True)
        return 1


def install_release(folder_name: str) -> int:
    """
    Устанавливает обновление.

    :param folder_name: название папки со скачанным обновлением в storage/cache/update
    :return: 0, если обновление установлено.
        1 - произошла непредвиденная ошибка.
        2 - папка с обновлением отсутствует.
    """
    try:
        release_folder = os.path.join("storage/cache/update", folder_name)
        if not os.path.exists(release_folder):
            return 2

        if os.path.exists(os.path.join(release_folder, "delete.json")):
            with open(os.path.join(release_folder, "delete.json"), "r", encoding="utf-8") as f:
                data = json.loads(f.read())
                for i in data:
                    if not os.path.exists(i):
                        continue
                    if os.path.isfile(i):
                        os.remove(i)
                    else:
                        shutil.rmtree(i, ignore_errors=True)

        for i in os.listdir(release_folder):
            if i == "delete.json":
                continue

            source = os.path.join(release_folder, i)
            if source.endswith(".exe"):
                if not os.path.exists("update"):
                    os.mkdir("update")
                shutil.copy2(source, os.path.join("update", i))
                continue

            if os.path.isfile(source):
                shutil.copy2(source, i)
            else:
                shutil.copytree(source, os.path.join(".", i), dirs_exist_ok=True)
        return 0
    except:
        logger.debug("TRACEBACK", exc_info=True)
        return 1
