from __future__ import annotations
from enum import Enum


class EventTypes(Enum):
    """
    В данном классе перечислены все типы событий FunPayAPI.
    """
    INITIAL_CHAT = 0
    """Обнаружен чат (при первом запросе Runner'а)."""

    CHATS_LIST_CHANGED = 1
    """Список чатов и/или последнее сообщение одного/нескольких чатов изменилось."""

    LAST_CHAT_MESSAGE_CHANGED = 2
    """В чате изменилось последнее сообщение."""

    NEW_MESSAGE = 3
    """Обнаружено новое сообщение в истории чата."""

    INITIAL_ORDER = 4
    """Обнаружен заказ (при первом запросе Runner'а)."""

    ORDERS_LIST_CHANGED = 5
    """Список заказов и/или статус одного/нескольких заказов изменился."""

    NEW_ORDER = 6
    """Новый заказ."""

    ORDER_STATUS_CHANGED = 7
    """Статус заказа изменился."""


class MessageTypes(Enum):
    """
    В данном классе перечислены все типы сообщений.
    """
    NON_SYSTEM = 0
    """Несистемное сообщение."""

    ORDER_PURCHASED = 1
    """Покупатель X оплатил заказ #Y. Лот. X, не забудьте потом нажать кнопку «Подтвердить выполнение заказа» или
     «Подтвердить получение валюты»."""

    ORDER_CONFIRMED = 2
    """Покупатель X подтвердил успешное выполнение заказа #Y и отправил деньги продавцу Z."""

    NEW_FEEDBACK = 3
    """Покупатель X написал отзыв к заказу #Y."""

    FEEDBACK_CHANGED = 4
    """Покупатель X изменил отзыв к заказу #Y."""

    FEEDBACK_DELETED = 5
    """Покупатель X удалил отзыв к заказу #Y."""

    NEW_FEEDBACK_ANSWER = 6
    """Продавец Z ответил на отзыв к заказу #Y."""

    FEEDBACK_ANSWER_CHANGED = 7
    """Продавец Z изменил ответ на отзыв к заказу #Y."""

    FEEDBACK_ANSWER_DELETED = 8
    """Продавец Z удалил ответ на отзыв к заказу #Y."""

    ORDER_REOPENED = 9
    """Заказ #Y открыт повторно."""

    REFUND = 10
    """Продавец Z вернул деньги покупателю X по заказу #Y."""

    PARTIAL_REFUND = 11
    """Часть средств по заказу #Y возвращена покупателю."""

    ORDER_CONFIRMED_BY_ADMIN = 12
    """Администратор A подтвердил успешное выполнение заказа #Y и отправил деньги продавцу Z."""

    DISCORD = 13
    """Вы можете перейти в Discord. Внимание: общение за пределами сервера FunPay считается нарушением правил."""

    DEAR_VENDORS = 14
    """Уважаемые продавцы, не доверяйте сообщениям в чате! Перед выполнением заказа всегда проверяйте наличие оплаты в разделе «Мои продажи»."""

    REFUND_BY_ADMIN = 15
    """Администратор A вернул деньги покупателю X по заказу #Y."""


class OrderStatuses(Enum):
    """
    В данном классе перечислены все состояния заказов.
    """
    PAID = 0
    """Заказ оплачен и ожидает выполнения."""
    CLOSED = 1
    """Заказ закрыт."""
    REFUNDED = 2
    """Средства по заказу возвращены."""


class SubCategoryTypes(Enum):
    """
    В данном классе перечислены все типы подкатегорий.
    """
    COMMON = 0
    """Подкатегория со стандартными лотами."""
    CURRENCY = 1
    """Подкатегория с лотами игровой валюты (их нельзя поднимать)."""


class Currency(Enum):
    """
    В данном классе перечислены все типы валют баланса FunPay.
    """
    USD = 0
    """Доллар"""
    RUB = 1
    """Рубль"""
    EUR = 2
    """Евро"""
    UNKNOWN = 3
    """Неизвестная валюта"""

    def __str__(self):
        if self == Currency.USD:
            return "$"
        if self == Currency.RUB:
            return "₽"
        if self == Currency.EUR:
            return "€"
        return "¤"

    @property
    def code(self) -> str:
        if self == Currency.USD:
            return "usd"
        if self == Currency.RUB:
            return "rub"
        if self == Currency.EUR:
            return "eur"
        raise Exception("Неизвестная валюта.")


class Wallet(Enum):
    """
    В данном классе перечислены все кошельки для вывода средств с баланса FunPay.
    """
    QIWI = 0
    """Qiwi кошелек."""
    BINANCE = 1
    """Binance Pay."""
    TRC = 2
    """USDT TRC20."""
    CARD_RUB = 3
    """Рублевая банковская карта."""
    CARD_USD = 4
    """Долларовая банковская карта."""
    CARD_EUR = 5
    """Евро банковская карта."""
    WEBMONEY = 6
    """WebMoney WMZ."""
    YOUMONEY = 7
    """ЮMoney."""
