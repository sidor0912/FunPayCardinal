from __future__ import annotations

import re
from typing import TYPE_CHECKING, Generator
if TYPE_CHECKING:
    from ..account import Account

import json
import logging
from bs4 import BeautifulSoup

from ..common import exceptions
from .events import *


logger = logging.getLogger("FunPayAPI.runner")


class Runner:
    """
    Класс для получения новых событий FunPay.

    :param account: экземпляр аккаунта (должен быть инициализирован с помощью метода :meth:`FunPayAPI.account.Account.get`).
    :type account: :class:`FunPayAPI.account.Account`

    :param disable_message_requests: отключить ли запросы для получения истории чатов?\n
        Если `True`, :meth:`FunPayAPI.updater.runner.Runner.listen` не будет возвращать события
        :class:`FunPayAPI.updater.events.NewMessageEvent`.\n
        Из событий, связанных с чатами, будут возвращаться только:\n
        * :class:`FunPayAPI.updater.events.InitialChatEvent`\n
        * :class:`FunPayAPI.updater.events.ChatsListChangedEvent`\n
        * :class:`FunPayAPI.updater.events.LastChatMessageChangedEvent`\n
    :type disable_message_requests: :obj:`bool`, опционально

    :param disabled_order_requests: отключить ли запросы для получения списка заказов?\n
        Если `True`, :meth:`FunPayAPI.updater.runner.Runner.listen` не будет возвращать события
        :class:`FunPayAPI.updater.events.InitialOrderEvent`, :class:`FunPayAPI.updater.events.NewOrderEvent`,
        :class:`FunPayAPI.updater.events.OrderStatusChangedEvent`.\n
        Из событий, связанных с заказами, будет возвращаться только
        :class:`FunPayAPI.updater.events.OrdersListChangedEvent`.
    :type disabled_order_requests: :obj:`bool`, опционально
    """
    def __init__(self, account: Account, disable_message_requests: bool = False,
                 disabled_order_requests: bool = False):
        # todo добавить события и исключение событий о новых покупках (не продажах!)
        if not account.is_initiated:
            raise exceptions.AccountNotInitiatedError()
        if account.runner:
            raise Exception("К аккаунту уже привязан Runner!")  # todo

        self.make_msg_requests: bool = False if disable_message_requests else True
        """Делать ли доп. запросы для получения всех новых сообщений изменившихся чатов?"""
        self.make_order_requests: bool = False if disabled_order_requests else True
        """Делать ли доп запросы для получения все новых / изменившихся заказов?"""

        self.__first_request = True
        self.__last_msg_event_tag = utils.random_tag()
        self.__last_order_event_tag = utils.random_tag()

        self.saved_orders: dict[str, types.OrderShortcut] = {}
        """Сохраненные состояния заказов ({ID заказа: экземпляр types.OrderShortcut})."""

        self.last_messages: dict[int, list[str, str | None]] = {}
        """ID последний сообщений ({ID чата: (текст сообщения (до 250 символов), время сообщения)})."""

        self.init_messages: dict[int, str] = {}
        """Текста инит. чатов (для generate_new_message_events)."""

        self.by_bot_ids: dict[int, list[int]] = {}
        """ID сообщений, отправленных с помощью self.account.send_message ({ID чата: [ID сообщения, ...]})."""

        self.last_messages_ids: dict[int, int] = {}
        """ID последних сообщений в чатах ({ID чата: ID последнего сообщения})."""

        self.account: Account = account
        """Экземпляр аккаунта, к которому привязан Runner."""
        self.account.runner = self

        self.__msg_time_re = re.compile(r"\d{2}:\d{2}")

    def get_updates(self) -> dict:
        """
        Запрашивает список событий FunPay.

        :return: ответ FunPay.
        :rtype: :obj:`dict`
        """
        orders = {
            "type": "orders_counters",
            "id": self.account.id,
            "tag": self.__last_order_event_tag,
            "data": False
        }
        chats = {
            "type": "chat_bookmarks",
            "id": self.account.id,
            "tag": self.__last_msg_event_tag,
            "data": False
        }
        payload = {
            "objects": json.dumps([orders, chats]),
            "request": False,
            "csrf_token": self.account.csrf_token
        }
        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest"
        }

        response = self.account.method("post", "runner/", headers, payload, raise_not_200=True)
        json_response = response.json()
        logger.debug(f"Получены данные о событиях: {json_response}")
        return json_response

    def parse_updates(self, updates: dict) -> list[InitialChatEvent | ChatsListChangedEvent |
                                                   LastChatMessageChangedEvent | NewMessageEvent | InitialOrderEvent |
                                                   OrdersListChangedEvent | NewOrderEvent | OrderStatusChangedEvent]:
        """
        Парсит ответ FunPay и создает события.

        :param updates: результат выполнения :meth:`FunPayAPI.updater.runner.Runner.get_updates`
        :type updates: :obj:`dict`

        :return: список событий.
        :rtype: :obj:`list` of :class:`FunPayAPI.updater.events.InitialChatEvent`,
            :class:`FunPayAPI.updater.events.ChatsListChangedEvent`,
            :class:`FunPayAPI.updater.events.LastChatMessageChangedEvent`,
            :class:`FunPayAPI.updater.events.NewMessageEvent`, :class:`FunPayAPI.updater.events.InitialOrderEvent`,
            :class:`FunPayAPI.updater.events.OrdersListChangedEvent`,
            :class:`FunPayAPI.updater.events.NewOrderEvent`,
            :class:`FunPayAPI.updater.events.OrderStatusChangedEvent`
        """
        events = []
        for obj in updates["objects"]:
            if obj.get("type") == "chat_bookmarks":
                events.extend(self.parse_chat_updates(obj))
            elif obj.get("type") == "orders_counters":
                events.extend(self.parse_order_updates(obj))

        if self.__first_request:
            self.__first_request = False
        return events

    def parse_chat_updates(self, obj) -> list[InitialChatEvent | ChatsListChangedEvent | LastChatMessageChangedEvent |
                                              NewMessageEvent]:
        """
        Парсит события, связанные с чатами.

        :param obj: словарь из результата выполнения :meth:`FunPayAPI.updater.runner.Runner.get_updates`, где
            "type" == "chat_bookmarks".
        :type obj: :obj:`dict`

        :return: список событий, связанных с чатами.
        :rtype: :obj:list of :class:`FunPayAPI.updater.events.InitialChatEvent`,
            :class:`FunPayAPI.updater.events.ChatsListChangedEvent`,
            :class:`FunPayAPI.updater.events.LastChatMessageChangedEvent`,
            :class:`FunPayAPI.updater.events.NewMessageEvent`
        """
        events, lcmc_events = [], []
        self.__last_msg_event_tag = obj.get("tag")
        parser = BeautifulSoup(obj["data"]["html"], "html.parser")
        chats = parser.find_all("a", {"class": "contact-item"})

        # Получаем все изменившиеся чаты
        for chat in chats:
            chat_id = int(chat["data-id"])
            # Если чат удален админами - скип.
            if not (last_msg_text := chat.find("div", {"class": "contact-item-message"})):
                continue

            last_msg_text = last_msg_text.text
            if last_msg_text.startswith(self.account.bot_character):
                last_msg_text = last_msg_text[1:]
            last_msg_time = chat.find("div", {"class": "contact-item-time"}).text

            # Если текст последнего сообщения совпадает с сохраненным
            if chat_id in self.last_messages and self.last_messages[chat_id][0] == last_msg_text:
                # Если есть сохраненное время сообщения для данного чата
                if self.last_messages[chat_id][1]:
                    # Если время ласт сообщения не имеет формат ЧЧ:ММ или совпадает с сохраненным - скип чата
                    if not self.__msg_time_re.fullmatch(last_msg_time) or self.last_messages[chat_id][1] == last_msg_time:
                        continue
                # Если нет сохраненного времени сообщения для данного чата - скип чата
                else:
                    continue

            unread = True if "unread" in chat.get("class") else False
            chat_with = chat.find("div", {"class": "media-user-name"}).text
            chat_obj = types.ChatShortcut(chat_id, chat_with, last_msg_text, unread, str(chat))
            self.account.add_chats([chat_obj])
            self.last_messages[chat_id] = [last_msg_text, last_msg_time]

            if self.__first_request:
                events.append(InitialChatEvent(self.__last_msg_event_tag, chat_obj))
                self.init_messages[chat_id] = last_msg_text
                continue
            else:
                lcmc_events.append(LastChatMessageChangedEvent(self.__last_msg_event_tag, chat_obj))

        # Если есть события изменения чатов, значит это не первый запрос и ChatsListChangedEvent будет первым событием
        if lcmc_events:
            events.append(ChatsListChangedEvent(self.__last_msg_event_tag))

        if not self.make_msg_requests:
            events.extend(lcmc_events)
            return events

        while lcmc_events:
            chats_pack = lcmc_events[:10]
            del lcmc_events[:10]
            chats_data = {i.chat.id: i.chat.name for i in chats_pack}
            new_msg_events = self.generate_new_message_events(chats_data)
            # [LastChatMessageChanged, NewMSG, NewMSG ..., LastChatMessageChanged, MewMSG, NewMSG ...]
            for i in chats_pack:
                events.append(i)
                if new_msg_events.get(i.chat.id):
                    events.extend(new_msg_events[i.chat.id])
        return events

    def generate_new_message_events(self, chats_data: dict[int, str]) -> dict[int, list[NewMessageEvent]]:
        """
        Получает историю переданных чатов и генерирует события новых сообщений.

        :param chats_data: ID чатов и никнеймы собеседников (None, если никнейм неизвестен)
            Например: {48392847: "SLLMK", 58392098: "Amongus", 38948728: None}
        :type chats_data: :obj:`dict` {:obj:`int`: :obj:`str` or :obj:`None`}

        :return: словарь с событиями новых сообщений в формате {ID чата: [список событий]}
        :rtype: :obj:`dict` {:obj:`int`: :obj:`list` of :class:`FunPayAPI.updater.events.NewMessageEvent`}
        """
        attempts = 3
        while attempts:
            attempts -= 1
            try:
                chats = self.account.get_chats_histories(chats_data)
                break
            except exceptions.RequestFailedError as e:
                logger.error(e)
            except:
                logger.error(f"Не удалось получить истории чатов {list(chats_data.keys())}.")
                logger.debug("TRACEBACK", exc_info=True)
            time.sleep(1)
        else:
            logger.error(f"Не удалось получить истории чатов {list(chats_data.keys())}: превышено кол-во попыток.")
            return {}

        result = {}

        for cid in chats:
            messages = chats[cid]
            result[cid] = []
            self.by_bot_ids[cid] = self.by_bot_ids.get(cid) or []

            # Удаляем все сообщения, у которых ID меньше сохраненного последнего сообщения
            if self.last_messages_ids.get(cid):
                messages = [i for i in messages if i.id > self.last_messages_ids[cid]]
            if not messages:
                continue

            # Отмечаем все сообщения, отправленные с помощью Account.send_message()
            if self.by_bot_ids.get(cid):
                for i in messages:
                    if not i.by_bot and i.id in self.by_bot_ids[cid]:
                        i.by_bot = True

            stack = MessageEventsStack()

            # Если нет сохраненного ID последнего сообщения
            if not self.last_messages_ids.get(cid):
                # Если данный чат был доступен при первом запросе и есть сохраненное последнее сообщение,
                # то ищем новые сообщения относительно последнего сохраненного текста
                if init_msg_text := self.init_messages.get(cid):
                    del self.init_messages[cid]
                    temp = []
                    for i in reversed(messages):
                        if i.image_link:
                            if init_msg_text == "Изображение":
                                if not temp:
                                    temp.append(i)
                                break
                        elif i.text[:250] == init_msg_text:
                            break
                        temp.append(i)
                    messages = list(reversed(temp))

                # Если данного чата не было при первом запросе, в результат добавляем только ласт сообщение истории.
                else:
                    messages = messages[-1:]

            self.last_messages_ids[cid] = messages[-1].id  # Перезаписываем ID последнего сообщение
            self.by_bot_ids[cid] = [i for i in self.by_bot_ids[cid] if i > self.last_messages_ids[cid]]  # чистим память

            for msg in messages:
                event = NewMessageEvent(self.__last_msg_event_tag, msg, stack)
                stack.add_events([event])
                result[cid].append(event)
        return result

    def parse_order_updates(self, obj) -> list[InitialOrderEvent | OrdersListChangedEvent | NewOrderEvent |
                                               OrderStatusChangedEvent]:
        """
        Парсит события, связанные с продажами.

        :param obj: словарь из результата выполнения :meth:`FunPayAPI.updater.runner.Runner.get_updates`, где
            "type" == "orders_counters".
        :type obj: :obj:`dict`

        :return: список событий, связанных с продажами.
        :rtype: :obj:`list` of :class:`FunPayAPI.updater.events.InitialOrderEvent`,
            :class:`FunPayAPI.updater.events.OrdersListChangedEvent`,
            :class:`FunPayAPI.updater.events.NewOrderEvent`,
            :class:`FunPayAPI.updater.events.OrderStatusChangedEvent`
        """
        events = []
        self.__last_order_event_tag = obj.get("tag")
        if not self.__first_request:
            events.append(OrdersListChangedEvent(self.__last_order_event_tag,
                                                 obj["data"]["buyer"], obj["data"]["seller"]))
        if not self.make_order_requests:
            return events

        attempts = 3
        while attempts:
            attempts -= 1
            try:
                orders_list = self.account.get_sells()
                break
            except exceptions.RequestFailedError as e:
                logger.error(e)
            except:
                logger.error("Не удалось обновить список заказов.")
                logger.debug("TRACEBACK", exc_info=True)
            time.sleep(1)
        else:
            logger.error("Не удалось обновить список продаж: превышено кол-во попыток.")
            return events

        for order in orders_list[1]:
            if order.id not in self.saved_orders:
                if self.__first_request:
                    events.append(InitialOrderEvent(self.__last_order_event_tag, order))
                else:
                    events.append(NewOrderEvent(self.__last_order_event_tag, order))
                    if order.status == types.OrderStatuses.CLOSED:
                        events.append(OrderStatusChangedEvent(self.__last_order_event_tag, order))
                self.update_order(order)

            elif order.status != self.saved_orders[order.id].status:
                events.append(OrderStatusChangedEvent(self.__last_order_event_tag, order))
                self.update_order(order)
        return events

    def update_last_message(self, chat_id: int, message_text: str | None, message_time: str | None = None):
        """
        Обновляет сохраненный текст последнего сообщения чата.

        :param chat_id: ID чата.
        :type chat_id: :obj:`int`

        :param message_text: текст сообщения (если `None`, заменяется за "Изображение").
        :type message_text: :obj:`str` or :obj:`None`

        :param message_time: время отправки сообщения в формате ЧЧ:ММ. Используется исключительно Runner'ом.
        :type message_time: :obj:`str` or :obj:`None`, опционально
        """
        if message_text is None:
            message_text = "Изображение"
        self.last_messages[chat_id] = [message_text[:250], message_time]

    def update_order(self, order: types.OrderShortcut):
        """
        Обновляет сохраненное состояние переданного заказа.

        :param order: экземпляр заказа, который нужно обновить.
        :type order: :class:`FunPayAPI.types.OrderShortcut`
        """
        self.saved_orders[order.id] = order

    def mark_as_by_bot(self, chat_id: int, message_id: int):
        """
        Помечает сообщение с переданным ID, как отправленный с помощью :meth:`FunPayAPI.account.Account.send_message`.

        :param chat_id: ID чата.
        :type chat_id: :obj:`int`

        :param message_id: ID сообщения.
        :type message_id: :obj:`int`
        """
        if self.by_bot_ids.get(chat_id) is None:
            self.by_bot_ids[chat_id] = [message_id]
        else:
            self.by_bot_ids[chat_id].append(message_id)

    def listen(self, requests_delay: int | float = 6.0,
               ignore_exceptions: bool = True) -> Generator[InitialChatEvent | ChatsListChangedEvent |
                                                            LastChatMessageChangedEvent | NewMessageEvent |
                                                            InitialOrderEvent | OrdersListChangedEvent | NewOrderEvent |
                                                            OrderStatusChangedEvent]:
        """
        Бесконечно отправляет запросы для получения новых событий.

        :param requests_delay: задержка между запросами (в секундах).
        :type requests_delay: :obj:`int` or :obj:`float`, опционально

        :param ignore_exceptions: игнорировать ошибки?
        :type ignore_exceptions: :obj:`bool`, опционально

        :return: генератор событий FunPay.
        :rtype: :obj:`Generator` of :class:`FunPayAPI.updater.events.InitialChatEvent`,
            :class:`FunPayAPI.updater.events.ChatsListChangedEvent`,
            :class:`FunPayAPI.updater.events.LastChatMessageChangedEvent`,
            :class:`FunPayAPI.updater.events.NewMessageEvent`, :class:`FunPayAPI.updater.events.InitialOrderEvent`,
            :class:`FunPayAPI.updater.events.OrdersListChangedEvent`,
            :class:`FunPayAPI.updater.events.NewOrderEvent`,
            :class:`FunPayAPI.updater.events.OrderStatusChangedEvent`
        """
        while True:
            try:
                updates = self.get_updates()
                events = self.parse_updates(updates)
                for event in events:
                    yield event
            except Exception as e:
                if not ignore_exceptions:
                    raise e
                else:
                    logger.error("Произошла ошибка при получении событий. "
                                 "(ничего страшного, если это сообщение появляется нечасто).")
                    logger.debug("TRACEBACK", exc_info=True)
            time.sleep(requests_delay)
