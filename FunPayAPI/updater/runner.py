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
                 disabled_order_requests: bool = False,
                 disabled_buyer_viewing_requests: bool = True):
        # todo добавить события и исключение событий о новых покупках (не продажах!)
        if not account.is_initiated:
            raise exceptions.AccountNotInitiatedError()
        if account.runner:
            raise Exception("К аккаунту уже привязан Runner!")  # todo

        self.make_msg_requests: bool = False if disable_message_requests else True
        """Делать ли доп. запросы для получения всех новых сообщений изменившихся чатов?"""
        self.make_order_requests: bool = False if disabled_order_requests else True
        """Делать ли доп запросы для получения новых / изменившихся заказов?"""
        self.make_buyer_viewing_requests: bool = False if disabled_buyer_viewing_requests else True
        """Делать ли доп запросы для получения поля "Покупатель смотрит"?"""

        self.__first_request = True
        self.__last_msg_event_tag = utils.random_tag()
        self.__last_order_event_tag = utils.random_tag()

        self.saved_orders: dict[str, types.OrderShortcut] = {}
        """Сохраненные состояния заказов ({ID заказа: экземпляр types.OrderShortcut})."""

        self.runner_last_messages: dict[int, list[int, int, str | None]] = {}
        """ID последний сообщений {ID чата: [ID последего сообщения чата, ID последнего прочитанного сообщения чата, 
        текст последнего сообщения или None, если это изображение]}."""

        self.by_bot_ids: dict[int, list[int]] = {}
        """ID сообщений, отправленных с помощью self.account.send_message ({ID чата: [ID сообщения, ...]})."""

        self.last_messages_ids: dict[int, int] = {}
        """ID последних сообщений в чатах ({ID чата: ID последнего сообщения})."""

        self.buyers_viewing: dict[int, types.BuyerViewing] = {}
        """Что смотрит покупатель? ({ID покупателя: что смотрит}"""

        self.runner_len: int = 10
        """Количество событий, на которое успешно отвечает funpay.com/runner/"""
        self.__interlocutor_ids: set = set()
        """Айди собеседников, у которых будет получено поле "Покупатель смотрит\""""

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
        buyers = [{"type": "c-p-u",
                   "id": str(buyer),
                   "tag": utils.random_tag(),
                   "data": False} for buyer in self.__interlocutor_ids or []]
        payload = {
            "objects": json.dumps([orders, chats, *buyers]),
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
        # сортируем в т.ч. для того, корректно реагировало на сообщения покупателей сразу после оплаты (плагины автовыдачи)
        for obj in sorted(updates["objects"], key=lambda x: x.get("type") == "orders_counters", reverse=True):
            if obj.get("type") == "chat_bookmarks":
                events.extend(self.parse_chat_updates(obj))
            elif obj.get("type") == "orders_counters":
                events.extend(self.parse_order_updates(obj))
            elif obj.get("type") == "c-p-u":
                bv = self.account.parse_buyer_viewing(obj)
                self.buyers_viewing[bv.buyer_id] = bv
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
        parser = BeautifulSoup(obj["data"]["html"], "lxml")
        chats = parser.find_all("a", {"class": "contact-item"})

        # Получаем все изменившиеся чаты
        for chat in chats:
            chat_id = int(chat["data-id"])
            # Если чат удален админами - скип.
            if not (last_msg_text := chat.find("div", {"class": "contact-item-message"})):
                continue

            last_msg_text = last_msg_text.text

            node_msg_id = int(chat.get('data-node-msg'))
            user_msg_id = int(chat.get('data-user-msg'))
            by_bot = False
            by_vertex = False
            if last_msg_text.startswith(self.account.bot_character):
                last_msg_text = last_msg_text[1:]
                by_bot = True
            elif last_msg_text.startswith(self.account.old_bot_character):
                last_msg_text = last_msg_text[1:]
                by_vertex = True
            # если сообщение отправлено непрочитанным и вкл старый режим, то [0, 0, None] или [0, 0, "text"]
            prev_node_msg_id, prev_user_msg_id, prev_text = self.runner_last_messages.get(chat_id) or [-1, -1, None]
            last_msg_text_or_none = None if last_msg_text in ("Изображение", "Зображення", "Image") else last_msg_text
            if node_msg_id <= prev_node_msg_id:
                continue
            elif not prev_node_msg_id and not prev_user_msg_id and prev_text == last_msg_text_or_none:
                # значит сообщение отправлено ботом и оставлено непрочитанным - просто обновляем инфу
                self.runner_last_messages[chat_id] = [node_msg_id, user_msg_id, last_msg_text_or_none]
                continue
            unread = True if "unread" in chat.get("class") else False

            chat_with = chat.find("div", {"class": "media-user-name"}).text
            chat_obj = types.ChatShortcut(chat_id, chat_with, last_msg_text, node_msg_id,
                                          user_msg_id, unread, str(chat))
            if last_msg_text_or_none is not None:
                chat_obj.last_by_bot = by_bot
                chat_obj.last_by_vertex = by_vertex

            self.account.add_chats([chat_obj])
            self.runner_last_messages[chat_id] = [node_msg_id, user_msg_id, last_msg_text_or_none]
            if self.__first_request:
                events.append(InitialChatEvent(self.__last_msg_event_tag, chat_obj))
                if self.make_msg_requests:
                    self.last_messages_ids[chat_id] = node_msg_id
                continue
            else:
                lcmc_events.append(LastChatMessageChangedEvent(self.__last_msg_event_tag, chat_obj))

        # Если есть события изменения чатов, значит это не первый запрос и ChatsListChangedEvent будет первым событием
        if lcmc_events:
            events.append(ChatsListChangedEvent(self.__last_msg_event_tag))

        if not self.make_msg_requests:
            events.extend(lcmc_events)
            return events

        lcmc_events_without_new_mess = []
        lcmc_events_with_new_mess = []
        for lcmc_event in lcmc_events:
            if lcmc_event.chat.node_msg_id <= self.last_messages_ids.get(lcmc_event.chat.id, -1):
                lcmc_events_without_new_mess.append(lcmc_event)
            else:
                lcmc_events_with_new_mess.append(lcmc_event)
        events.extend(lcmc_events_without_new_mess)

        if self.make_buyer_viewing_requests:
            # в приоритете те, у которых не известен айди собеседника (чтобы быстрее узнать, что они смотрят)
            lcmc_events_with_new_mess.sort(key=lambda i: i.chat.id not in self.account.interlocutor_ids)
            self.__interlocutor_ids = self.__interlocutor_ids | set([self.account.interlocutor_ids.get(i.chat.id)
                                                                     for i in lcmc_events_with_new_mess if
                                                                     i.chat.id in self.account.interlocutor_ids])

        while lcmc_events_with_new_mess or len(self.__interlocutor_ids) >= self.runner_len - 2:
            chats_pack = lcmc_events_with_new_mess[:self.runner_len]
            del lcmc_events_with_new_mess[:self.runner_len]
            bv_pack = []
            while self.make_buyer_viewing_requests and \
                    len(chats_pack) + len(bv_pack) < self.runner_len and self.__interlocutor_ids:
                interlocutor_id = self.__interlocutor_ids.pop()
                if interlocutor_id not in self.buyers_viewing:
                    bv_pack.append(interlocutor_id)

            chats_data = {i.chat.id: i.chat.name for i in chats_pack}
            new_msg_events = self.generate_new_message_events(chats_data, bv_pack)

            if self.make_buyer_viewing_requests:
                # Если раньше айди не знали, то добавляем
                for chat_id, msgs in new_msg_events.items():
                    if chat_id not in self.account.interlocutor_ids and msgs and msgs[0].message.interlocutor_id:
                        self.account.interlocutor_ids[chat_id] = msgs[0].message.interlocutor_id
                        self.__interlocutor_ids.add(msgs[0].message.interlocutor_id)

            # [LastChatMessageChanged, NewMSG, NewMSG ..., LastChatMessageChanged, NewMSG, NewMSG ...]
            for i in chats_pack:
                events.append(i)
                if new_msg_events.get(i.chat.id):
                    events.extend(new_msg_events[i.chat.id])
        return events

    def generate_new_message_events(self, chats_data: dict[int, str],
                                    interlocutor_ids: list[int] | None = None) -> dict[int, list[NewMessageEvent]]:
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
                chats = self.account.get_chats_histories(chats_data, interlocutor_ids)
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
                messages = [m for m in messages if
                            m.id > min(self.last_messages_ids.values(), default=10 ** 20)] or messages[-1:]

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
                orders_list = self.account.get_sales()  # todo добавить возможность реакции на подтверждение очень старых заказов
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

        saved_orders = {}
        for order in orders_list[1]:
            saved_orders[order.id] = order
            if order.id not in self.saved_orders:
                if self.__first_request:
                    events.append(InitialOrderEvent(self.__last_order_event_tag, order))
                else:
                    events.append(NewOrderEvent(self.__last_order_event_tag, order))
                    if order.status == types.OrderStatuses.CLOSED:
                        events.append(OrderStatusChangedEvent(self.__last_order_event_tag, order))

            elif order.status != self.saved_orders[order.id].status:
                events.append(OrderStatusChangedEvent(self.__last_order_event_tag, order))
        self.saved_orders = saved_orders
        return events

    def update_last_message(self, chat_id: int, message_id: int, message_text: str | None):
        """
        Обновляет сохраненный ID последнего сообщения чата.

        :param chat_id: ID чата.
        :type chat_id: :obj:`int`

        :param message_id: ID сообщения.
        :type message_id: :obj:`int`

        :param message_text: текст сообщения или None, если это изображение.
        :type message_text: :obj:`str` or :obj:`None`
        """
        self.runner_last_messages[chat_id] = [message_id, message_id, message_text]

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
        events = []
        while True:
            try:
                self.__interlocutor_ids = set([event.message.interlocutor_id for event in events
                                               if event.type == EventTypes.NEW_MESSAGE])
                updates = self.get_updates()
                events.extend(self.parse_updates(updates))
                next_events = []
                for event in events:
                    if self.make_msg_requests and self.make_buyer_viewing_requests \
                            and event.type == EventTypes.NEW_MESSAGE \
                            and event.message.interlocutor_id is not None:
                        event.message.buyer_viewing = self.buyers_viewing.get(event.message.interlocutor_id)
                        if event.message.buyer_viewing is None:
                            next_events.append(event)
                            continue

                    yield event
                events = next_events
                self.buyers_viewing = {}
            except Exception as e:
                if not ignore_exceptions:
                    raise e
                else:
                    logger.error("Произошла ошибка при получении событий. "
                                 "(ничего страшного, если это сообщение появляется нечасто).")
                    logger.debug("TRACEBACK", exc_info=True)
            time.sleep(requests_delay)
