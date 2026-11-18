"""
В данном модуле написаны инструменты, которыми пользуется Telegram бот.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cardinal import Cardinal

from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
import configparser
import datetime
import os.path
import json
import time
import unicodedata
import Utils.cardinal_tools
from locales.localizer import Localizer
from tg_bot import CBT

localizer = Localizer()
_ = localizer.translate


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
    """Не отключаемые критически важные уведомления (только авторизованные юзеры и чаты)."""
    important_announcement = "14"
    """Не отключаемые новости/объявления (все возможные чаты)."""


def load_authorized_users() -> dict[int, dict[str, bool | None | str]]:
    """
    Загружает авторизированных пользователей из кэша.

    :return: список из id авторизированных пользователей.
    """
    if not os.path.exists("storage/cache/tg_authorized_users.json"):
        return dict()
    with open("storage/cache/tg_authorized_users.json", "r", encoding="utf-8") as f:
        data = f.read()
    data = json.loads(data)
    result = {}
    if isinstance(data, list):
        for i in data:
            result[i] = {}
        save_authorized_users(result)
    else:
        for k, v in data.items():
            result[int(k)] = v
    return result


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


def save_authorized_users(users: dict[int, dict]) -> None:
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


def format_message_line(cardinal: Cardinal, msg, last: dict | None = None, *, force_show_author: bool = False,
                        chat_url: bool = False, mono: bool = True, hide_watermark: bool = False,
                        show_ads: bool = True, show_image_name: bool | None = None,
                        system_message_style: str = "code") -> str:
    """
    Форматирует ОДНО сообщение чата (значок по роли автора + тело) в HTML для Telegram.

    Общая логика для всех мест, где нужно показать сообщение чата в тг (уведомления о новых
    сообщениях, полная/недавняя история чата, синхронизация с форумом) - не дублируй её, зови
    эту функцию (или format_messages() для готового списка сообщений).

    :param cardinal: экземпляр Cardinal (нужен account.id, blacklist, show_image_name).
    :param msg: сообщение чата (FunPayAPI.types.Message).
    :param last: {"author_id", "by_bot", "badge", "by_vertex"} предыдущего ПОКАЗАННОГО сообщения -
        нужен, чтобы схлопнуть подпись автора у подряд идущих сообщений одного и того же автора.
        None/{} - подпись показать (нет предыдущего сообщения). Обнови этот словарь вызовом
        {"author_id": msg.author_id, "by_bot": msg.by_bot, "badge": msg.badge,
        "by_vertex": msg.by_vertex} после каждого НЕпустого результата, если форматируешь
        сообщения по одному в своём цикле (format_messages() делает это сама).
    :param force_show_author: не схлопывать подпись, даже если она совпадает с last - используй
        для первого сообщения после того, как ты сама сбросила накопленный текст (например,
        отправила его отдельным Telegram-сообщением), чтобы новое сообщение не начиналось без
        подписи автора.
    :param chat_url: оборачивать ник автора ссылкой на чат на FunPay.
    :param mono: оборачивать текст обычных сообщений в <code> (моноширинный шрифт).
    :param hide_watermark: прятать вотермарку бота (Other.watermark в _main.cfg) под спойлером в
        собственных сообщениях, отправленных ботом.
    :param show_ads: показывать рекламные сообщения (📣) или молча пропускать их
        (возвращается пустая строка, last обновлять не нужно).
    :param show_image_name: показывать ли имя файла у отправленных изображений вместо "photo".
        None - взять из cardinal.show_image_name (глобальная настройка).
    :param system_message_style: "code" - тело системных сообщений FunPay (author_id == 0) в
        <code>, как у обычных сообщений; "bold_italic" - <b><i>...</i></b> без <code>.

    :return: строка "{author}{body}" (без завершающих переносов), либо пустая строка, если
        сообщение нужно молча пропустить (см. show_ads).
    """
    account = cardinal.account
    last = last or {}

    is_ad = msg.author_id == 500 and msg.interlocutor_id != 500
    if is_ad and not show_ads:
        return ""

    author_text = msg.author
    if chat_url:
        author_text = f"<a href='https://funpay.com/chat/?node={msg.chat_id}'>{msg.author}</a>"

    if not force_show_author and msg.author_id == last.get("author_id") and msg.by_bot == last.get("by_bot") \
            and msg.badge == last.get("badge") and msg.by_vertex == last.get("by_vertex"):
        author = ""
    elif msg.author_id == account.id:
        if msg.is_autoreply:
            author = f"<i><b>📦 {_('you')} ({msg.badge}):</b></i> "
        elif msg.by_bot:
            author = f"<i><b>🤖 FPC:</b></i> "
        else:
            author = f"<i><b>🫵 {_('you')}:</b></i> "

    elif msg.author_id == 0:
        author = f"<i><b>🔵 {author_text}: </b></i>"
    elif msg.is_employee:
        author = f"<i><b>📣 {author_text} ({msg.badge}): </b></i>" if is_ad \
            else f"<i><b>🆘 {author_text} ({msg.badge}): </b></i>"
    elif msg.author == msg.chat_name:
        author = f"<i><b>👤 {author_text}: </b></i>"
        if msg.is_autoreply:
            author = f"<i><b>🛍️ {author_text} ({msg.badge}):</b></i> "
        elif msg.author in cardinal.blacklist:
            author = f"<i><b>🚷 {author_text}: </b></i>"
        elif msg.by_bot:
            author = f"<i><b>🐦 {author_text}: </b></i>"
        elif msg.by_vertex:
            author = f"<i><b>🐺 {author_text}: </b></i>"
    else:
        author = f"<i><b>🆘 {author_text} ({_('support')}): </b></i>"

    if msg.text:
        if msg.author_id == 0 and system_message_style == "bold_italic":
            body = f"<b><i>{escape(msg.text)}</i></b>"
        else:
            text = msg.text
            hidden_wm = False
            if hide_watermark and msg.author_id == account.id and msg.by_bot:
                watermark = cardinal.MAIN_CFG["Other"].get("watermark", "")
                if watermark and text.startswith(f"{watermark}\n"):
                    text = text.replace(watermark, "", 1)
                    hidden_wm = True
            body = escape(text)
            if mono:
                body = f"<code>{body}</code>"
            if hidden_wm:
                body = f"<tg-spoiler>🐦</tg-spoiler>{body}"
    elif msg.image_link:
        is_own_bot_image = msg.author_id == account.id and msg.by_bot
        show_name = cardinal.show_image_name if show_image_name is None else show_image_name
        name = show_name and not is_own_bot_image and msg.image_name
        body = f"<a href=\"{msg.image_link}\">{name or _('photo')}</a>"
    else:
        body = ""

    return f"{author}{body}"


def format_messages(cardinal: Cardinal, messages: list, **options) -> str:
    """
    Форматирует список сообщений чата в HTML для Telegram, вызывая format_message_line() для
    каждого сообщения по очереди и склеивая результат (см. её докстринг за подробностями и
    списком поддерживаемых опций - force_show_author/chat_url/mono/hide_watermark/show_ads/
    show_image_name/system_message_style).

    :param cardinal: экземпляр Cardinal (нужен account.id, blacklist, show_image_name).
    :param messages: список сообщений чата (FunPayAPI.types.Message), от старых к новым.

    :return: HTML-форматированный текст (используй с parse_mode="HTML").
    """
    lines = []
    last: dict = {}
    for msg in messages:
        line = format_message_line(cardinal, msg, last, **options)
        if not line:
            continue
        lines.append(line)
        last = {"author_id": msg.author_id, "by_bot": msg.by_bot, "badge": msg.badge, "by_vertex": msg.by_vertex}
    return "\n\n".join(lines)


def has_brand_mark(watermark: str) -> bool:
    """
    Проверяет, содержит ли watermark какую-нибудь форму названия
    """
    simplified = (unicodedata.normalize("NFKD", watermark)
                  .encode("ascii", "ignore").decode("ascii").lower())
    ascii_hits = any(kw in simplified for kw in ("cardinal", "fpc"))
    raw_hits = any(kw in watermark.lower() for kw in ("кардинал", "🐦", "ᴄᴀʀᴅɪɴᴀʟ"))

    return ascii_hits or raw_hits or "ᑕᗩᖇᗪIᑎᗩᒪ" in watermark


def split_by_limit(list_of_str: list[str], limit: int = 4096):
    result = []
    current = ""

    for part in list_of_str:
        if len(current) + len(part) > limit:
            result.append(current)
            current = part
        else:
            current += part

    if current:
        result.append(current)

    return result


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
        center_text = f"{(curr_offset // max_elements_on_page) + 1}/{math.ceil(elements_amount / max_elements_on_page)}"
        keyboard_obj.row(B("◀️◀️", callback_data=first_cb), B("◀️", callback_data=back_cb),
                         B(center_text, callback_data=CBT.EMPTY),
                         B("▶️", callback_data=forward_cb), B("▶️▶️", callback_data=last_cb))
    return keyboard_obj


def generate_profile_text(cardinal: Cardinal) -> str:
    """
    Генерирует текст с информацией об аккаунте.

    :return: сгенерированный текст с информацией об аккаунте.
    """
    account = cardinal.account  # locale
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
        file_path = "<b><u>не привязан.</u></b>"  # locale
        products_amount = "<code>∞</code>"
    else:
        file_path = f"<code>storage/products/{lot_obj.get('productsFileName')}</code>"
        if not os.path.exists(f"storage/products/{lot_obj.get('productsFileName')}"):
            with open(f"storage/products/{lot_obj.get('productsFileName')}", "w", encoding="utf-8"):
                pass
        products_amount = Utils.cardinal_tools.count_products(f"storage/products/{lot_obj.get('productsFileName')}")
        products_amount = f"<code>{products_amount}</code>"
    # locale
    message = f"""<b>{escape(lot_obj.name)}</b>\n
<b><i>Текст выдачи:</i></b> <code>{escape(lot_obj["response"])}</code>\n
<b><i>Кол-во товаров: </i></b> {products_amount}\n
<b><i>Файл с товарами: </i></b>{file_path}\n
<i>Обновлено:</i>  <code>{datetime.datetime.now().strftime('%H:%M:%S')}</code>"""
    return message
