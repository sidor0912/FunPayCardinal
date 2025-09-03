from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from FunPayAPI import types
from FunPayAPI.common.enums import SubCategoryTypes

if TYPE_CHECKING:
    from configparser import ConfigParser

from tg_bot import auto_response_cp, config_loader_cp, auto_delivery_cp, templates_cp, plugins_cp, file_uploader, \
    authorized_users_cp, proxy_cp, default_cp
from types import ModuleType
import Utils.exceptions
from uuid import UUID
import importlib.util
import configparser
import itertools
import requests
import datetime
import logging
import random
import time
import sys
import os
from pip._internal.cli.main import main
import FunPayAPI
import handlers
import announcements
from locales.localizer import Localizer
from FunPayAPI import utils as fp_utils
from Utils import cardinal_tools
import tg_bot.bot

from threading import Thread

logger = logging.getLogger("FPC")
localizer = Localizer()
_ = localizer.translate


def get_cardinal() -> None | Cardinal:
    """
    Возвращает существующий экземпляр кардинала.
    """
    if hasattr(Cardinal, "instance"):
        return getattr(Cardinal, "instance")


class PluginData:
    """
    Класс, описывающий плагин.
    """

    def __init__(self, name: str, version: str, desc: str, credentials: str, uuid: str,
                 path: str, plugin: ModuleType, settings_page: bool, delete_handler: Callable | None, enabled: bool):
        """
        :param name: название плагина.
        :param version: версия плагина.
        :param desc: описание плагина.
        :param credentials: авторы плагина.
        :param uuid: UUID плагина.
        :param path: путь до плагина.
        :param plugin: экземпляр плагина как модуля.
        :param settings_page: есть ли страница настроек у плагина.
        :param delete_handler: хэндлер, привязанный к удалению плагина.
        :param enabled: включен ли плагин.
        """
        self.name = name
        self.version = version
        self.description = desc
        self.credits = credentials
        self.uuid = uuid

        self.path = path
        self.plugin = plugin
        self.settings_page = settings_page
        self.commands = {}
        self.delete_handler = delete_handler
        self.enabled = enabled


class Cardinal(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Cardinal, cls).__new__(cls)
        return getattr(cls, "instance")

    def __init__(self, main_config: ConfigParser,
                 auto_delivery_config: ConfigParser,
                 auto_response_config: ConfigParser,
                 raw_auto_response_config: ConfigParser,
                 version: str):
        self.VERSION = version
        self.instance_id = random.randint(0, 999999999)
        self.delivery_tests = {}  # Одноразовые ключи для тестов автовыдачи. {"ключ": "название лота"}

        # Конфиги
        self.MAIN_CFG = main_config
        self.AD_CFG = auto_delivery_config
        self.AR_CFG = auto_response_config
        self.RAW_AR_CFG = raw_auto_response_config
        # Прокси
        self.proxy = {}
        self.proxy_dict = cardinal_tools.load_proxy_dict()  # прокси {0: "login:password@ip:port", 1: "ip:port"...}
        if self.MAIN_CFG["Proxy"].getboolean("enable"):
            if self.MAIN_CFG["Proxy"]["ip"] and self.MAIN_CFG["Proxy"]["port"].isnumeric():
                logger.info(_("crd_proxy_detected"))

                ip, port = self.MAIN_CFG["Proxy"]["ip"], self.MAIN_CFG["Proxy"]["port"]
                login, password = self.MAIN_CFG["Proxy"]["login"], self.MAIN_CFG["Proxy"]["password"]
                proxy_str = f"{f'{login}:{password}@' if login and password else ''}{ip}:{port}"
                self.proxy = {
                    "http": f"http://{proxy_str}",
                    "https": f"http://{proxy_str}"
                }

                if proxy_str not in self.proxy_dict.values():
                    max_id = max(self.proxy_dict.keys(), default=-1)
                    self.proxy_dict[max_id + 1] = proxy_str
                    cardinal_tools.cache_proxy_dict(self.proxy_dict)

                if self.MAIN_CFG["Proxy"].getboolean("check") and not cardinal_tools.check_proxy(self.proxy):
                    sys.exit()

        self.account = FunPayAPI.Account(self.MAIN_CFG["FunPay"]["golden_key"],
                                         self.MAIN_CFG["FunPay"]["user_agent"],
                                         proxy=self.proxy)
        self.runner: FunPayAPI.Runner | None = None
        self.telegram: tg_bot.bot.TGBot | None = None

        self.running = False
        self.run_id = 0
        self.start_time = int(time.time())

        self.balance: FunPayAPI.types.Balance | None = None
        self.raise_time = {}  # Временные метки поднятия категорий {id игры: след. время поднятия}
        self.raised_time = {}  # Время последнего поднятия категории {id игры: время последнего поднятия}
        self.__exchange_rates = {}  # Курс валют {(валюта1, валюта2): (курс, время обновления)}
        self.profile: FunPayAPI.types.UserProfile | None = None  # FunPay профиль для всего кардинала (+ хэндлеров)
        self.tg_profile: FunPayAPI.types.UserProfile | None = None  # FunPay профиль (для Telegram-ПУ)
        self.last_tg_profile_update = datetime.datetime.now()  # Последнее время обновления профиля для TG-ПУ
        self.curr_profile: FunPayAPI.types.UserProfile | None = None  # Текущий профиль (для восст. / деакт. лотов.)
        # Тег последнего event'а, после которого обновлялся self.current_profile
        self.curr_profile_last_tag: str | None = None
        # Тег последнего event'а, после которого в self.profile добавлялись отсутствующие ранее лоты
        self.profile_last_tag: str | None = None
        # Тег последнего event'а, после которого обновлялось состояние лотов.
        self.last_state_change_tag: str | None = None
        # Тег последнего event'а, перед которым пороговое значение для определения новых чатов.
        self.last_greeting_chat_id_threshold_change_tag: str | None = None
        self.greeting_threshold_chat_ids = set()  # ID чатов для последующего обновления  self.greeting_chat_id_threshold
        self.blacklist = cardinal_tools.load_blacklist()  # ЧС.
        self.old_users = cardinal_tools.load_old_users(
            float(self.MAIN_CFG["Greetings"]["greetingsCooldown"]))  # Уже написавшие пользователи.
        self.greeting_chat_id_threshold = max(self.old_users.keys(), default=0)
        # пороговое значение для определения новых чатов (для приветствия)

        # Хэндлеры
        self.pre_init_handlers = []
        self.post_init_handlers = []
        self.pre_start_handlers = []
        self.post_start_handlers = []
        self.pre_stop_handlers = []
        self.post_stop_handlers = []

        self.init_message_handlers = []
        self.messages_list_changed_handlers = []
        self.last_chat_message_changed_handlers = []
        self.new_message_handlers = []
        self.init_order_handlers = []
        self.orders_list_changed_handlers = []
        self.new_order_handlers = []
        self.order_status_changed_handlers = []

        self.pre_delivery_handlers = []
        self.post_delivery_handlers = []

        self.pre_lots_raise_handlers = []
        self.post_lots_raise_handlers = []

        self.handler_bind_var_names = {
            "BIND_TO_PRE_INIT": self.pre_init_handlers,
            "BIND_TO_POST_INIT": self.post_init_handlers,
            "BIND_TO_PRE_START": self.pre_start_handlers,
            "BIND_TO_POST_START": self.post_start_handlers,
            "BIND_TO_PRE_STOP": self.pre_stop_handlers,
            "BIND_TO_POST_STOP": self.post_stop_handlers,
            "BIND_TO_INIT_MESSAGE": self.init_message_handlers,
            "BIND_TO_MESSAGES_LIST_CHANGED": self.messages_list_changed_handlers,
            "BIND_TO_LAST_CHAT_MESSAGE_CHANGED": self.last_chat_message_changed_handlers,
            "BIND_TO_NEW_MESSAGE": self.new_message_handlers,
            "BIND_TO_INIT_ORDER": self.init_order_handlers,
            "BIND_TO_NEW_ORDER": self.new_order_handlers,
            "BIND_TO_ORDERS_LIST_CHANGED": self.orders_list_changed_handlers,
            "BIND_TO_ORDER_STATUS_CHANGED": self.order_status_changed_handlers,
            "BIND_TO_PRE_DELIVERY": self.pre_delivery_handlers,
            "BIND_TO_POST_DELIVERY": self.post_delivery_handlers,
            "BIND_TO_PRE_LOTS_RAISE": self.pre_lots_raise_handlers,
            "BIND_TO_POST_LOTS_RAISE": self.post_lots_raise_handlers,
        }

        self.plugins: dict[str, PluginData] = {}
        self.disabled_plugins = cardinal_tools.load_disabled_plugins()

    def __init_account(self) -> None:
        """
        Инициализирует класс аккаунта (self.account)
        """
        while True:
            try:
                self.account.get()
                self.balance = self.get_balance()
                greeting_text = cardinal_tools.create_greeting_text(self)
                cardinal_tools.set_console_title(f"FunPay Cardinal - {self.account.username} ({self.account.id})")
                for line in greeting_text.split("\n"):
                    logger.info(line)
                break
            except TimeoutError:
                logger.error(_("crd_acc_get_timeout_err"))
            except (FunPayAPI.exceptions.UnauthorizedError, FunPayAPI.exceptions.RequestFailedError) as e:
                logger.error(e.short_str())
                logger.debug(f"TRACEBACK {e.short_str()}")
            except:
                logger.error(_("crd_acc_get_unexpected_err"))
                logger.debug("TRACEBACK", exc_info=True)
            logger.warning(_("crd_try_again_in_n_secs", 2))
            time.sleep(2)

    def __update_profile(self, infinite_polling: bool = True, attempts: int = 0, update_telegram_profile: bool = True,
                         update_main_profile: bool = True) -> bool:
        """
        Загружает данные о лотах категориях аккаунта

        :param infinite_polling: бесконечно посылать запросы, пока не будет получен ответ (игнорировать макс. кол-во
        попыток)
        :param attempts: максимальное кол-во попыток.
        :param update_telegram_profile: обновить ли информацию о профиле для TG ПУ?
        :param update_main_profile: обновить ли информацию о профиле для всего кардинала (+ хэндлеров)?

        :return: True, если информация обновлена, False, если превышено макс. кол-во попыток.
        """
        logger.info(_("crd_getting_profile_data"))
        # Получаем категории аккаунта.
        while attempts or infinite_polling:
            try:
                profile = self.account.get_user(self.account.id)
                break
            except TimeoutError:
                logger.error(_("crd_profile_get_timeout_err"))
            except FunPayAPI.exceptions.RequestFailedError as e:
                logger.error(e.short_str())
                logger.debug(e)
            except:
                logger.error(_("crd_profile_get_unexpected_err"))
                logger.debug("TRACEBACK", exc_info=True)
            attempts -= 1
            logger.warning(_("crd_try_again_in_n_secs", 2))
            time.sleep(2)
        else:
            logger.error(_("crd_profile_get_too_many_attempts_err", attempts))
            return False

        if update_main_profile:
            self.profile = profile
            self.curr_profile = profile
            self.lots_ids = [i.id for i in profile.get_lots()]
            logger.info(_("crd_profile_updated", len(profile.get_lots()), len(profile.get_sorted_lots(2))))
        if update_telegram_profile:
            self.tg_profile = profile
            self.last_telegram_lots_update = datetime.datetime.now()
            logger.info(_("crd_tg_profile_updated", len(profile.get_lots()), len(profile.get_sorted_lots(2))))
        return True

    def __init_telegram(self) -> None:
        """
        Инициализирует Telegram бота.
        """
        self.telegram = tg_bot.bot.TGBot(self)
        self.telegram.init()

    def get_balance(self, attempts: int = 3) -> FunPayAPI.types.Balance:
        subcategories = self.account.get_sorted_subcategories()[FunPayAPI.enums.SubCategoryTypes.COMMON]
        lots = []
        while not lots and attempts:
            attempts -= 1
            subcat_id = random.choice(list(subcategories.keys()))
            lots = self.account.get_subcategory_public_lots(FunPayAPI.enums.SubCategoryTypes.COMMON, subcat_id)
            break
        else:
            raise Exception(...)
        balance = self.account.get_balance(random.choice(lots).id)
        return balance

    # Прочее
    def raise_lots(self) -> int:
        """
        Пытается поднять лоты.

        :return: предположительное время, когда нужно снова запустить данную функцию.
        """
        # Время следующего вызова функции (по умолчанию - бесконечность).
        next_call = float("inf")

        for subcat in sorted(list(self.profile.get_sorted_lots(2).keys()), key=lambda x: x.category.position):
            if subcat.type is SubCategoryTypes.CURRENCY:
                continue
            # Если id категории текущей подкатегории уже находится в self.game_ids, но время поднятия подкатегорий
            # данной категории еще не настало - пропускам эту подкатегорию.
            if (saved_time := self.raise_time.get(subcat.category.id)) and saved_time > int(time.time()):
                # Если записанное в self.game_ids время больше текущего времени
                # обновляем время next_call'а на записанное время.
                next_call = saved_time if saved_time < next_call else next_call
                continue

            # В любом другом случае пытаемся поднять лоты всех категорий, относящихся к игре
            raise_ok = False
            error_text = ""
            time_delta = ""
            try:
                time.sleep(1)
                self.account.raise_lots(subcat.category.id)
                logger.info(_("crd_lots_raised", subcat.category.name))
                raise_ok = True
                last_time = self.raised_time.get(subcat.category.id)
                self.raised_time[subcat.category.id] = new_time = int(time.time())  # locale
                time_delta = "" if not last_time else f" Последнее поднятие: {cardinal_tools.time_to_str(new_time - last_time)} назад."
                time.sleep(1)
                self.account.raise_lots(subcat.category.id)
            except FunPayAPI.exceptions.RaiseError as e:
                if e.error_message is not None:
                    error_text = e.error_message
                if e.wait_time is not None:
                    logger.warning(_("crd_raise_time_err", subcat.category.name, error_text,
                                     cardinal_tools.time_to_str(e.wait_time)))
                    next_time = int(time.time()) + e.wait_time
                else:
                    logger.error(_("crd_raise_unexpected_err", subcat.category.name))
                    time.sleep(10)
                    next_time = int(time.time()) + 1
                self.raise_time[subcat.category.id] = next_time
                next_call = next_time if next_time < next_call else next_call
                if not raise_ok:
                    continue
            except Exception as e:
                t = 10
                if isinstance(e, FunPayAPI.exceptions.RequestFailedError) and e.status_code in (503, 403, 429):
                    logger.warning(_("crd_raise_status_code_err", e.status_code, subcat.category.name))
                    t = 60
                else:
                    logger.error(_("crd_raise_unexpected_err", subcat.category.name))
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(t)
                next_time = int(time.time()) + 1
                next_call = next_time if next_time < next_call else next_call
                if not raise_ok:
                    continue
            self.run_handlers(self.post_lots_raise_handlers, (self, subcat.category, error_text + time_delta))
        return next_call if next_call < float("inf") else 10

    def get_order_from_object(self, obj: types.OrderShortcut | types.Message | types.ChatShortcut,
                              order_id: str | None = None) -> None | types.Order:
        if obj._order_attempt_error:
            return
        if obj._order_attempt_made:
            while obj._order is None and not obj._order_attempt_error:
                time.sleep(0.1)
            return obj._order
        obj._order_attempt_made = True
        if type(obj) not in (types.Message, types.ChatShortcut, types.OrderShortcut):
            obj._order_attempt_error = True
            raise Exception("Неправильный тип объекта")
        if not order_id:
            if isinstance(obj, types.OrderShortcut):
                order_id = obj.id
                if order_id == "ADTEST":
                    obj._order_attempt_error = True
                    return
            elif isinstance(obj, types.Message) or isinstance(obj, types.ChatShortcut):
                order_id = fp_utils.RegularExpressions().ORDER_ID.findall(str(obj))
                if not order_id:
                    obj._order_attempt_error = True
                    return
                order_id = order_id[0][1:]
        for i in range(2, -1, -1):
            try:
                obj._order = self.account.get_order(order_id)
                logger.info(f"Получил информацию о заказе {obj._order}")  # locale
                return obj._order
            except:
                logger.warning(f"Произошла ошибка при получении заказа #{order_id}. Осталось {i} попыток.")  # locale
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(1)
        obj._order_attempt_error = True

    @staticmethod
    def split_text(text: str) -> list[str]:
        """
        Разбивает текст на суб-тексты по 20 строк.

        :param text: исходный текст.

        :return: список из суб-текстов.
        """
        output = []
        lines = text.split("\n")
        while lines:
            subtext = "\n".join(lines[:20])
            del lines[:20]
            if (strip := subtext.strip()) and strip != "[a][/a]":
                output.append(subtext)
        return output

    def parse_message_entities(self, msg_text: str) -> list[str | int | float]:
        """
        Разбивает сообщения по 20 строк, отделяет изображения от текста.
        (обозначение изображения: $photo=1234567890)

        :param msg_text: текст сообщения.

        :return: набор текстов сообщений / изображений.
        """
        msg_text = "\n".join(i.strip() for i in msg_text.split("\n"))
        while "\n\n" in msg_text:
            msg_text = msg_text.replace("\n\n", "\n[a][/a]\n")

        pos = 0
        entities = []
        while entity := cardinal_tools.ENTITY_RE.search(msg_text, pos=pos):
            if text := msg_text[pos:entity.span()[0]].strip():
                entities.extend(self.split_text(text))

            variable = msg_text[entity.span()[0]:entity.span()[1]]
            if variable.startswith("$photo"):
                entities.append(int(variable.split("=")[1]))
            elif variable.startswith("$sleep"):
                entities.append(float(variable.split("=")[1]))
            pos = entity.span()[1]
        else:
            if text := msg_text[pos:].strip():
                entities.extend(self.split_text(text))
        return entities

    def send_message(self, chat_id: int | str, message_text: str, chat_name: str | None = None,
                     interlocutor_id: int | None = None, attempts: int = 3,
                     watermark: bool = True) -> list[FunPayAPI.types.Message] | None:
        """
        Отправляет сообщение в чат FunPay.

        :param chat_id: ID чата.
        :param message_text: текст сообщения.
        :param chat_name: название чата (необязательно).
        :param interlocutor_id: ID собеседника (необязательно).
        :param attempts: кол-во попыток на отправку сообщения.
        :param watermark: добавлять ли водяной знак в начало сообщения?

        :return: объект сообщения / последнего сообщения, если оно доставлено, иначе - None
        """
        if self.MAIN_CFG["Other"].get("watermark") and watermark and not message_text.strip().startswith("$photo="):
            message_text = f"{self.MAIN_CFG['Other']['watermark']}\n" + message_text

        entities = self.parse_message_entities(message_text)
        if all(isinstance(i, float) for i in entities) or not entities:
            return

        result = []
        for entity in entities:
            current_attempts = attempts
            while current_attempts:
                try:
                    if isinstance(entity, str):
                        msg = self.account.send_message(chat_id, entity, chat_name,
                                                        interlocutor_id or self.account.interlocutor_ids.get(chat_id),
                                                        None, not self.old_mode_enabled,
                                                        self.old_mode_enabled,
                                                        self.keep_sent_messages_unread)
                        result.append(msg)
                        logger.info(_("crd_msg_sent", chat_id))
                    elif isinstance(entity, int):
                        msg = self.account.send_image(chat_id, entity, chat_name,
                                                      interlocutor_id or self.account.interlocutor_ids.get(chat_id),
                                                      not self.old_mode_enabled,
                                                      self.old_mode_enabled,
                                                      self.keep_sent_messages_unread)
                        result.append(msg)
                        logger.info(_("crd_msg_sent", chat_id))
                    elif isinstance(entity, float):
                        time.sleep(entity)
                    break
                except Exception as ex:
                    logger.warning(_("crd_msg_send_err", chat_id))
                    logger.debug("TRACEBACK", exc_info=True)
                    logger.info(_("crd_msg_attempts_left", current_attempts))
                    current_attempts -= 1
                    time.sleep(1)
            else:
                logger.error(_("crd_msg_no_more_attempts_err", chat_id))
                return []
        return result

    def get_exchange_rate(self, base_currency: types.Currency, target_currency: types.Currency, min_interval: int = 60):
        """
        Получает курс обмена между двумя указанными валютами.
        Если с последней проверки прошло меньше `min_interval` секунд, используется сохранённое значение.

        :param base_currency: Исходная валюта, из которой производится обмен.
        :type base_currency: :obj:`types.Currency`

        :param target_currency: Целевая валюта, в которую производится обмен.
        :type target_currency: :obj:`types.Currency`

        :param min_interval: Минимальное время в секундах между проверками курса обмена.
        :type min_interval: :obj:`int`

        :return: Коэффициент обмена, где 1 единица `base_currency` = X единиц `target_currency`.
        :rtype: :obj:`float`
        """
        assert base_currency != types.Currency.UNKNOWN and target_currency != types.Currency.UNKNOWN
        if base_currency == target_currency:
            return 1
        rate, t = self.__exchange_rates.get((base_currency, target_currency), (None, 0))
        if t and time.time() < t + min_interval:
            return rate
        for i in range(2, -1, -1):
            try:
                exchange_rate1, currency1 = self.account.get_exchange_rate(base_currency)
                self.__exchange_rates[(currency1, base_currency)] = (exchange_rate1, time.time())
                self.__exchange_rates[(base_currency, currency1)] = (1 / exchange_rate1, time.time())

                time.sleep(1)

                exchange_rate2, currency2 = self.account.get_exchange_rate(target_currency)
                self.__exchange_rates[(currency2, target_currency)] = (exchange_rate2, time.time())
                self.__exchange_rates[(target_currency, currency2)] = (1 / exchange_rate2, time.time())

                assert currency1 == currency2

                result = exchange_rate2 / exchange_rate1
                self.__exchange_rates[(base_currency, target_currency)] = (result, time.time())
                self.__exchange_rates[(target_currency, base_currency)] = (1 / result, time.time())

                return result
            except:
                logger.warning("Не удалось получить курс обмена. Осталось попыток: {i}")
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(1)

        raise Exception("Не удалось получить курс обмена: превышено количество попыток.")

    def update_session(self, attempts: int = 3) -> bool:
        """
        Обновляет данные аккаунта (баланс, токены и т.д.)

        :param attempts: кол-во попыток.

        :return: True, если удалось обновить данные, False - если нет.
        """
        while attempts:
            try:
                self.account.get(update_phpsessid=True)
                logger.info(_("crd_session_updated"))
                return True
            except TimeoutError:
                logger.warning(_("crd_session_timeout_err"))
            except (FunPayAPI.exceptions.UnauthorizedError, FunPayAPI.exceptions.RequestFailedError) as e:
                logger.error(e.short_str)
                logger.debug(e)
            except:
                logger.error(_("crd_session_unexpected_err"))
                logger.debug("TRACEBACK", exc_info=True)
            attempts -= 1
            logger.warning(_("crd_try_again_in_n_secs", 2))
            time.sleep(2)
        else:
            logger.error(_("crd_session_no_more_attempts_err"))
            return False

    # Бесконечные циклы
    def process_events(self):
        """
        Запускает хэндлеры, привязанные к тому или иному событию.
        """
        instance_id = self.run_id
        events_handlers = {
            FunPayAPI.events.EventTypes.INITIAL_CHAT: self.init_message_handlers,
            FunPayAPI.events.EventTypes.CHATS_LIST_CHANGED: self.messages_list_changed_handlers,
            FunPayAPI.events.EventTypes.LAST_CHAT_MESSAGE_CHANGED: self.last_chat_message_changed_handlers,
            FunPayAPI.events.EventTypes.NEW_MESSAGE: self.new_message_handlers,

            FunPayAPI.events.EventTypes.INITIAL_ORDER: self.init_order_handlers,
            FunPayAPI.events.EventTypes.ORDERS_LIST_CHANGED: self.orders_list_changed_handlers,
            FunPayAPI.events.EventTypes.NEW_ORDER: self.new_order_handlers,
            FunPayAPI.events.EventTypes.ORDER_STATUS_CHANGED: self.order_status_changed_handlers,
        }

        for event in self.runner.listen(requests_delay=int(self.MAIN_CFG["Other"]["requestsDelay"])):
            if instance_id != self.run_id:
                break
            self.run_handlers(events_handlers[event.type], (self, event))

    def lots_raise_loop(self):
        """
        Запускает бесконечный цикл поднятия категорий (если autoRaise в _main.cfg == 1)
        """
        if not self.profile.get_lots():
            logger.info(_("crd_raise_loop_not_started"))
            return

        logger.info(_("crd_raise_loop_started"))
        while True:
            try:
                if not self.MAIN_CFG["FunPay"].getboolean("autoRaise"):
                    time.sleep(10)
                    continue
                next_time = self.raise_lots()
                delay = next_time - int(time.time())
                if delay <= 0:
                    continue
                time.sleep(delay)
            except:
                logger.debug("TRACEBACK", exc_info=True)

    def update_session_loop(self):
        """
        Запускает бесконечный цикл обновления данных о пользователе.
        """
        logger.info(_("crd_session_loop_started"))
        sleep_time = 3600
        while True:
            time.sleep(sleep_time)
            result = self.update_session()
            sleep_time = 60 if not result else 3600

    # Управление процессом
    def init(self):
        """
        Инициализирует кардинал: регистрирует хэндлеры, инициализирует и запускает Telegram бота,
        получает данные аккаунта и профиля.
        """
        self.add_handlers_from_plugin(handlers)
        self.add_handlers_from_plugin(announcements)
        self.load_plugins()
        self.add_handlers()

        if self.MAIN_CFG["Telegram"].getboolean("enabled"):
            self.__init_telegram()
            for module in [auto_response_cp, auto_delivery_cp, config_loader_cp, templates_cp, plugins_cp,
                           file_uploader, authorized_users_cp, proxy_cp, default_cp]:
                self.add_handlers_from_plugin(module)

        self.run_handlers(self.pre_init_handlers, (self,))

        if self.MAIN_CFG["Telegram"].getboolean("enabled"):
            self.telegram.setup_commands()
            try:
                self.telegram.edit_bot()
            except AttributeError:  # todo убрать когда-то
                logger.warning("Произошла ошибка при изменении бота Telegram. Обновляю библиотеку...")
                logger.debug("TRACEBACK", exc_info=True)
                try:
                    main(["install", "-U", "pytelegrambotapi==4.15.2"])
                    logger.info("Библиотека обновлена.")
                except:
                    logger.warning("Произошла ошибка при обновлении библиотеки.")
                    logger.debug("TRACEBACK", exc_info=True)
            except:
                logger.warning("Произошла ошибка при изменении бота Telegram.")
                logger.debug("TRACEBACK", exc_info=True)

            Thread(target=self.telegram.run, daemon=True).start()

        self.__init_account()
        self.runner = FunPayAPI.Runner(self.account, self.old_mode_enabled)
        self.__update_profile()
        self.run_handlers(self.post_init_handlers, (self,))
        return self

    def run(self):
        """
        Запускает кардинал после инициализации. Используется для первого старта.
        """
        self.run_id += 1
        self.start_time = int(time.time())
        self.run_handlers(self.pre_start_handlers, (self,))
        self.run_handlers(self.post_start_handlers, (self,))

        Thread(target=self.lots_raise_loop, daemon=True).start()
        Thread(target=self.update_session_loop, daemon=True).start()
        self.process_events()

    def start(self):
        """
        Запускает кардинал после остановки. Не используется.
        """
        self.run_id += 1
        self.run_handlers(self.pre_start_handlers, (self,))
        self.run_handlers(self.post_start_handlers, (self,))
        self.process_events()

    def stop(self):
        """
        Останавливает кардинал. Не используется.
        """
        self.run_id += 1
        self.run_handlers(self.pre_stop_handlers, (self,))
        self.run_handlers(self.post_stop_handlers, (self,))

    def update_lots_and_categories(self):
        """
        Парсит лоты (для ПУ TG).
        """
        result = self.__update_profile(infinite_polling=False, attempts=3, update_main_profile=False)
        return result

    def switch_msg_get_mode(self):
        self.MAIN_CFG["FunPay"]["oldMsgGetMode"] = str(int(not self.old_mode_enabled))
        self.save_config(self.MAIN_CFG, "configs/_main.cfg")
        if not self.runner:
            return
        if not self.old_mode_enabled:
            self.runner.last_messages_ids = {k: v[0] for k, v in self.runner.runner_last_messages.items()}
        self.runner.make_msg_requests = False if self.old_mode_enabled else True
        if self.old_mode_enabled:
            self.runner.last_messages_ids = {}
            self.runner.by_bot_ids = {}

    @staticmethod
    def save_config(config: configparser.ConfigParser, file_path: str) -> None:
        """
        Сохраняет конфиг в указанный файл.

        :param config: объект конфига.
        :param file_path: путь до файла, в который нужно сохранить конфиг.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            config.write(f)

    # Загрузка плагинов
    @staticmethod
    def is_uuid_valid(uuid: str) -> bool:
        """
        Проверяет, является ли UUID плагина валидным.
        :param uuid: UUID4.
        """
        try:
            uuid_obj = UUID(uuid, version=4)
        except ValueError:
            return False
        return str(uuid_obj) == uuid

    @staticmethod
    def is_plugin(file: str) -> bool:
        """
        Есть ли "noplug" в начале файла плагина?

        :param file: файл плагина.
        """
        with open(f"plugins/{file}", "r", encoding="utf-8") as f:
            line = f.readline()
        if line.startswith("#"):
            line = line.replace("\n", "")
            args = line.split()
            if "noplug" in args:
                return False
        return True

    @staticmethod
    def load_plugin(from_file: str) -> tuple:
        """
        Создает модуль из переданного файла-плагина и получает необходимые поля для PluginData.
        :param from_file: путь до файла-плагина.

        :return: плагин, поля плагина.
        """
        spec = importlib.util.spec_from_file_location(f"plugins.{from_file[:-3]}", f"plugins/{from_file}")
        plugin = importlib.util.module_from_spec(spec)
        sys.modules[f"plugins.{from_file[:-3]}"] = plugin
        spec.loader.exec_module(plugin)

        fields = ["NAME", "VERSION", "DESCRIPTION", "CREDITS", "SETTINGS_PAGE", "UUID", "BIND_TO_DELETE"]
        result = {}

        for i in fields:
            try:
                value = getattr(plugin, i)
            except AttributeError:
                raise Utils.exceptions.FieldNotExistsError(i, from_file)
            result[i] = value
        return plugin, result

    def load_plugins(self):
        """
        Импортирует все плагины из папки plugins.
        """
        if not os.path.exists("plugins"):
            logger.warning(_("crd_no_plugins_folder"))
            return
        plugins = [file for file in os.listdir("plugins") if file.endswith(".py")]
        if not plugins:
            logger.info(_("crd_no_plugins"))
            return

        sys.path.append("plugins")
        for file in plugins:
            try:
                if not self.is_plugin(file):
                    continue
                plugin, data = self.load_plugin(file)
            except:
                logger.error(_("crd_plugin_load_err", file))
                logger.debug("TRACEBACK", exc_info=True)
                continue

            if not self.is_uuid_valid(data["UUID"]):
                logger.error(_("crd_invalid_uuid", file))
                continue

            if data["UUID"] in self.plugins:
                logger.error(_("crd_uuid_already_registered", data['UUID'], data['NAME']))
                continue

            plugin_data = PluginData(data["NAME"], data["VERSION"], data["DESCRIPTION"], data["CREDITS"], data["UUID"],
                                     f"plugins/{file}", plugin, data["SETTINGS_PAGE"], data["BIND_TO_DELETE"],
                                     False if data["UUID"] in self.disabled_plugins else True)

            self.plugins[data["UUID"]] = plugin_data

    def add_handlers_from_plugin(self, plugin, uuid: str | None = None):
        """
        Добавляет хэндлеры из плагина + присваивает каждому хэндлеру UUID плагина.

        :param plugin: модуль (плагин).
        :param uuid: UUID плагина (None для встроенных хэндлеров).
        """
        for name in self.handler_bind_var_names:
            try:
                functions = getattr(plugin, name)
            except AttributeError:
                continue
            for func in functions:
                func.plugin_uuid = uuid
            self.handler_bind_var_names[name].extend(functions)
        logger.info(_("crd_handlers_registered", plugin.__name__))

    def add_handlers(self):
        """
        Регистрирует хэндлеры из всех плагинов.
        """
        for i in self.plugins:
            plugin = self.plugins[i].plugin
            self.add_handlers_from_plugin(plugin, i)

    def run_handlers(self, handlers_list: list[Callable], args) -> None:
        """
        Выполняет функции из списка handlers.

        :param handlers_list: Список хэндлеров.
        :param args: аргументы для хэндлеров.
        """
        for func in handlers_list:
            try:
                plugin_uuid = getattr(func, "plugin_uuid")
                if plugin_uuid is None or (plugin_uuid in self.plugins and self.plugins[plugin_uuid].enabled):
                    func(*args)
            except Exception as ex:
                text = _("crd_handler_err")
                try:
                    text += f" {ex.short_str()}"
                except:
                    pass
                logger.error(text)
                logger.debug("TRACEBACK", exc_info=True)
                continue

    def add_telegram_commands(self, uuid: str, commands: list[tuple[str, str, bool]]):
        """
        Добавляет команды в список команд плагина.
        [
            ("команда1", "описание команды", Добавлять ли в меню команд (True / False)),
            ("команда2", "описание команды", Добавлять ли в меню команд (True / False))
        ]

        :param uuid: UUID плагина.
        :param commands: список команд (без "/")
        """
        if uuid not in self.plugins:
            return

        for i in commands:
            self.plugins[uuid].commands[i[0]] = i[1]
            if i[2] and self.telegram:
                self.telegram.add_command_to_menu(i[0], i[1])

    def toggle_plugin(self, uuid):
        """
        Активирует / деактивирует плагин.
        :param uuid: UUID плагина.
        """
        self.plugins[uuid].enabled = not self.plugins[uuid].enabled
        if self.plugins[uuid].enabled and uuid in self.disabled_plugins:
            self.disabled_plugins.remove(uuid)
        elif not self.plugins[uuid].enabled and uuid not in self.disabled_plugins:
            self.disabled_plugins.append(uuid)
        cardinal_tools.cache_disabled_plugins(self.disabled_plugins)

    # Настройки
    @property
    def autoraise_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("autoRaise")

    @property
    def autoresponse_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("autoResponse")

    @property
    def autodelivery_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("autoDelivery")

    @property
    def multidelivery_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("multiDelivery")

    @property
    def autorestore_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("autoRestore")

    @property
    def autodisable_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("autoDisable")

    @property
    def old_mode_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("oldMsgGetMode")

    @property
    def keep_sent_messages_unread(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("keepSentMessagesUnread")

    @property
    def show_image_name(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("showImageName")

    @property
    def bl_delivery_enabled(self) -> bool:
        return self.MAIN_CFG["BlockList"].getboolean("blockDelivery")

    @property
    def bl_response_enabled(self) -> bool:
        return self.MAIN_CFG["BlockList"].getboolean("blockResponse")

    @property
    def bl_msg_notification_enabled(self) -> bool:
        return self.MAIN_CFG["BlockList"].getboolean("blockNewMessageNotification")

    @property
    def bl_order_notification_enabled(self) -> bool:
        return self.MAIN_CFG["BlockList"].getboolean("blockNewOrderNotification")

    @property
    def bl_cmd_notification_enabled(self) -> bool:
        return self.MAIN_CFG["BlockList"].getboolean("blockCommandNotification")

    @property
    def include_my_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("includeMyMessages")

    @property
    def include_fp_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("includeFPMessages")

    @property
    def include_bot_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("includeBotMessages")

    @property
    def only_my_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("notifyOnlyMyMessages")

    @property
    def only_fp_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("notifyOnlyFPMessages")

    @property
    def only_bot_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("notifyOnlyBotMessages")

    @property
    def block_tg_login(self) -> bool:
        return self.MAIN_CFG["Telegram"].getboolean("blockLogin")
