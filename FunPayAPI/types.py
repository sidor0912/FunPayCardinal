"""
В данном модуле описаны все типы пакета FunPayAPI
"""
from __future__ import annotations
from typing import Literal, overload, Optional
from .common.utils import RegularExpressions
from .common.enums import MessageTypes, OrderStatuses, SubCategoryTypes
import datetime


class ChatShortcut:
    """
    Данный класс представляет виджет чата со страницы https://funpay.com/chat/

    :param id_: ID чата.
    :type id_: :obj:`int`

    :param name: название чата (никнейм собеседника).
    :type name: :obj:`str`

    :param last_message_text: текст последнего сообщения в чате (макс. 250 символов).
    :type last_message_text: :obj:`str`

    :param unread: флаг "непрочитанности" (`True`, если чат не прочитан (оранжевый). `False`, если чат прочитан).
    :type unread: :obj:`bool`

    :param html: HTML код виджета чата.
    :type html: :obj:`str`

    :param determine_msg_type: определять ли тип последнего сообщения?
    :type determine_msg_type: :obj:`bool`, опционально
    """
    def __init__(self, id_: int, name: str, last_message_text: str,
                 unread: bool, html: str, determine_msg_type: bool = True):
        self.id: int = id_
        """ID чата."""
        self.name: str | None = name if name else None
        """Название чата (никнейм собеседника)."""
        self.last_message_text: str = last_message_text
        """Текст последнего сообщения в чате (макс. 250 символов)."""
        self.unread: bool = unread
        """Флаг \"непрочитанности\" (если True - в чате есть непрочитанные сообщения)."""
        self.last_message_type: MessageTypes | None = None if not determine_msg_type else self.get_last_message_type()
        """Тип последнего сообщения."""
        self.html: str = html
        """HTML код виджета чата."""

    def get_last_message_type(self) -> MessageTypes:
        """
        Определяет тип последнего сообщения в чате на основе регулярных выражений из MessageTypesRes.

        !Внимание! Результат определения типа сообщения данным методом не является правильным в 100% случаев, т.к. он
        основан на сравнении с регулярными выражениями.
        Возможны "ложные срабатывание", если пользователь напишет "поддельное" сообщение, которое совпадет с одним из
        регулярных выражений.

        :return: тип последнего сообщения.
        :rtype: :class:`FunPayAPI.common.enums.MessageTypes`
        """
        res = RegularExpressions()
        if self.last_message_text == res.DISCORD:
            return MessageTypes.DISCORD

        if res.ORDER_PURCHASED.findall(self.last_message_text) and res.ORDER_PURCHASED2.findall(self.last_message_text):
            return MessageTypes.ORDER_PURCHASED

        if res.ORDER_ID.search(self.last_message_text) is None:
            return MessageTypes.NON_SYSTEM

        # Регулярные выражения выставлены в порядке от самых часто-используемых к самым редко-используемым
        sys_msg_types = {
            MessageTypes.ORDER_CONFIRMED: res.ORDER_CONFIRMED,
            MessageTypes.NEW_FEEDBACK: res.NEW_FEEDBACK,
            MessageTypes.NEW_FEEDBACK_ANSWER: res.NEW_FEEDBACK_ANSWER,
            MessageTypes.FEEDBACK_CHANGED: res.FEEDBACK_CHANGED,
            MessageTypes.FEEDBACK_DELETED: res.FEEDBACK_DELETED,
            MessageTypes.REFUND: res.REFUND,
            MessageTypes.FEEDBACK_ANSWER_CHANGED: res.FEEDBACK_ANSWER_CHANGED,
            MessageTypes.FEEDBACK_ANSWER_DELETED: res.FEEDBACK_ANSWER_DELETED,
            MessageTypes.ORDER_CONFIRMED_BY_ADMIN: res.ORDER_CONFIRMED_BY_ADMIN,
            MessageTypes.PARTIAL_REFUND: res.PARTIAL_REFUND,
            MessageTypes.ORDER_REOPENED: res.ORDER_REOPENED
        }

        for i in sys_msg_types:
            if sys_msg_types[i].search(self.last_message_text):
                return i
        else:
            return MessageTypes.NON_SYSTEM

    def __str__(self):
        return self.last_message_text


class Chat:
    """
    Данный класс представляет личный чат.

    :param id_: ID чата.
    :type id_: :obj:`int`

    :param name: название чата (никнейм собеседника).
    :type name: :obj:`str`

    :param looking_link: ссылка на лот, который смотрит собеседник.
    :type looking_link: :obj:`str` or :obj:`None`

    :param looking_text: название лота, который смотрит собеседник.
    :type looking_text: :obj:`str` or :obj:`None`

    :param html: HTML код чата.
    :type html: :obj:`str`

    :param messages: последние 100 сообщений чата.
    :type messages: :obj:`list` of :class:`FunPayAPI.types.Message` or :obj:`None`
    """
    def __init__(self, id_: int, name: str, looking_link: str | None, looking_text: str | None,
                 html: str, messages: Optional[list[Message]] = None):
        self.id: int = id_
        """ID чата."""
        self.name: str = name
        """Название чата (никнейм собеседника)."""
        self.looking_link: str | None = looking_link
        """Ссылка на лот, который в данный момент смотрит собеседник."""
        self.looking_text: str | None = looking_text
        """Название лота, который в данный момент смотрит собеседник."""
        self.html: str = html
        """HTML код чата."""
        self.messages: list[Message] = messages or []
        """Последние 100 сообщений чата."""


class Message:
    """
    Данный класс представляет отдельное сообщение.

    :param id_: ID сообщения.
    :type id_: :obj:`int`

    :param text: текст сообщения (если есть).
    :type text: :obj:`str` or :obj:`None`

    :param chat_id: ID чата, в котором находится данное сообщение.
    :type chat_id: :obj:`int` or :obj:`str`

    :param chat_name: название чата, в котором находится данное сообщение.
    :type chat_name: :obj:`str` or :obj:`None`

    :param author: никнейм автора сообщения.
    :type author: :obj:`str`, or :obj:`None`

    :param author_id: ID автора сообщения.
    :type author_id: :obj:`int`

    :param html: HTML код сообщения.
    :type html: :obj:`str`

    :param image_link: ссылка на изображение из сообщения (если есть).
    :type image_link: :obj:`str` or :obj:`None`, опционально

    :param determine_msg_type: определять ли тип сообщения.
    :type determine_msg_type: :obj:`bool`, опционально
    """
    def __init__(self, id_: int, text: str | None, chat_id: int | str, chat_name: str | None,
                 author: str | None, author_id: int, html: str,
                 image_link: str | None = None, determine_msg_type: bool = True, badge_text: Optional[str] = None):
        self.id: int = id_
        """ID сообщения."""
        self.text: str | None = text
        """Текст сообщения."""
        self.chat_id: int | str = chat_id
        """ID чата."""
        self.chat_name: str | None = chat_name
        """Название чата."""
        self.type: MessageTypes | None = None if not determine_msg_type else self.get_message_type()
        """Тип сообщения."""
        self.author: str | None = author
        """Автор сообщения."""
        self.author_id: int = author_id
        """ID автора сообщения."""
        self.html: str = html
        """HTML-код сообщения."""
        self.image_link: str | None = image_link
        """Ссылка на изображение в сообщении (если оно есть)."""
        self.by_bot: bool = False
        """Отправлено ли сообщение с помощью :meth:`FunPayAPI.Account.send_message`?"""
        self.badge: str | None = badge_text
        """Текст бэйджика тех. поддержки."""

    def get_message_type(self) -> MessageTypes:
        """
        Определяет тип сообщения на основе регулярных выражений из MessageTypesRes.

        Внимание! Данный способ определения типа сообщения не является 100% правильным, т.к. он основан на сравнении с
        регулярными выражениями. Возможно ложное "срабатывание", если пользователь напишет "поддельное" сообщение,
        которое совпадет с одним из регулярных выражений.
        Рекомендуется делать проверку на author_id == 0.

        :return: тип последнего сообщения в чате.
        :rtype: :class:`FunPayAPI.common.enums.MessageTypes`
        """
        if not self.text:
            return MessageTypes.NON_SYSTEM

        res = RegularExpressions()
        if self.text == res.DISCORD:
            return MessageTypes.DISCORD

        if res.ORDER_PURCHASED.findall(self.text) and res.ORDER_PURCHASED2.findall(self.text):
            return MessageTypes.ORDER_PURCHASED

        if res.ORDER_ID.search(self.text) is None:
            return MessageTypes.NON_SYSTEM

        # Регулярные выражения выставлены в порядке от самых часто-используемых к самым редко-используемым
        sys_msg_types = {
            MessageTypes.ORDER_CONFIRMED: res.ORDER_CONFIRMED,
            MessageTypes.NEW_FEEDBACK: res.NEW_FEEDBACK,
            MessageTypes.NEW_FEEDBACK_ANSWER: res.NEW_FEEDBACK_ANSWER,
            MessageTypes.FEEDBACK_CHANGED: res.FEEDBACK_CHANGED,
            MessageTypes.FEEDBACK_DELETED: res.FEEDBACK_DELETED,
            MessageTypes.REFUND: res.REFUND,
            MessageTypes.FEEDBACK_ANSWER_CHANGED: res.FEEDBACK_ANSWER_CHANGED,
            MessageTypes.FEEDBACK_ANSWER_DELETED: res.FEEDBACK_ANSWER_DELETED,
            MessageTypes.ORDER_CONFIRMED_BY_ADMIN: res.ORDER_CONFIRMED_BY_ADMIN,
            MessageTypes.PARTIAL_REFUND: res.PARTIAL_REFUND,
            MessageTypes.ORDER_REOPENED: res.ORDER_REOPENED
        }

        for i in sys_msg_types:
            if sys_msg_types[i].search(self.text):
                return i
        else:
            return MessageTypes.NON_SYSTEM

    def __str__(self):
        return self.text if self.text is not None else self.image_link if self.image_link is not None else ""


class OrderShortcut:
    """
    Данный класс представляет виджет заказа со страницы https://funpay.com/orders/trade

    :param id_: ID заказа.
    :type id_: :obj:`str`

    :param description: описание заказа.
    :type description: :obj:`str`

    :param price: цена заказа.
    :type price: :obj:`float`

    :param buyer_username: никнейм покупателя.
    :type buyer_username: :obj:`str`

    :param buyer_id: ID покупателя.
    :type buyer_id: :obj:`int`

    :param status: статус заказа.
    :type status: :class:`FunPayAPI.common.enums.OrderStatuses`

    :param date: дата создания заказа.
    :type date: :class:`datetime.datetime`

    :param subcategory_name: название подкатегории, к которой относится заказ.
    :type subcategory_name: :obj:`str`

    :param html: HTML код виджета заказа.
    :type html: :obj:`str`

    :param dont_search_amount: не искать кол-во товара.
    :type dont_search_amount: :obj:`bool`, опционально
    """
    def __init__(self, id_: str, description: str, price: float,
                 buyer_username: str, buyer_id: int, status: OrderStatuses,
                 date: datetime.datetime, subcategory_name: str, html: str, dont_search_amount: bool = False):
        self.id: str = id_ if not id_.startswith("#") else id_[1:]
        """ID заказа."""
        self.description: str = description
        """Описание заказа."""
        self.price: float = price
        """Цена заказа."""
        self.amount: int | None = self.parse_amount() if not dont_search_amount else None
        """Кол-во товаров."""
        self.buyer_username: str = buyer_username
        """Никнейм покупателя."""
        self.buyer_id: int = buyer_id
        """ID покупателя."""
        self.status: OrderStatuses = status
        """Статус заказа."""
        self.date: datetime.datetime = date
        """Дата создания заказа."""
        self.subcategory_name: str = subcategory_name
        """Название подкатегории, к которой относится заказ."""
        self.html: str = html
        """HTML код виджета заказа."""

    def parse_amount(self) -> int:
        """
        Парсит кол-во купленного товара (ищет подстроку по регулярному выражению).

        :return: кол-во купленного товара.
        :rtype: :obj:`int`
        """
        res = RegularExpressions()
        result = res.PRODUCTS_AMOUNT.findall(self.description)
        if result:
            return int(result[0].split(" ")[0])
        return 1

    def __str__(self):
        return self.description


class Order:
    """
    Данный класс представляет заказ со страницы https://funpay.com/orders/<ORDER_ID>/

    :param id_: ID заказа.
    :type id_: :obj:`str`

    :param status: статус заказа.
    :type status: :class:`FunPayAPI.common.enums.OrderStatuses`

    :param subcategory: подкатегория, к которой относится заказ.
    :type subcategory: :class:`FunPayAPI.types.SubCategory`

    :param short_description: краткое описание (название) заказа.
    :type short_description: :obj:`str` or :obj:`None`

    :param full_description: полное описание заказа.
    :type full_description: :obj:`str` or :obj:`None`

    :param sum_: сумма заказа.
    :type sum_: :obj:`float`

    :param buyer_id: ID покупателя.
    :type buyer_id: :obj:`int`

    :param buyer_username: никнейм покупателя.
    :type buyer_username: :obj:`str`

    :param seller_id: ID продавца.
    :type seller_id: :obj:`int`

    :param seller_username: никнейм продавца.
    :type seller_username: :obj:`str`

    :param html: HTML код заказа.
    :type html: :obj:`str`

    :param review: объект отзыва на заказ.
    :type review: :class:`FunPayAPI.types.Review` or :obj:`None`
    """
    def __init__(self, id_: str, status: OrderStatuses, subcategory: SubCategory, short_description: str | None,
                 full_description: str | None, sum_: float,
                 buyer_id: int, buyer_username: str,
                 seller_id: int, seller_username: str,
                 html: str, review: Review | None):
        self.id: str = id_ if not id_.startswith("#") else id_[1:]
        """ID заказа."""
        self.status: OrderStatuses = status
        """Статус заказа."""
        self.subcategory: SubCategory = subcategory
        """Подкатегория, к которой относится заказ."""
        self.short_description: str | None = short_description
        """Краткое описание (название) заказа. То же самое, что и Order.title."""
        self.title: str | None = short_description
        """Краткое описание (название) заказа. То же самое, что и Order.short_description."""
        self.full_description: str | None = full_description
        """Полное описание заказа."""
        self.sum: float = sum_
        """Сумма заказа."""
        self.buyer_id: int = buyer_id
        """ID покупателя."""
        self.buyer_username: str = buyer_username
        """Никнейм покупателя."""
        self.seller_id: int = seller_id
        """ID продавца."""
        self.seller_username: str = seller_username
        """Никнейм продавца."""
        self.html: str = html
        """HTML код заказа."""
        self.review: Review | None = review
        """Объект отзыва заказа."""


class Category:
    """
    Класс, описывающий категорию (игру).

    :param id_: ID категории (game_id / data-id).
    :type id_: :obj:`int`

    :param name: название категории (игры).
    :type name: :obj:`str`

    :param subcategories: подкатегории.
    :type subcategories: :obj:`list` of :class:`FunPayAPI.types.SubCategory` or :obj:`None`, опционально
    """
    def __init__(self, id_: int, name: str, subcategories: list[SubCategory] | None = None):
        self.id: int = id_
        """ID категории (game_id / data-id)."""
        self.name: str = name
        """Название категории (игры)."""
        self.__subcategories: list[SubCategory] = subcategories or []
        """Список подкатегорий."""
        self.__sorted_subcategories: dict[SubCategoryTypes, dict[int, SubCategory]] = {
            SubCategoryTypes.COMMON: {},
            SubCategoryTypes.CURRENCY: {}
        }
        for i in self.__subcategories:
            self.__sorted_subcategories[i.type][i.id] = i

    def add_subcategory(self, subcategory: SubCategory):
        """
        Добавляет подкатегорию в список подкатегорий.

        :param subcategory: объект подкатегории.
        :type subcategory: :class:`FunPayAPI.types.SubCategory`
        """
        if subcategory not in self.__subcategories:
            self.__subcategories.append(subcategory)
            self.__sorted_subcategories[subcategory.type][subcategory.id] = subcategory

    def get_subcategory(self, subcategory_type: SubCategoryTypes, subcategory_id: int) -> SubCategory | None:
        """
        Возвращает объект подкатегории.

        :param subcategory_type: тип подкатегории.
        :type subcategory_type: :class:`FunPayAPI.common.enums.SubCategoryTypes`

        :param subcategory_id: ID подкатегории.
        :type subcategory_id: :obj:`int`

        :return: объект подкатегории или None, если подкатегория не найдена.
        :rtype: :class:`FunPayAPI.types.SubCategory` or :obj:`None`
        """
        return self.__sorted_subcategories[subcategory_type].get(subcategory_id)

    def get_subcategories(self) -> list[SubCategory]:
        """
        Возвращает все подкатегории данной категории (игры).

        :return: все подкатегории данной категории (игры).
        :rtype: :obj:`list` of :class:`FunPayAPI.types.SubCategory`
        """
        return self.__subcategories

    def get_sorted_subcategories(self) -> dict[SubCategoryTypes, dict[int, SubCategory]]:
        """
        Возвращает все подкатегории данной категории (игры) в виде словаря {type: {ID: подкатегория}}.

        :return: все подкатегории данной категории (игры) в виде словаря {type: ID: подкатегория}}.
        :rtype: :obj:`dict` {:class:`FunPayAPI.common.enums.SubCategoryTypes`: :obj:`dict` {:obj:`int`, :class:`FunPayAPI.types.SubCategory`}}
        """
        return self.__sorted_subcategories


class SubCategory:
    """
    Класс, описывающий подкатегорию.

    :param id_: ID подкатегории.
    :type id_: :obj:`int`

    :param name: название подкатегории.
    :type name: :obj:`str`

    :param type_: тип лотов подкатегории.
    :type type_: :class:`FunPayAPI.common.enums.SubCategoryTypes`

    :param category: родительская категория (игра).
    :type category: :class:`FunPayAPI.types.Category`
    """
    def __init__(self, id_: int, name: str, type_: SubCategoryTypes, category: Category):
        self.id: int = id_
        """ID подкатегории."""
        self.name: str = name
        """Название подкатегории."""
        self.type: SubCategoryTypes = type_
        """Тип подкатегории."""
        self.category: Category = category
        """Родительская категория (игра)."""
        self.fullname: str = f"{self.name} {self.category.name}"
        """Полное название подкатегории."""
        self.public_link: str = f"https://funpay.com/chips/{id_}/" if type_ is SubCategoryTypes.CURRENCY else \
            f"https://funpay.com/lots/{id_}/"
        """Публичная ссылка на список лотов подкатегории."""
        self.private_link: str = f"{self.public_link}trade"
        """Приватная ссылка на список лотов подкатегории (для редактирования лотов)."""


class LotFields:
    """
    Класс, описывающий поля лота со страницы редактирования лота.

    :param lot_id: ID лота.
    :type lot_id: :obj:`int`

    :param fields: словарь с полями.
    :type fields: :obj:`dict`
    """
    def __init__(self, lot_id: int, fields: dict):
        self.lot_id: int = lot_id
        """ID лота."""
        self.__fields: dict = fields
        """Поля лота."""

        self.title_ru: str = self.__fields.get("fields[summary][ru]")
        """Русское краткое описание (название) лота."""
        self.title_en: str = self.__fields.get("fields[summary][en]")
        """Английское краткое описание (название) лота."""
        self.description_ru: str = self.__fields.get("fields[desc][ru]")
        """Русское полное описание лота."""
        self.description_en: str = self.__fields.get("fields[desc][en]")
        """Английское полное описание лота."""
        self.amount: int | None = int(i) if (i := self.__fields.get("amount")) else None
        """Кол-во товара."""
        self.price: float = float(i) if (i := self.__fields.get("price")) else None
        """Цена за 1шт."""
        self.active: bool = "active" in self.__fields
        """Активен ли лот."""
        self.deactivate_after_sale: bool = "deactivate_after_sale[]" in self.__fields
        """Деактивировать ли лот после продажи."""

    @property
    def fields(self) -> dict[str, str]:
        """
        Возвращает все поля лота в виде словаря.

        :return: все поля лота в виде словаря.
        :rtype: :obj:`dict` {:obj:`str`: :obj:`str`}
        """
        return self.__fields

    def edit_fields(self, fields: dict[str, str]):
        """
        Редактирует переданные поля лота.

        :param fields: поля лота, которые нужно заменить, и их значения.
        :type fields: obj:`dict` {:obj:`str`: :obj:`str`}
        """
        self.__fields.update(fields)

    def set_fields(self, fields: dict):
        """
        Сбрасывает текущие поля лота и устанавливает переданные.
        !НЕ РЕДАКТИРУЕТ СВОЙСТВА ЭКЗЕМЛПЯРА!

        :param fields: поля лота.
        :type fields: :obj:`dict` {:obj:`str`: :obj:`str`}
        """
        self.__fields = fields

    def renew_fields(self) -> LotFields:
        """
        Обновляет :py:obj:`~__fields` (возвращается в методе :meth:`FunPayAPI.types.LotFields.get_fields`),
        основываясь на свойствах экземпляра.
        Необходимо вызвать перед сохранением лота на FunPay после изменения любого свойства экземпляра.

        :return: экземпляр класса :class:`FunPayAPI.types.LotFields` с новыми полями лота.
        :rtype: :class:`FunPayAPI.types.LotFields`
        """
        self.__fields["fields[summary][ru]"] = self.title_ru
        self.__fields["fields[summary][en]"] = self.title_en
        self.__fields["fields[desc][ru]"] = self.description_ru
        self.__fields["fields[desc][en]"] = self.description_en
        self.__fields["price"] = str(self.price) if self.price is not None else ""
        self.__fields["deactivate_after_sale"] = "on" if self.deactivate_after_sale else ""
        self.__fields["active"] = "on" if self.active else ""
        self.__fields["amount"] = self.amount if self.amount is not None else ""
        return self


class LotShortcut:
    """
    Данный класс представляет виджет лота.

    :param id_: ID лота.
    :type id_: :obj:`int` or :obj:`str`

    :param server: название сервера (если указан в лоте).
    :type server: :obj:`str` or :obj:`None`

    :param description: краткое описание (название) лота.
    :type description: :obj:`str` or :obj:`None`

    :param price: цена лота.
    :type price: :obj:`float`

    :param subcategory: подкатегория лота.
    :type subcategory: :class:`FunPayAPI.types.SubCategory`

    :param html: HTML код виджета лота.
    :type html: :obj:`str`
    """
    def __init__(self, id_: int | str, server: str | None,
                 description: str | None, price: float, subcategory: SubCategory, html: str):
        self.id: int | str = id_
        if isinstance(self.id, str) and self.id.isnumeric():
            self.id = int(self.id)
        """ID лота."""
        self.server: str | None = server
        """Название сервера (если указан)."""
        self.description: str | None = description
        """Краткое описание (название) лота."""
        self.title: str | None = description
        """Краткое описание (название) лота."""
        self.price: float = price
        """Цена лота."""
        self.subcategory: SubCategory = subcategory
        """Подкатегория лота."""
        self.html: str = html
        """HTML-код виджета лота."""
        self.public_link: str = f"https://funpay.com/chips/offer?id={self.id}" \
            if self.subcategory.type is SubCategoryTypes.CURRENCY else f"https://funpay.com/lots/offer?id={self.id}"
        """Публичная ссылка на лот."""


class UserProfile:
    """
    Данный класс представляет пользователя FunPay.

    :param id_: ID пользователя.
    :type id_: :obj:`int`

    :param username: никнейм пользователя.
    :type username: :obj:`str`

    :param profile_photo: ссылка на фото профиля.
    :type profile_photo: :obj:`str`

    :param online: онлайн ли пользователь?
    :type online: :obj:`bool`

    :param banned: заблокирован ли пользователь?
    :type banned: :obj:`bool`

    :param html: HTML код страницы пользователя.
    :type html: :obj:`str`
    """
    def __init__(self, id_: int, username: str, profile_photo: str, online: bool, banned: bool, html: str):
        self.id: int = id_
        """ID пользователя."""
        self.username: str = username
        """Никнейм пользователя."""
        self.profile_photo: str = profile_photo
        """Ссылка на фото профиля."""
        self.online: bool = online
        """Онлайн ли пользователь."""
        self.banned: bool = banned
        """Заблокирован ли пользователь."""
        self.html: str = html
        """HTML код страницы пользователя."""
        self.__lots: list[LotShortcut] = []
        """Все лоты пользователя."""
        self.__lots_ids: dict[int | str, LotShortcut] = {}
        """Все лоты пользователя в виде словаря {ID: лот}}"""
        self.__sorted_by_subcategory_lots: dict[SubCategory, dict[int | str, LotShortcut]] = {}
        """Все лоты пользователя в виде словаря {подкатегория: {ID: лот}}"""
        self.__sorted_by_subcategory_type_lots: dict[SubCategoryTypes, dict[int | str, LotShortcut]] = {
            SubCategoryTypes.COMMON: {},
            SubCategoryTypes.CURRENCY: {}
        }

    def get_lot(self, lot_id: int | str) -> LotShortcut | None:
        """
        Возвращает объект лота со страницы пользователя.

        :param lot_id: ID лота.
        :type lot_id: :obj:`int` or :obj:`str`

        :return: объект лота со страницы пользователя или `None`, если объект не найден.
        :rtype: :class:`FunPayAPI.types.LotShortcut` or :obj:`None`
        """
        if isinstance(lot_id, str) and lot_id.isnumeric():
            return self.__lots_ids.get(int(lot_id))
        return self.__lots_ids.get(lot_id)

    def get_lots(self) -> list[LotShortcut]:
        """
        Возвращает список всех лотов пользователя.

        :return: список всех лотов пользователя.
        :rtype: :obj:`list` of :class:`FunPayAPI.types.LotShortcut`
        """
        return self.__lots

    @overload
    def get_sorted_lots(self, mode: Literal[1]) -> dict[int | str, LotShortcut]:
        ...

    @overload
    def get_sorted_lots(self, mode: Literal[2]) -> dict[SubCategory, dict[int | str, LotShortcut]]:
        ...

    @overload
    def get_sorted_lots(self, mode: Literal[3]) -> dict[SubCategoryTypes, dict[int | str, LotShortcut]]:
        ...

    def get_sorted_lots(self, mode: Literal[1, 2, 3]) -> dict[int | str, LotShortcut] |\
                                                         dict[SubCategory, dict[int | str, LotShortcut]] |\
                                                         dict[SubCategoryTypes, dict[int | str, LotShortcut]]:
        """
        Возвращает список всех лотов пользователя в виде словаря.

        :param mode: вариант словаря.\n
            1 - {ID: лот}\n
            2 - {подкатегория: {ID: лот}}\n
            3 - {тип лота: {ID: лот}}

        :return: список всех лотов пользователя в виде словаря.
        :rtype: :obj:`dict` {:obj:`int` or :obj:`str`: :class:`FunPayAPI.types.LotShortcut`} (`mode==1`) \n
            :obj:`dict` {:class:`FunPayAPI.types.SubCategory`: :obj:`dict` {:obj:`int` or :obj:`str`: :class:`FunPayAPI.types.LotShortcut`}} (`mode==2`) \n
            :obj:`dict` {:class:`FunPayAPI.common.enums.SubCategoryTypes`: :obj:`dict` {:obj:`int` or :obj:`str`: :class:`FunPayAPI.types.LotShortcut`}} (`mode==3`)
        """
        if mode == 1:
            return self.__lots_ids
        elif mode == 2:
            return self.__sorted_by_subcategory_lots
        else:
            return self.__sorted_by_subcategory_type_lots

    def add_lot(self, lot: LotShortcut):
        """
        Добавляет лот в список лотов.

        :param lot: объект лота.
        """
        if lot in self.__lots:
            return

        self.__lots.append(lot)
        self.__lots_ids[lot.id] = lot
        if lot.subcategory not in self.__sorted_by_subcategory_lots:
            self.__sorted_by_subcategory_lots[lot.subcategory] = {}
        self.__sorted_by_subcategory_lots[lot.subcategory][lot.id] = lot
        self.__sorted_by_subcategory_type_lots[lot.subcategory.type][lot.id] = lot

    def get_common_lots(self) -> list[LotShortcut]:
        """
        Возвращает список стандартных лотов со страницы пользователя.

        :return: Список стандартных лотов со страницы пользователя.
        :rtype: :obj:`list` of :class:`FunPayAPI.types.LotShortcut`
        """
        return list(self.__sorted_by_subcategory_type_lots[SubCategoryTypes.COMMON].values())

    def get_currency_lots(self) -> list[LotShortcut]:
        """
        Возвращает список лотов-валют со страницы пользователя.

        :return: список лотов-валют со страницы пользователя.
        :rtype: :obj:`list` of :class:`FunPayAPI.types.LotShortcut`
        """
        return list(self.__sorted_by_subcategory_type_lots[SubCategoryTypes.CURRENCY].values())

    def __str__(self):
        return self.username


class Review:
    """
    Данный класс представляет отзыв на заказ.

    :param stars: кол-во звезд в отзыве.
    :type stars: :obj:`int` or :obj:`None`

    :param text: текст отзыва.
    :type text: :obj:`str` or :obj:`None`

    :param reply: текст ответа на отзыв.
    :type reply: :obj:`str` or :obj:`None`

    :param anonymous: анонимный ли отзыв?
    :type anonymous: :obj:`bool`

    :param html: HTML код отзыва.
    :type html: :obj:`str`

    :param order_id: ID заказа, к которому относится отзыв.
    :type order_id: :obj:`str` or :obj:`None`, опционально

    :param author: автор отзыва.
    :type author: :obj:`str` or :obj:`None`, опционально

    :param author_id: ID автора отзыва.
    :type author_id: :obj:`int` or :obj:`None`, опционально
    """
    def __init__(self, stars: int | None, text: str | None, reply: str | None, anonymous: bool, html: str,
                 order_id: str | None = None, author: str | None = None, author_id: int | None = None):
        self.stars: int | None = stars
        """Кол-во звезде в отзыве."""
        self.text: str | None = text
        """Текст отзыва."""
        self.reply: str | None = reply
        """Текст ответа на отзыв."""
        self.anonymous: bool = anonymous
        """Анонимный ли отзыв?"""
        self.html: str = html
        """HTML код отзыва."""
        self.order_id: str | None = order_id[1:] if order_id and order_id.startswith("#") else order_id
        """ID заказа, к которому относится отзыв."""
        self.author: str | None = author
        """Автор отзыва."""
        self.author_id: int | None = author_id
        """ID автора отзыва."""


class Balance:
    """
    Данный класс представляет информацию о балансе аккаунта.

    :param total_rub: общий рублёвый баланс.
    :type total_rub: :obj:`float`

    :param available_rub: доступный к выводу рублёвый баланс.
    :type available_rub: :obj:`float`

    :param total_usd: общий долларовый баланс.
    :type total_usd: :obj:`float`

    :param available_usd: доступный к выводу долларовый баланс.
    :type available_usd: :obj:`float`

    :param total_eur: общий евро баланс.
    :param available_eur: :obj:`float`
    """
    def __init__(self, total_rub: float, available_rub: float, total_usd: float, available_usd: float,
                 total_eur: float, available_eur: float):
        self.total_rub: float = total_rub
        """Общий рублёвый баланс."""
        self.available_rub: float = available_rub
        """Доступный к выводу рублёвый баланс."""
        self.total_usd: float = total_usd
        """Общий долларовый баланс."""
        self.available_usd: float = available_usd
        """Доступный к выводу долларовый баланс."""
        self.total_eur: float = total_eur
        """Общий евро баланс."""
        self.available_eur: float = available_eur
        """Доступный к выводу евро баланс."""
