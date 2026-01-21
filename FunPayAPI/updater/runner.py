from __future__ import annotations

import random
import re
import time
import uuid
from typing import TYPE_CHECKING, Generator

import requests

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
        """Делать ли доп запросы для получения новых / изменившихся заказов?"""

        self.__first_request = True
        self.__last_msg_event_tag = utils.random_tag()
        self.__last_order_event_tag = utils.random_tag()
        self.__is_running = False


        self.saved_orders: dict[str, types.OrderShortcut] | None = None
        """Сохраненные состояния заказов ({ID заказа: экземпляр types.OrderShortcut})."""

        self.runner_last_messages: dict[int, list[int, int, str | None]] = {}
        """ID последний сообщений {ID чата: [ID последего сообщения чата, ID последнего прочитанного сообщения чата, 
        текст последнего сообщения или None, если это изображение]}."""

        self.by_bot_ids: dict[int, list[int]] = {}
        """ID сообщений, отправленных с помощью self.account.send_message ({ID чата: [ID сообщения, ...]})."""

        self.last_messages_ids: dict[int, int] = {}
        """ID последних сообщений в чатах ({ID чата: ID последнего сообщения})."""

        self.chat_node_tags: dict[int, str] = {}
        """Теги прочитанных чатов ({ID чата: тег})"""

        self.users_ids: dict[int, int] = {}
        """id чата - id собеседника"""

        self.buyers_viewing: dict[int, types.BuyerViewing] = {}
        """Что смотрит покупатель? ({ID покупателя: что смотрит}"""

        self.runner_len: int = 10
        """Количество событий, на которое успешно отвечает funpay.com/runner/"""

        self.payload_queue: dict [str, dict] = {}
        """uuid4 - payload"""

        self.runner_results: dict [str, requests.Response | Exception] = {}
        """uuid4 - response/exception"""
        self.account: Account = account
        """Экземпляр аккаунта, к которому привязан Runner."""

        self.__orders_counters: dict | None = None
        self.__chat_bookmarks: list[dict] = []
        self.__chat_nodes: dict[int, tuple[dict, int]] = {}
        self.__chat_bookmarks_time = 0
        self.account.runner = self

    def __add_payload(self, payload: dict):
        """
        Добавляет полезную нагрузку в очередь и присваивает ей уникальный идентификатор.

        :param payload: словарь с данными для добавления в очередь.
        :type payload: dict

        :return: уникальный идентификатор добавленной полезной нагрузки.
        :rtype: str
        """
        id_ = str(uuid.uuid4())
        self.payload_queue[id_] = payload
        return id_

    def get_result(self, payload: dict) -> requests.Response:
        """
        Отправляет полезную нагрузку на обработку и возвращает HTTP-ответ после выполнения.

        :param payload: словарь с данными для отправки на обработку.
        :type payload: dict

        :return: объект ответа от обработчика в виде `requests.Response`.
        :rtype: requests.Response

        :raises Exception: если результат не был получен в течение ожидания или произошла ошибка при обработке.
        """

        id_ = self.__add_payload(payload)
        while id_ in self.payload_queue:
            time.sleep(0.1)
        for i in range(300):
            if id_ in self.runner_results:
                break
            time.sleep(0.1)
        result = self.runner_results.pop(id_, Exception("Что-то пошло не так во время получения результата"))
        if isinstance(result, Exception):
            raise result
        return result

    def __detect_chats_with_activity(self, amount: int) -> list[int]:
        if not self.__chat_bookmarks or len(self.__chat_bookmarks) < 2:
            return []
        new_list = self.__chat_bookmarks[-1]["data"]["order"]
        old_list = random.choice(self.__chat_bookmarks[:-1])["data"]["order"]
        old_positions = {chat_id: i for i, chat_id in enumerate(old_list)}
        last = float('inf')
        split_index = len(new_list)
        for i in range(len(new_list)-1, -1, -1):
            idx = old_positions.get(new_list[i])

            if idx is None or i < idx or last < idx:
                split_index = i
                break
            else:
                last = idx

        result = new_list[:split_index+1]
        if len(result) >= amount:
            return random.sample(result, amount)
        i = 0
        result = set(result)
        while len(result) < amount and i < len(new_list):
            result.add(new_list[i])
            i+=1

        return list(result)


    def __fill_request_data(self, request_data: dict) -> dict:
        """
        Дополняет словарь запроса дополнительными объектами для отправки на сервер.

        В зависимости от состояния объекта и настроек добавляет:
        - `chat_bookmarks` для отслеживания списка диалогов,
        - `orders_counters` для отслеживания счетчиков заказов,
        - `chat_node` для запросов сообщений из чатов.

        :param request_data: исходный словарь данных запроса.
        :type request_data: dict

        :return: обновленный словарь данных запроса с добавленными объектами.
        :rtype: dict
        """

        if not self.__first_request:
            if (len(request_data["objects"]) < self.runner_len and not self.__orders_counters
                    and "orders_counters" not in [i["type"] for i in request_data["objects"]]):
                request_data["objects"].extend(
                    self.account.get_payload_data(last_order_event_tag=self.__last_order_event_tag)["objects"])

            if (len(request_data["objects"]) < self.runner_len
                    and time.time() - self.__chat_bookmarks_time > 1.5 ** len(self.__chat_bookmarks) - 1
                    and "chat_bookmarks" not in [i["type"] for i in request_data["objects"]]):
                request_data["objects"].extend(
                    self.account.get_payload_data(last_msg_event_tag=self.__last_msg_event_tag)["objects"])
                self.__chat_bookmarks_time = time.time()

        try:
            if (self.make_msg_requests and (remaining := self.runner_len - len(request_data["objects"])) > 0):
                payload_data = self.account.get_payload_data(chats_data=self.__detect_chats_with_activity(remaining),
                                                             include_runner_context=True)
                request_data["objects"].extend(payload_data["objects"])
        except:
            logger.warning("Что-то пошло не так во время подкидывания чатов.")
            logger.debug("TRACEBACK", exc_info=True)
        return request_data


    def loop(self):
        """
        Основной цикл обработки полезных нагрузок
        """
        if self.__is_running:
            return
        self.__is_running = True

        while True:
            try:
                request_data = {"objects": [],
                                "request": False}
                ids = set()

                for id_ in list(self.payload_queue.keys()):
                    payload = self.payload_queue.get(id_)
                    if payload is None:
                        continue
                    if ((not request_data["objects"] and not request_data["request"])
                            or ((len(request_data["objects"]) + len(payload["objects"]) <= self.runner_len and
                            int(bool(request_data["request"])) + int(bool(payload["request"])) <= 1))):
                        request_data["objects"].extend(payload["objects"])
                        request_data["request"] = request_data["request"] or payload["request"]
                        ids.add(id_)
                        self.payload_queue.pop(id_, None)
                    else:
                        break


                if not request_data["objects"] and not request_data["request"]:
                    time.sleep(0.1)
                    continue
                types_ = [i["type"] for i in request_data["objects"]]
                if "orders_counters" in types_ and "chat_bookmarks" in types_:
                    is_listener_request = True
                else:
                    is_listener_request = False
                request_data = self.__fill_request_data(request_data)

                try:
                    result = self.account.runner_request(request_data)
                except Exception as e:
                    result = e

                for id_ in ids:
                    self.runner_results[id_] = result
                if isinstance(result, Exception):
                    time.sleep(5)
                    continue
                try:
                    result = result.json()
                    for obj in result["objects"]:
                        if not is_listener_request and obj["type"] == "orders_counters":
                            self.__orders_counters = obj
                        elif obj["type"] == "chat_bookmarks" and (data := obj.get("data")) and data.get("order"):
                            if not is_listener_request:
                                self.__chat_bookmarks.append(obj)
                        elif (self.make_msg_requests and
                              (obj["type"] == "chat_node" and (data := obj.get("data")) and
                               (node := data.get("node")) and
                              (node_id:=node.get("id")) and (messages := data.get("messages")))):
                            last_msg_id = messages[-1]["id"]
                            if (last_msg_id > self.last_messages_ids.get(node_id, 0) and
                                    (node_id not in self.__chat_nodes or last_msg_id > self.__chat_nodes[node_id][-1])):
                                self.__chat_nodes[node_id] = (obj, last_msg_id)
                except:
                    logger.warning("Что-то пошло не так во время разбора ответа Runner")
                    logger.debug("TRACEBACK", exc_info=True)
            except:
                logger.error("Бабах")
                logger.debug("TRACEBACK", exc_info=True)



    def get_updates(self) -> dict:
        """
        Запрашивает список событий FunPay.

        :return: ответ FunPay.
        :rtype: :obj:`dict`
        """
        response = self.account.abuse_runner(last_msg_event_tag=self.__last_msg_event_tag,
                                               last_order_event_tag=self.__last_order_event_tag)
        json_response = response.json()
        return json_response

    def parse_updates(self, updates_objects: list[dict]) -> list[InitialChatEvent | ChatsListChangedEvent |
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
        for obj in sorted(updates_objects, key=lambda x: x.get("type") == "orders_counters", reverse=True):
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
            self.__chat_nodes = {}
            return events

        lcmc_events_without_new_mess = []
        lcmc_events_with_new_mess = []
        lcmc_events_with_chat_node = []


        for lcmc_event in lcmc_events:
            if lcmc_event.chat.node_msg_id <= self.last_messages_ids.get(lcmc_event.chat.id, -1):
                lcmc_events_without_new_mess.append(lcmc_event)
            elif lcmc_event.chat.node_msg_id <= self.__chat_nodes.get(lcmc_event.chat.id, ({}, -1))[-1]:
                lcmc_events_with_chat_node.append(lcmc_event)
            else:
                lcmc_events_with_new_mess.append(lcmc_event)
        events.extend(lcmc_events_without_new_mess)


        chats_data = {i.chat.id: i.chat.name for i in lcmc_events_with_chat_node}
        chats = [self.__chat_nodes.pop(i.chat.id, ({}, -1))[0] for i in lcmc_events_with_chat_node]
        new_msg_events = self.generate_new_message_events(chats_data=chats_data,
                                                          chats=self.account.parse_chats_histories(chats_data, chats))
        for event in lcmc_events_with_chat_node:
            events.append(event)
            if new_msg_events.get(event.chat.id):
                events.extend(new_msg_events[event.chat.id])


        while lcmc_events_with_new_mess:
            chats_pack = lcmc_events_with_new_mess[:self.runner_len]
            del lcmc_events_with_new_mess[:self.runner_len]

            chats_data = {i.chat.id: i.chat.name for i in chats_pack}
            new_msg_events = self.generate_new_message_events(chats_data)

            # [LastChatMessageChanged, NewMSG, NewMSG ..., LastChatMessageChanged, NewMSG, NewMSG ...]
            for i in chats_pack:
                events.append(i)
                if new_msg_events.get(i.chat.id):
                    events.extend(new_msg_events[i.chat.id])
        return events

    def generate_new_message_events(self, chats_data: dict[int, str],
                                    chats: dict[int | str, list[types.Message]] | None = None) -> dict[int, list[NewMessageEvent]]:
        """
        Получает историю переданных чатов и генерирует события новых сообщений.


        :param chats_data: ID чатов и никнеймы собеседников (None, если никнейм неизвестен)
            Например: {48392847: "SLLMK", 58392098: "Amongus", 38948728: None}
        :type chats_data: :obj:`dict` {:obj:`int`: :obj:`str` or :obj:`None`}

        :param chats: словарь с историями чатов в формате {ID чата: список сообщений}, если уже получены.
        :type chats: dict[int | str, list[types.Message]] | None

        :return: словарь с событиями новых сообщений в формате {ID чата: [список событий]}
        :rtype: :obj:`dict` {:obj:`int`: :obj:`list` of :class:`FunPayAPI.updater.events.NewMessageEvent`}
        """

        if chats is None:
            attempts = 3
            while attempts:
                attempts -= 1
                try:
                    chats = self.account.get_chats_histories(chats_data, include_runner_context=True)
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
            self.chat_node_tags[cid] = messages[-1].tag # Перезаписываем тег чата
            self.users_ids[cid] = messages[-1].interlocutor_id
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
                orders_list = self.account.get_sales()[1]  # todo добавить возможность реакции на подтверждение очень старых заказов
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

        now_orders = {}
        for order in orders_list:
            now_orders[order.id] = order
            if self.saved_orders is None:
                events.append(InitialOrderEvent(self.__last_order_event_tag, order))
            elif order.id not in self.saved_orders:
                events.append(NewOrderEvent(self.__last_order_event_tag, order))
                if order.status == types.OrderStatuses.CLOSED:
                    events.append(OrderStatusChangedEvent(self.__last_order_event_tag, order))
            elif order.status != self.saved_orders[order.id].status:
                events.append(OrderStatusChangedEvent(self.__last_order_event_tag, order))
        self.saved_orders = now_orders
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

        while True:
            start_time = time.time()
            try:
                if not (self.__orders_counters and self.__chat_bookmarks):
                    updates_objects = self.get_updates()["objects"]
                    is_request_made = True
                else:
                    updates_objects = [self.__orders_counters,]
                    chat_bookmarks = self.__chat_bookmarks[::-1]
                    chat_ids = set()
                    for cb in chat_bookmarks:
                        cb_ids = set(cb["data"]["order"])
                        if chat_ids.issuperset(cb_ids):
                            continue
                        chat_ids.update(cb_ids)
                        updates_objects.append(cb)
                    is_request_made = False
                self.__orders_counters = None
                self.__chat_bookmarks = []
                events = self.parse_updates(updates_objects)
                if is_request_made and not events:
                    # если сделали запрос и не получили эвентов, то сохраненные чаты нам больше не понадобятся
                    self.__chat_nodes = {}
                for event in events:
                    yield event
            except Exception as e:
                if not ignore_exceptions:
                    raise e
                else:
                    logger.error("Произошла ошибка при получении событий. "
                                 "(ничего страшного, если это сообщение появляется нечасто).")
                    logger.debug("TRACEBACK", exc_info=True)
            iteration_time = time.time() - start_time
            if time.time() - self.account.last_429_err_time > 60:
                rt = requests_delay - iteration_time
                if rt > 0:
                    time.sleep(rt)
            else:
                time.sleep(requests_delay)
