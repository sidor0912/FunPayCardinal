from __future__ import annotations
from typing import TYPE_CHECKING

import bcrypt
import requests

from locales.localizer import Localizer

if TYPE_CHECKING:
    from cardinal import Cardinal

import FunPayAPI.types

from datetime import datetime
import Utils.exceptions
import itertools
import psutil
import json
import sys
import os
import re
import time
import logging

PHOTO_RE = re.compile(r'\$photo=[\d]+')
ENTITY_RE = re.compile(r"\$photo=\d+|\$new|(\$sleep=(\d+\.\d+|\d+))")
logger = logging.getLogger("FPC.cardinal_tools")
localizer = Localizer()
_ = localizer.translate


def count_products(path: str) -> int:
    """
    Считает кол-во товара в указанном файле.

    :param path: путь до файла с товарами.

    :return: кол-во товара в указанном файле.
    """
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        products = f.read()
    products = products.split("\n")
    products = list(itertools.filterfalse(lambda el: not el, products))
    return len(products)


def cache_blacklist(blacklist: list[str]) -> None:
    """
    Кэширует черный список.

    :param blacklist: черный список.
    """
    if not os.path.exists("storage/cache"):
        os.makedirs("storage/cache")

    with open("storage/cache/blacklist.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(blacklist, indent=4))


def load_blacklist() -> list[str]:
    """
    Загружает черный список.

    :return: черный список.
    """
    if not os.path.exists("storage/cache/blacklist.json"):
        return []

    with open("storage/cache/blacklist.json", "r", encoding="utf-8") as f:
        blacklist = f.read()

        try:
            blacklist = json.loads(blacklist)
        except json.decoder.JSONDecodeError:
            return []
        return blacklist


def check_proxy(proxy: dict) -> bool:
    """
    Проверяет работоспособность прокси.

    :param proxy: словарь с данными прокси.

    :return: True, если прокси работает, иначе - False.
    """
    logger.info(_("crd_checking_proxy"))
    try:
        response = requests.get("https://api.ipify.org/", proxies=proxy, timeout=10)
    except:
        logger.error(_("crd_proxy_err"))
        logger.debug("TRACEBACK", exc_info=True)
        return False
    logger.info(_("crd_proxy_success", response.content.decode()))
    return True


def validate_proxy(proxy: str):
    """
    Проверяет прокси на соответствие формату IPv4 и выбрасывает исключение или возвращает логин, пароль, IP и порт.

    :param proxy: прокси
    :return: логин, пароль, IP и порт
    """
    try:
        if "@" in proxy:
            login_password, ip_port = proxy.split("@")
            login, password = login_password.split(":")
            ip, port = ip_port.split(":")
        else:
            login, password = "", ""
            ip, port = proxy.split(":")
        if not all([0 <= int(i) < 256 for i in ip.split(".")]) or ip.count(".") != 3 \
                or not ip.replace(".", "").isdigit() or not 0 <= int(port) <= 65535:
            raise Exception()
    except:
        raise ValueError("Прокси должны иметь формат login:password@ip:port или ip:port")  # locale
    return login, password, ip, port


def cache_proxy_dict(proxy_dict: dict[int, str]) -> None:
    """
    Кэширует список прокси.

    :param proxy_dict: список прокси.
    """
    if not os.path.exists("storage/cache"):
        os.makedirs("storage/cache")

    with open("storage/cache/proxy_dict.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(proxy_dict, indent=4))


def load_proxy_dict() -> dict[int, str]:
    """
    Загружает список прокси.

    :return: список прокси.
    """
    if not os.path.exists("storage/cache/proxy_dict.json"):
        return {}

    with open("storage/cache/proxy_dict.json", "r", encoding="utf-8") as f:
        proxy = f.read()

        try:
            proxy = json.loads(proxy)
            proxy = {int(k): v for k, v in proxy.items()}
        except json.decoder.JSONDecodeError:
            return {}
        return proxy


def cache_disabled_plugins(disabled_plugins: list[str]) -> None:
    """
    Кэширует UUID отключенных плагинов.

    :param disabled_plugins: список UUID отключенных плагинов.
    """
    if not os.path.exists("storage/cache"):
        os.makedirs("storage/cache")

    with open("storage/cache/disabled_plugins.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(disabled_plugins))


def load_disabled_plugins() -> list[str]:
    """
    Загружает список UUID отключенных плагинов из кэша.

    :return: список UUID отключенных плагинов.
    """
    if not os.path.exists("storage/cache/disabled_plugins.json"):
        return []

    with open("storage/cache/disabled_plugins.json", "r", encoding="utf-8") as f:
        try:
            return json.loads(f.read())
        except json.decoder.JSONDecodeError:
            return []


def cache_old_users(old_users: dict[int, float]):
    """
    Сохраняет в кэш список пользователей, которые уже писали на аккаунт.
    """
    if not os.path.exists("storage/cache"):
        os.makedirs("storage/cache")
    with open(f"storage/cache/old_users.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(old_users, ensure_ascii=False))


def load_old_users(greetings_cooldown: float) -> dict[int, float]:
    """
    Загружает из кэша список пользователей, которые уже писали на аккаунт.

    :return: список ID чатов.
    """
    if not os.path.exists(f"storage/cache/old_users.json"):
        return dict()
    with open(f"storage/cache/old_users.json", "r", encoding="utf-8") as f:
        users = f.read()
    try:
        users = json.loads(users)
    except json.decoder.JSONDecodeError:
        return dict()
    # todo убрать позже, конвертация для старых версий кардинала
    if type(users) == list:
        users = {user: time.time() for user in users}
    else:
        users = {int(user): time_ for user, time_ in users.items() if
                 time.time() - time_ < greetings_cooldown * 24 * 60 * 60}
    cache_old_users(users)
    return users


def create_greeting_text(cardinal: Cardinal):
    """
    Генерирует приветствие для вывода в консоль после загрузки данных о пользователе.
    """
    account = cardinal.account
    balance = cardinal.balance
    current_time = datetime.now()
    if current_time.hour < 4:
        greetings = "Какая прекрасная ночь"  # locale
    elif current_time.hour < 12:
        greetings = "Доброе утро"
    elif current_time.hour < 17:
        greetings = "Добрый день"
    else:
        greetings = "Добрый вечер"

    lines = [
        f"* {greetings}, $CYAN{account.username}.",
        f"* Ваш ID: $YELLOW{account.id}.",
        f"* Ваш текущий баланс: $CYAN{balance.total_rub} RUB $RESET| $MAGENTA{balance.total_usd} USD $RESET| $YELLOW{balance.total_eur} EUR",
        f"* Текущие незавершенные сделки: $YELLOW{account.active_sales}.",
        f"* Удачной торговли!"
    ]

    length = 60
    greetings_text = f"\n{'-' * length}\n"
    for line in lines:
        greetings_text += line + " " * (length - len(
            line.replace("$CYAN", "").replace("$YELLOW", "").replace("$MAGENTA", "").replace("$RESET",
                                                                                             "")) - 1) + "$RESET*\n"
    greetings_text += f"{'-' * length}\n"
    return greetings_text


def time_to_str(time_: int):
    """
    Конвертирует число в строку формата "Хд Хч Хмин Хсек"

    :param time_: число для конвертации.

    :return: строку-время.
    """
    days = time_ // 86400
    hours = (time_ - days * 86400) // 3600
    minutes = (time_ - days * 86400 - hours * 3600) // 60
    seconds = time_ - days * 86400 - hours * 3600 - minutes * 60

    if not any([days, hours, minutes, seconds]):  # locale
        return "0 сек"
    time_str = ""
    if days:
        time_str += f"{days}д"
    if hours:
        time_str += f" {hours}ч"
    if minutes:
        time_str += f" {minutes}мин"
    if seconds:
        time_str += f" {seconds}сек"
    return time_str.strip()


def get_month_name(month_number: int) -> str:
    """
    Возвращает название месяца в родительном падеже.

    :param month_number: номер месяца.

    :return: название месяца в родительном падеже.
    """
    months = [
        "Января", "Февраля", "Марта",
        "Апреля", "Мая", "Июня",
        "Июля", "Августа", "Сентября",
        "Октября", "Ноября", "Декабря"
    ]  # todo локализация
    if month_number > len(months):
        return months[0]
    return months[month_number - 1]


def get_products(path: str, amount: int = 1) -> list[list[str] | int] | None:
    """
    Берет из товарного файла товар/-ы, удаляет их из товарного файла.

    :param path: путь до файла с товарами.
    :param amount: кол-во товара.

    :return: [[Товар/-ы], оставшееся кол-во товара]
    """
    with open(path, "r", encoding="utf-8") as f:
        products = f.read()

    products = products.split("\n")

    # Убираем пустые элементы
    products = list(itertools.filterfalse(lambda el: not el, products))

    if not products:
        raise Utils.exceptions.NoProductsError(path)

    elif len(products) < amount:
        raise Utils.exceptions.NotEnoughProductsError(path, len(products), amount)

    got_products = products[:amount]
    save_products = products[amount:]
    amount = len(save_products)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(save_products))

    return [got_products, amount]


def add_products(path: str, products: list[str], at_zero_position=False):
    """
    Добавляет товары в файл с товарами.

    :param path: путь до файла с товарами.
    :param products: товары.
    :param at_zero_position: добавить товары в начало товарного файла.
    """
    if not at_zero_position:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(products))
    else:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(products) + "\n" + text)


def safe_text(text: str):
    return "⁣".join(text)


def format_msg_text(text: str, obj: FunPayAPI.types.Message | FunPayAPI.types.ChatShortcut) -> str:
    """
    Форматирует текст, подставляя значения переменных, доступных для MessageEvent.

    :param text: текст для форматирования.
    :param obj: экземпляр types.Message или types.ChatShortcut.

    :return: форматированый текст.
    """
    date_obj = datetime.now()
    month_name = get_month_name(date_obj.month)
    date = date_obj.strftime("%d.%m.%Y")
    str_date = f"{date_obj.day} {month_name}"
    str_full_date = str_date + f" {date_obj.year} года"  # locale

    time_ = date_obj.strftime("%H:%M")
    time_full = date_obj.strftime("%H:%M:%S")

    username = obj.author if isinstance(obj, FunPayAPI.types.Message) else obj.name
    chat_name = obj.chat_name if isinstance(obj, FunPayAPI.types.Message) else obj.name
    chat_id = str(obj.chat_id) if isinstance(obj, FunPayAPI.types.Message) else str(obj.id)

    variables = {
        "$full_date_text": str_full_date,
        "$date_text": str_date,
        "$date": date,
        "$time": time_,
        "$full_time": time_full,
        "$username": safe_text(username),
        "$message_text": str(obj),
        "$chat_id": chat_id,
        "$chat_name": safe_text(chat_name)
    }

    for var in variables:
        text = text.replace(var, variables[var])
    return text


def format_order_text(text: str, order: FunPayAPI.types.OrderShortcut | FunPayAPI.types.Order) -> str:
    """
    Форматирует текст, подставляя значения переменных, доступных для Order.

    :param text: текст для форматирования.
    :param order: экземпляр Order.

    :return: форматированый текст.
    """
    date_obj = datetime.now()
    month_name = get_month_name(date_obj.month)
    date = date_obj.strftime("%d.%m.%Y")
    str_date = f"{date_obj.day} {month_name}"
    str_full_date = str_date + f" {date_obj.year} года"  # locale
    time_ = date_obj.strftime("%H:%M")
    time_full = date_obj.strftime("%H:%M:%S")
    game = subcategory_fullname = subcategory = ""
    try:
        if isinstance(order, FunPayAPI.types.OrderShortcut) and not order.subcategory:
            game, subcategory = order.subcategory_name.rsplit(", ", 1)
            subcategory_fullname = f"{subcategory} {game}"
        else:
            subcategory_fullname = order.subcategory.fullname
            game = order.subcategory.category.name
            subcategory = order.subcategory.name
    except:
        logger.warning("Произошла ошибка при парсинге игры из заказа")  # locale
        logger.debug("TRACEBACK", exc_info=True)
    description = order.description if isinstance(order,
                                                  FunPayAPI.types.OrderShortcut) else order.short_description if order.short_description else ""
    params = order.params if isinstance(order, FunPayAPI.types.Order) and order.params else ""
    variables = {
        "$full_date_text": str_full_date,
        "$date_text": str_date,
        "$date": date,
        "$time": time_,
        "$full_time": time_full,
        "$username": safe_text(order.buyer_username),
        "$order_desc_and_params": f"{description}, {params}" if description and params else f"{description}{params}",
        "$order_desc_or_params": description if description else params,
        "$order_desc": description,
        "$order_title": description,
        "$order_params": params,
        "$order_id": order.id,
        "$order_link": f"https://funpay.com/orders/{order.id}/",
        "$category_fullname": subcategory_fullname,
        "$category": subcategory,
        "$game": game
    }

    for var in variables:
        text = text.replace(var, variables[var])
    return text


def restart_program():
    """
    Полный перезапуск FPC.
    """
    python = sys.executable
    os.execl(python, python, *sys.argv)
    try:
        process = psutil.Process()
        for handler in process.open_files():
            os.close(handler.fd)
        for handler in process.connections():
            os.close(handler.fd)
    except:
        pass


def shut_down():
    """
    Полное отключение FPC.
    """
    try:
        process = psutil.Process()
        process.terminate()
    except:
        pass


def set_console_title(title: str) -> None:
    """
    Изменяет название консоли для Windows.
    """
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(title)
    except:
        logger.warning("Произошла ошибка при изменении названия консоли")
        logger.debug("TRACEBACK", exc_info=True)


# Хеширование пароля
def hash_password(password: str) -> str:
    # Генерация соли и хеширование пароля
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()  # Возвращаем хеш как строку


# Проверка пароля
def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())  # Кодируем для проверки
