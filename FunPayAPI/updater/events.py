from __future__ import annotations
import time
from ..common import utils
from ..common.enums import *
from .. import types


class BaseEvent:
    """
    Базовый класс события.

    :param runner_tag: тег Runner'а.
    :type runner_tag: :obj:`str`

    :param event_type: тип события.
    :type event_type: :class:`FunPayAPI.common.enums.EventTypes`

    :param event_time: время события (лучше не указывать, будет генерироваться автоматически).
    :type event_time: :obj:`int` or :obj:`float` or :obj:`None`, опционально.
    """
    def __init__(self, runner_tag: str, event_type: EventTypes, event_time: int | float | None = None):
        self.runner_tag = runner_tag
        self.type = event_type
        self.time = event_time if event_type is not None else time.time()


class InitialChatEvent(BaseEvent):
    """
    Класс события: обнаружен чат при первом запросе Runner'а.

    :param runner_tag: тег Runner'а.
    :type runner_tag: :obj:`str`

    :param chat_obj: объект обнаруженного чата.
    :type chat_obj: :class:`FunPayAPI.types.ChatShortcut`
    """
    def __init__(self, runner_tag: str, chat_obj: types.ChatShortcut):
        super(InitialChatEvent, self).__init__(runner_tag, EventTypes.INITIAL_CHAT)
        self.chat: types.ChatShortcut = chat_obj
        """Объект обнаруженного чата."""


class ChatsListChangedEvent(BaseEvent):
    """
    Класс события: список чатов и / или содержимое одного / нескольких чатов изменилось.

    :param runner_tag: тег Runner'а.
    :type runner_tag: :obj:`str`
    """
    def __init__(self, runner_tag: str):
        super(ChatsListChangedEvent, self).__init__(runner_tag, EventTypes.CHATS_LIST_CHANGED)
        # todo: добавить список всех чатов.


class LastChatMessageChangedEvent(BaseEvent):
    """
    Класс события: последнее сообщение в чате изменилось.

    :param runner_tag: тег Runner'а.
    :type runner_tag: :obj:`str`

    :param chat_obj: объект чата, в котором изменилось полседнее сообщение.
    :type chat_obj: :class:`FunPayAPI.types.ChatShortcut`
    """
    def __init__(self, runner_tag: str, chat_obj: types.ChatShortcut):
        super(LastChatMessageChangedEvent, self).__init__(runner_tag, EventTypes.LAST_CHAT_MESSAGE_CHANGED)
        self.chat: types.ChatShortcut = chat_obj
        """Объект чата, в котором изменилось полседнее сообщение."""


class NewMessageEvent(BaseEvent):
    """
    Класс события: в истории чата обнаружено новое сообщение.

    :param runner_tag: тег Runner'а.
    :type runner_tag: :obj:`str`

    :param message_obj: объект нового сообщения.
    :type message_obj: :class:`FunPayAPI.types.Message`

    :param stack: объект стэка событий новых собщений.
    :type stack: :class:`FunPayAPI.updater.events.MessageEventsStack` or :obj:`None`, опционально
    """
    def __init__(self, runner_tag: str, message_obj: types.Message, stack: MessageEventsStack | None = None):
        super(NewMessageEvent, self).__init__(runner_tag, EventTypes.NEW_MESSAGE)
        self.message: types.Message = message_obj
        """Объект нового сообщения."""
        self.stack: MessageEventsStack = stack
        """Объект стэка событий новых сообщений."""


class MessageEventsStack:
    """
    Данный класс представляет стэк событий новых сообщений.
    Нужен для того, чтобы сразу предоставить доступ ко всем событиям новых сообщений от одного пользователя и одного запроса Runner'а.
    """
    def __init__(self):
        self.__id = utils.random_tag()
        self.__stack = []

    def add_events(self, messages: list[NewMessageEvent]):
        """
        Добавляет события новых сообщений в стэк.

        :param messages: список событий новых сообщений.
        :type messages: :obj:`list` of :class:`FunPayAPI.updater.events.NewMessageEvent`
        """
        self.__stack.extend(messages)

    def get_stack(self) -> list[NewMessageEvent]:
        """
        Возвращает стэк событий новых сообщений.

        :return: стэк событий новых сообщений.
        :rtype: :obj:`list` of :class:`FunPayAPI.updater.events.NewMessageEvent`
        """
        return self.__stack

    def id(self) -> str:
        """
        Возвращает ID стэка (ID стега генерируется случайным образом при создании объекта).

        :return: ID стэка.
        :rtype: :obj:`str`
        """
        return self.__id


class InitialOrderEvent(BaseEvent):
    """
    Класс события: обнаружен заказ при первом запросе Runner'а.

    :param runner_tag: тег Runner'а.
    :type runner_tag: :obj:`str`

    :param order_obj: объект обнаруженного заказа.
    :type order_obj: :class:`FunPayAPI.types.OrderShortcut`
    """
    def __init__(self, runner_tag: str, order_obj: types.OrderShortcut):
        super(InitialOrderEvent, self).__init__(runner_tag, EventTypes.INITIAL_ORDER)
        self.order: types.OrderShortcut = order_obj
        """Объект обнаруженного заказа."""


class OrdersListChangedEvent(BaseEvent):
    """
    Класс события: список заказов и/или статус одного/нескольких заказов изменился.

    :param runner_tag: тег Runner'а.
    :type runner_tag: :obj:`str`

    :param purchases: кол-во незавершенных покупок.
    :type purchases: :obj:`int`

    :param sales: кол-во незавершенных продаж.
    :type sales: :obj:`int`
    """
    def __init__(self, runner_tag: str, purchases: int, sales: int):
        super(OrdersListChangedEvent, self).__init__(runner_tag, EventTypes.ORDERS_LIST_CHANGED)
        self.purchases: int = purchases
        """Кол-во незавершенных покупок."""
        self.sales: int = sales
        """Кол-во незавершенных продаж."""


class NewOrderEvent(BaseEvent):
    """
    Класс события: в списке заказов обнаружен новый заказ.

    :param runner_tag: тег Runner'а.
    :type runner_tag: :obj:`str`

    :param order_obj: объект нового заказа.
    :type order_obj: :class:`FunPayAPI.types.OrderShortcut`
    """
    def __init__(self, runner_tag: str, order_obj: types.OrderShortcut):
        super(NewOrderEvent, self).__init__(runner_tag, EventTypes.NEW_ORDER)
        self.order: types.OrderShortcut = order_obj
        """Объект нового заказа."""


class OrderStatusChangedEvent(BaseEvent):
    """
    Класс события: статус заказа изменился.

    :param runner_tag: тег Runner'а.
    :type runner_tag: :obj:`str`

    :param order_obj: объект измененного заказа.
    :type order_obj: :class:`FunPayAPI.types.OrderShortcut`
    """
    def __init__(self, runner_tag: str, order_obj: types.OrderShortcut):
        super(OrderStatusChangedEvent, self).__init__(runner_tag, EventTypes.ORDER_STATUS_CHANGED)
        self.order: types.OrderShortcut = order_obj
        """Объект измененного заказа."""
