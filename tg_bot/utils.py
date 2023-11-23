"""
В данном модуле написаны инструменты, которыми пользуется Telegram бот.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cardinal import Cardinal

from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
import configparser
import datetime
import os.path
import json
import time

import Utils.cardinal_tools
from tg_bot import CBT


class NotificationTypes:
    """
    Класс с типами Telegram уведомлений.
    """
    bot_start = "1"
    """Уведомление о старте бота."""
    new_message = "2"
    """Уведомление о новом сообщении."""
    command = "3"
    """Уведомление о введенной команде."""
    new_order = "4"
    """Уведомление о новом заказе."""
    order_confirmed = "5"
    """Уведомление о подтверждении заказа."""
    review = "5r"
    """Уведомление об отзыве."""
    lots_restore = "6"
    """Уведомление о восстановлении лота."""
    lots_deactivate = "7"
    """Уведомление о деактивации лота."""
    delivery = "8"
    """Уведомление о выдаче товара."""
    lots_raise = "9"
    """Уведомление о поднятии лотов."""
    other = "10"
    """Прочие уведомления (плагины)."""
    announcement = "11"
    """Новости / объявления."""
    ad = "12"
    """Реклама."""
    critical = "13"
    """Не отключаемые критически важные уведомления."""


def load_authorized_users() -> list[int]:
    """
    Загружает авторизированных пользователей из кэша.

    :return: список из id авторизированных пользователей.
    """
    if not os.path.exists("storage/cache/tg_authorized_users.json"):
        return []
    with open("storage/cache/tg_authorized_users.json", "r", encoding="utf-8") as f:
        data = f.read()
    return json.loads(data)


def load_notification_settings() -> dict:
    """
    Загружает настройки Telegram уведомлений из кэша.

    :return: настройки Telegram уведомлений.
    """
    if not os.path.exists("storage/cache/notifications.json"):
        return {}
    with open("storage/cache/notifications.json", "r", encoding="utf-8") as f:
        return json.loads(f.read())


def load_answer_templates() -> list[str]:
    """
    Загружает шаблоны ответов из кэша.

    :return: шаблоны ответов из кэша.
    """
    if not os.path.exists("storage/cache/answer_templates.json"):
        return []
    with open("storage/cache/answer_templates.json", "r", encoding="utf-8") as f:
        return json.loads(f.read())


def save_authorized_users(users: list[int]) -> None:
    """
    Сохраняет ID авторизированных пользователей.

    :param users: список id авторизированных пользователей.
    """
    if not os.path.exists("storage/cache/"):
        os.makedirs("storage/cache/")
    with open("storage/cache/tg_authorized_users.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(users))


def save_notification_settings(settings: dict) -> None:
    """
    Сохраняет настройки Telegram-уведомлений.

    :param settings: настройки Telegram-уведомлений.
    """
    if not os.path.exists("storage/cache/"):
        os.makedirs("storage/cache/")
    with open("storage/cache/notifications.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(settings))


def save_answer_templates(templates: list[str]) -> None:
    """
    Сохраняет шаблоны ответов.

    :param templates: список шаблонов.
    """
    if not os.path.exists("storage/cache/"):
        os.makedirs("storage/cache")
    with open("storage/cache/answer_templates.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(templates))


def escape(text: str) -> str:
    """
    Форматирует текст под HTML разметку.

    :param text: текст.
    :return: форматированный текст.
    """
    escape_characters = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
    }
    for char in escape_characters:
        text = text.replace(char, escape_characters[char])
    return text


def bool_to_text(value: bool | int | str | None, on: str = "🟢", off: str = "🔴"):
    if value is not None and int(value):
        return on
    return off


def get_offset(element_index: int, max_elements_on_page: int) -> int:
    """
    Возвращает смещение списка элементов таким образом, чтобы элемент с индексом element_index оказался в конце списка.

    :param element_index: индекс элемента, который должен оказаться в конце.
    :param max_elements_on_page: максимальное кол-во элементов на 1 странице.
    """
    elements_amount = element_index + 1
    elements_on_page = elements_amount % max_elements_on_page
    elements_on_page = elements_on_page if elements_on_page else max_elements_on_page
    if not elements_amount - elements_on_page:  # если это первая группа команд:
        return 0
    else:
        return element_index - elements_on_page + 1


def add_navigation_buttons(keyboard_obj: K, curr_offset: int,
                           max_elements_on_page: int,
                           elements_on_page: int, elements_amount: int,
                           callback_text: str,
                           extra: list | None = None) -> K:
    """
    Добавляет к переданной клавиатуре кнопки след. / пред. страница.

    :param keyboard_obj: экземпляр клавиатуры.
    :param curr_offset: текущее смещение списка.
    :param max_elements_on_page: максимальное кол-во кнопок на 1 странице.
    :param elements_on_page: текущее кол-во элементов на странице.
    :param elements_amount: общее кол-во элементов.
    :param callback_text: текст callback'а.
    :param extra: доп. данные (будут перечислены через ":")
    """
    extra = (":" + ":".join(str(i) for i in extra)) if extra else ""
    back, forward = True, True

    if curr_offset > 0:
        back_offset = curr_offset - max_elements_on_page if curr_offset > max_elements_on_page else 0
        back_cb = f"{callback_text}:{back_offset}{extra}"
        first_cb = f"{callback_text}:0{extra}"
    else:
        back, back_cb, first_cb = False, CBT.EMPTY, CBT.EMPTY

    if curr_offset + elements_on_page < elements_amount:
        forward_offset = curr_offset + elements_on_page
        last_page_offset = get_offset(elements_amount - 1, max_elements_on_page)
        forward_cb = f"{callback_text}:{forward_offset}{extra}"
        last_cb = f"{callback_text}:{last_page_offset}{extra}"
    else:
        forward, forward_cb, last_cb = False, CBT.EMPTY, CBT.EMPTY

    if back or forward:
        keyboard_obj.row(B("◀️◀️", callback_data=first_cb), B("◀️", callback_data=back_cb),
                         B("▶️", callback_data=forward_cb), B("▶️▶️", callback_data=last_cb))
    return keyboard_obj


def generate_profile_text(cardinal: Cardinal) -> str:
    """
    Генерирует текст с информацией об аккаунте.

    :return: сгенерированный текст с информацией об аккаунте.
    """
    account = cardinal.account
    balance = cardinal.balance
    return f"""Статистика аккаунта <b><i>{account.username}</i></b>

<b>ID:</b> <code>{account.id}</code>
<b>Незавершенных заказов:</b> <code>{account.active_sales}</code>
<b>Баланс:</b> 
    <b>₽:</b> <code>{balance.total_rub}₽</code>, доступно для вывода <code>{balance.available_rub}₽</code>.
    <b>$:</b> <code>{balance.total_usd}$</code>, доступно для вывода <code>{balance.available_usd}$</code>.
    <b>€:</b> <code>{balance.total_eur}€</code>, доступно для вывода <code>{balance.available_eur}€</code>.

<i>Обновлено:</i>  <code>{time.strftime('%H:%M:%S', time.localtime(account.last_update))}</code>"""


def generate_lot_info_text(lot_obj: configparser.SectionProxy) -> str:
    """
    Генерирует текст с информацией о лоте.

    :param lot_obj: секция лота в конфиге автовыдачи.

    :return: сгенерированный текст с информацией о лоте.
    """
    if lot_obj.get("productsFileName") is None:
        file_path = "<b><u>не привязан.</u></b>"
        products_amount = "<code>∞</code>"
    else:
        file_path = f"<code>storage/products/{lot_obj.get('productsFileName')}</code>"
        if not os.path.exists(f"storage/products/{lot_obj.get('productsFileName')}"):
            with open(f"storage/products/{lot_obj.get('productsFileName')}", "w", encoding="utf-8"):
                pass
        products_amount = Utils.cardinal_tools.count_products(f"storage/products/{lot_obj.get('productsFileName')}")
        products_amount = f"<code>{products_amount}</code>"

    message = f"""<b>{escape(lot_obj.name)}</b>\n
<b><i>Текст выдачи:</i></b> <code>{escape(lot_obj["response"])}</code>\n
<b><i>Кол-во товаров: </i></b> {products_amount}\n
<b><i>Файл с товарами: </i></b>{file_path}\n
<i>Обновлено:</i>  <code>{datetime.datetime.now().strftime('%H:%M:%S')}</code>"""
    return message
