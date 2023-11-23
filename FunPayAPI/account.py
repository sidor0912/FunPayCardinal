from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Any, Optional, IO
if TYPE_CHECKING:
    from .updater.runner import Runner

from requests_toolbelt import MultipartEncoder
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import logging
import random
import string
import json
import time
import re

from . import types
from .common import exceptions, utils, enums


logger = logging.getLogger("FunPayAPI.account")
PRIVATE_CHAT_ID_RE = re.compile(r"users-\d+-\d+$")


class Account:
    """
    Класс для управления аккаунтом FunPay.

    :param golden_key: токен (golden_key) аккаунта.
    :type golden_key: :obj:`str`

    :param user_agent: user-agent браузера, с которого был произведен вход в аккаунт.
    :type user_agent: :obj:`str`

    :param requests_timeout: тайм-аут ожидания ответа на запросы.
    :type requests_timeout: :obj:`int` or :obj:`float`

    :param proxy: прокси для запросов.
    :type proxy: :obj:`dict` {:obj:`str`: :obj:`str` or :obj:`None`
    """
    def __init__(self, golden_key: str, user_agent: str | None = None,
                 requests_timeout: int | float = 10, proxy: Optional[dict] = None):
        self.golden_key: str = golden_key
        """Токен (golden_key) аккаунта."""
        self.user_agent: str | None = user_agent
        """User-agent браузера, с которого был произведен вход в аккаунт."""
        self.requests_timeout: int | float = requests_timeout
        """Тайм-аут ожидания ответа на запросы."""
        self.proxy = proxy

        self.html: str | None = None
        """HTML основной страницы FunPay."""
        self.app_data: dict | None = None
        """Appdata."""
        self.id: int | None = None
        """ID аккаунта."""
        self.username: str | None = None
        """Никнейм аккаунта."""
        self.active_sales: int | None = None
        """Активные продажи."""
        self.active_purchases: int | None = None
        """Активные покупки."""

        self.csrf_token: str | None = None
        """CSRF токен."""
        self.phpsessid: str | None = None
        """PHPSESSID сессии."""
        self.last_update: int | None = None
        """Последнее время обновления аккаунта."""

        self.__initiated: bool = False

        self.__saved_chats: dict[int, types.ChatShortcut] = {}
        self.runner: Runner | None = None
        """Объект Runner'а."""

        self.__categories: list[types.Category] = []
        self.__sorted_categories: dict[int, types.Category] = {}

        self.__subcategories: list[types.SubCategory] = []
        self.__sorted_subcategories: dict[types.SubCategoryTypes, dict[int, types.SubCategory]] = {
            types.SubCategoryTypes.COMMON: {},
            types.SubCategoryTypes.CURRENCY: {}
        }

        self.__bot_character = "⁤"
        """Если сообщение начинается с этого символа, значит оно отправлено ботом."""

    def method(self, request_method: Literal["post", "get"], api_method: str, headers: dict, payload: Any,
               exclude_phpsessid: bool = False, raise_not_200: bool = False) -> requests.Response:
        """
        Отправляет запрос к FunPay. Добавляет в заголовки запроса user_agent и куки.

        :param request_method: метод запроса ("get" / "post").
        :type request_method: :obj:`str` `post` or `get`

        :param api_method: метод API / полная ссылка.
        :type api_method: :obj:`str`

        :param headers: заголовки запроса.
        :type headers: :obj:`dict`

        :param payload: полезная нагрузка.
        :type payload: :obj:`dict`

        :param exclude_phpsessid: исключить ли PHPSESSID из добавляемых куки?
        :type exclude_phpsessid: :obj:`bool`

        :param raise_not_200: возбуждать ли исключение, если статус код ответа != 200?
        :type raise_not_200: :obj:`bool`

        :return: объект ответа.
        :rtype: :class:`requests.Response`
        """
        headers["cookie"] = f"golden_key={self.golden_key}"
        headers["cookie"] += f"; PHPSESSID={self.phpsessid}" if self.phpsessid and not exclude_phpsessid else ""
        if self.user_agent:
            headers["user-agent"] = self.user_agent
        link = api_method if api_method.startswith("https://funpay.com") else "https://funpay.com/" + api_method
        response = getattr(requests, request_method)(link, headers=headers, data=payload, timeout=self.requests_timeout,
                                                     proxies=self.proxy or {})

        if response.status_code == 403:
            raise exceptions.UnauthorizedError(response)
        elif response.status_code != 200 and raise_not_200:
            raise exceptions.RequestFailedError(response)
        return response

    def get(self, update_phpsessid: bool = False) -> Account:
        """
        Получает / обновляет данные об аккаунте. Необходимо вызывать каждые 40-60 минут, дабы обновить
        :py:obj:`.Account.phpsessid`.

        :param update_phpsessid: обновить :py:obj:`.Account.phpsessid` или использовать старый.
        :type update_phpsessid: :obj:`bool`, опционально

        :return: объект аккаунта с обновленными данными.
        :rtype: :class:`FunPayAPI.account.Account`
        """
        response = self.method("get", "https://funpay.com", {}, {}, update_phpsessid, raise_not_200=True)

        html_response = response.content.decode()
        parser = BeautifulSoup(html_response, "html.parser")

        username = parser.find("div", {"class": "user-link-name"})
        if not username:
            raise exceptions.UnauthorizedError(response)

        self.username = username.text
        self.app_data = json.loads(parser.find("body").get("data-app-data"))
        self.id = self.app_data["userId"]
        self.csrf_token = self.app_data["csrf-token"]

        active_sales = parser.find("span", {"class": "badge badge-trade"})
        self.active_sales = int(active_sales.text) if active_sales else 0

        active_purchases = parser.find("span", {"class": "badge badge-orders"})
        self.active_purchases = int(active_purchases.text) if active_purchases else 0

        cookies = response.cookies.get_dict()
        if update_phpsessid or not self.phpsessid:
            self.phpsessid = cookies["PHPSESSID"]
        if not self.is_initiated:
            self.__setup_categories(html_response)

        self.last_update = int(time.time())
        self.html = html_response
        self.__initiated = True
        return self

    def get_subcategory_public_lots(self, subcategory_type: enums.SubCategoryTypes, subcategory_id: int) -> list[types.LotShortcut]:
        """
        Получает список всех опубликованных лотов переданной подкатегории.

        :param subcategory_type: тип подкатегории.
        :type subcategory_type: :class:`FunPayAPI.enums.SubCategoryTypes`

        :param subcategory_id: ID подкатегории.
        :type subcategory_id: :obj:`int`

        :return: список всех опубликованных лотов переданной подкатегории.
        :rtype: :obj:`list` of :class:`FunPayAPI.types.LotShortcut`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        meth = f"lots/{subcategory_id}/" if subcategory_type is enums.SubCategoryTypes.COMMON else f"chips/{subcategory_id}/"
        response = self.method("get", meth, {"accept": "*/*"}, {}, raise_not_200=True)
        html_response = response.content.decode()
        parser = BeautifulSoup(html_response, "html.parser")

        username = parser.find("div", {"class": "user-link-name"})
        if not username:
            raise exceptions.UnauthorizedError(response)

        offers = parser.find_all("a", {"class": "tc-item"})
        if not offers:
            return []

        subcategory_obj = self.get_subcategory(subcategory_type, subcategory_id)
        result = []
        for offer in offers:
            offer_id = offer["href"].split("id=")[1]
            description = offer.find("div", {"class": "tc-desc-text"})
            description = description.text if description else None
            server = offer.find("div", {"class": "tc-server hidden-xxs"})
            if not server:
                server = offer.find("div", {"class": "tc-server hidden-xs"})
            server = server.text if server else None

            if subcategory_type is types.SubCategoryTypes.COMMON:
                price = float(offer.find("div", {"class": "tc-price"})["data-s"])
            else:
                price = float(offer.find("div", {"class": "tc-price"}).find("div").text.split()[0])
            lot_obj = types.LotShortcut(offer_id, server, description, price, subcategory_obj, str(offer))
            result.append(lot_obj)
        return result

    def get_balance(self, lot_id: int = 20978354) -> types.Balance:
        """
        Получает информацию о балансе пользователя.

        :param lot_id: ID лота, на котором проверять баланс.
        :type lot_id: :obj:`int`, опционально

        :return: информацию о балансе пользователя.
        :rtype: :class:`FunPayAPI.types.Balance`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()
        response = self.method("get", f"lots/offer?id={lot_id}", {"accept": "*/*"}, {}, raise_not_200=True)
        html_response = response.content.decode()
        parser = BeautifulSoup(html_response, "html.parser")

        username = parser.find("div", {"class": "user-link-name"})
        if not username:
            raise exceptions.UnauthorizedError(response)

        balances = parser.find("select", {"name": "method"})
        balance = types.Balance(float(balances["data-balance-total-rub"]), float(balances["data-balance-rub"]),
                                float(balances["data-balance-total-usd"]), float(balances["data-balance-usd"]),
                                float(balances["data-balance-total-eur"]), float(balances["data-balance-eur"]))
        return balance

    def get_chat_history(self, chat_id: int | str, last_message_id: int = 99999999999999999999999,
                         interlocutor_username: Optional[str] = None, from_id: int = 0) -> list[types.Message]:
        """
        Получает историю указанного чата (до 100 последних сообщений).

        :param chat_id: ID чата (или его текстовое обозначение).
        :type chat_id: :obj:`int` or :obj:`str`

        :param last_message_id: ID сообщения, с которого начинать историю (фильтр FunPay).
        :type last_message_id: :obj:`int`

        :param interlocutor_username: никнейм собеседника. Не нужно указывать для получения истории публичного чата.
            Так же не обязательно, но желательно указывать для получения истории личного чата.
        :type interlocutor_username: :obj:`str` or :obj:`None`, опционально.

        :param from_id: все сообщения с ID < переданного не попадут в возвращаемый список сообщений.
        :type from_id: :obj:`int`, опционально.

        :return: история указанного чата.
        :rtype: :obj:`list` of :class:`FunPayAPI.types.Message`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        headers = {
            "accept": "*/*",
            "x-requested-with": "XMLHttpRequest"
        }
        payload = {
            "node": chat_id,
            "last_message": last_message_id
        }
        response = self.method("get", f"chat/history?node={chat_id}&last_message={last_message_id}",
                               headers, payload, raise_not_200=True)

        json_response = response.json()
        if not json_response.get("chat") or not json_response["chat"].get("messages"):
            return []
        if isinstance(chat_id, int):
            interlocutor_id = int(json_response["chat"]["node"]["name"].split("-")[2])
        else:
            interlocutor_id = None
        return self.__parse_messages(json_response["chat"]["messages"], chat_id, interlocutor_id,
                                     interlocutor_username, from_id)

    def get_chats_histories(self, chats_data: dict[int | str, str | None]) -> dict[int, list[types.Message]]:
        """
        Получает историю сообщений сразу нескольких чатов
        (до 50 сообщений на личный чат, до 25 сообщений на публичный чат).

        :param chats_data: ID чатов и никнеймы собеседников (None, если никнейм неизвестен)\n
            Например: {48392847: "SLLMK", 58392098: "Amongus", 38948728: None}
        :type chats_data: :obj:`dict` {:obj:`int` or :obj:`str`: :obj:`str` or :obj:`None`}

        :return: словарь с историями чатов в формате {ID чата: [список сообщений]}
        :rtype: :obj:`dict` {:obj:`int`: :obj:`list` of :class:`FunPayAPI.types.Message`}
        """
        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest"
        }
        objects = [{"type": "chat_node", "id": i, "tag": "00000000",
                    "data": {"node": i, "last_message": -1, "content": ""}} for i in chats_data]
        payload = {
            "objects": json.dumps(objects),
            "request": False,
            "csrf_token": self.csrf_token
        }
        response = self.method("post", "runner/", headers, payload, raise_not_200=True)
        json_response = response.json()

        result = {}
        for i in json_response["objects"]:
            if not i.get("data"):
                result[i.get("id")] = []
                continue
            if isinstance(i.get("id"), int):
                interlocutor_id = int(i["data"]["node"]["name"].split("-")[2])
                interlocutor_name = chats_data[i.get("id")]
            else:
                interlocutor_id = None
                interlocutor_name = None
            messages = self.__parse_messages(i["data"]["messages"], i.get("id"), interlocutor_id, interlocutor_name)
            result[i.get("id")] = messages
        return result

    def upload_image(self, image: str | IO[bytes]) -> int:
        """
        Выгружает изображение на сервер FunPay для дальнейшей отправки в качестве сообщения.
        Для отправки изображения в чат рекомендуется использовать метод :meth:`FunPayAPI.account.Account.send_image`.

        :param image: путь до изображения или представление изображения в виде байтов.
        :type image: :obj:`str` or :obj:`bytes`

        :return: ID изображения на серверах FunPay.
        :rtype: :obj:`int`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        if isinstance(image, str):
            with open(image, "rb") as f:
                img = f.read()
        else:
            img = image

        fields = {
            'file': ("funpay_cardinal_image.png", img, "image/png"),
            'file_id': "0"
        }
        boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
        m = MultipartEncoder(fields=fields, boundary=boundary)

        headers = {
            "accept": "*/*",
            "x-requested-with": "XMLHttpRequest",
            "content-type": m.content_type,
        }

        response = self.method("post", "file/addChatImage", headers, m)

        if response.status_code == 400:
            try:
                json_response = response.json()
                message = json_response.get("msg")
                raise exceptions.ImageUploadError(response, message)
            except requests.exceptions.JSONDecodeError:
                raise exceptions.ImageUploadError(response, None)
        elif response.status_code != 200:
            raise exceptions.RequestFailedError(response)

        if not (document_id := response.json().get("fileId")):
            raise exceptions.ImageUploadError(response, None)
        return int(document_id)

    def send_message(self, chat_id: int | str, text: Optional[str] = None, chat_name: Optional[str] = None,
                     image_id: Optional[int] = None, add_to_ignore_list: bool = True,
                     update_last_saved_message: bool = False) -> types.Message:
        """
        Отправляет сообщение в чат.

        :param chat_id: ID чата.
        :type chat_id: :obj:`int` or :obj:`str`

        :param text: текст сообщения.
        :type text: :obj:`str` or :obj:`None`, опционально

        :param chat_name: название чата (для возвращаемого объекта сообщения) (не нужно для отправки сообщения в публичный чат).
        :type chat_name: :obj:`str` or :obj:`None`, опционально

        :param image_id: ID изображения. Доступно только для личных чатов.
        :type image_id: :obj:`int` or :obj:`None`, опционально

        :param add_to_ignore_list: добавлять ли ID отправленного сообщения в игнорируемый список Runner'а?
        :type add_to_ignore_list: :obj:`bool`, опционально

        :param update_last_saved_message: обновлять ли последнее сохраненное сообщение на отправленное в Runner'е?
        :type update_last_saved_message: :obj:`bool`, опционально.

        :return: экземпляр отправленного сообщения.
        :rtype: :class:`FunPayAPI.types.Message`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest"
        }
        request = {
            "action": "chat_message",
            "data": {"node": chat_id, "last_message": -1, "content": text}
        }

        if image_id is not None:
            request["data"]["image_id"] = image_id
            request["data"]["content"] = ""
        else:
            request["data"]["content"] = f"{self.__bot_character}{text}" if text else ""

        objects = [
            {
                "type": "chat_node",
                "id": chat_id,
                "tag": "00000000",
                "data": {"node": chat_id, "last_message": -1, "content": ""}
            }
        ]
        payload = {
            "objects": json.dumps(objects),
            "request": json.dumps(request),
            "csrf_token": self.csrf_token
        }

        response = self.method("post", "runner/", headers, payload, raise_not_200=True)
        json_response = response.json()
        if not (resp := json_response.get("response")):
            raise exceptions.MessageNotDeliveredError(response, None, chat_id)

        if (error_text := resp.get("error")) is not None:
            raise exceptions.MessageNotDeliveredError(response, error_text, chat_id)

        mes = json_response["objects"][0]["data"]["messages"][-1]
        parser = BeautifulSoup(mes["html"], "html.parser")
        try:
            if image_link := parser.find("a", {"class": "chat-img-link"}):
                image_link = image_link.get("href")
                message_text = None
            else:
                message_text = parser.find("div", {"class": "message-text"}).text.replace(self.__bot_character, "", 1)
        except Exception as e:
            logger.debug("SEND_MESSAGE RESPONSE")
            logger.debug(response.content.decode())
            raise e

        message_obj = types.Message(int(mes["id"]), message_text, chat_id, chat_name, self.username, self.id,
                                    mes["html"], image_link)
        if self.runner and isinstance(chat_id, int):
            if add_to_ignore_list:
                self.runner.mark_as_by_bot(chat_id, message_obj.id)
            if update_last_saved_message:
                self.runner.update_last_message(chat_id, message_text)
        return message_obj

    def send_image(self, chat_id: int, image: int | str | IO[bytes], chat_name: Optional[str] = None,
                   add_to_ignore_list: bool = True, update_last_saved_message: bool = False) -> types.Message:
        """
        Отправляет изображение в чат. Доступно только для личных чатов.

        :param chat_id: ID чата.
        :type chat_id: :obj:`int`

        :param image: ID изображения / путь до изображения / изображение в виде байтов.
            Если передан путь до изображения или представление изображения в виде байтов, сначала оно будет выгружено
            с помощью метода :meth:`FunPayAPI.account.Account.upload_image`.
        :type image: :obj:`int` or :obj:`str` or :obj:`bytes`

        :param chat_name: Название чата (никнейм собеседника). Нужен для возвращаемого объекта.
        :type chat_name: :obj:`str` or :obj:`None`, опционально

        :param add_to_ignore_list: добавлять ли ID отправленного сообщения в игнорируемый список Runner'а?
        :type add_to_ignore_list: :obj:`bool`, опционально

        :param update_last_saved_message: обновлять ли последнее сохраненное сообщение на отправленное в Runner'е?
        :type update_last_saved_message: :obj:`bool`, опционально

        :return: объект отправленного сообщения.
        :rtype: :class:`FunPayAPI.types.Message`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        if not isinstance(image, int):
            image = self.upload_image(image)
        result = self.send_message(chat_id, None, chat_name, image, add_to_ignore_list, update_last_saved_message)
        return result

    def send_review(self, order_id: str, text: str, rating: Literal[1, 2, 3, 4, 5] = 5) -> str:
        """
        Отправляет / редактирует отзыв / ответ на отзыв.

        :param order_id: ID заказа.
        :type order_id: :obj:`str`

        :param text: текст отзыва.
        :type text: :obj:`str`

        :param rating: рейтинг (от 1 до 5).
        :type rating: :obj:`int`, опционально

        :return: ответ FunPay (HTML-код блока отзыва).
        :rtype: :obj:`str`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        headers = {
            "accept": "*/*",
            "x-requested-with": "XMLHttpRequest"
        }
        payload = {
            "authorId": self.id,
            "text": text,
            "rating": rating,
            "csrf_token": self.csrf_token,
            "orderId": order_id
        }

        response = self.method("post", "orders/review", headers, payload)
        if response.status_code == 400:
            json_response = response.json()
            msg = json_response.get("msg")
            raise exceptions.FeedbackEditingError(response, msg, order_id)
        elif response.status_code != 200:
            raise exceptions.RequestFailedError(response)

        return response.json().get("content")

    def delete_review(self, order_id: str) -> str:
        """
        Удаляет отзыв / ответ на отзыв.

        :param order_id: ID заказа.
        :type order_id: :obj:`str`

        :return: ответ FunPay (HTML-код блока отзыва).
        :rtype: :obj:`str`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        headers = {
            "accept": "*/*",
            "x-requested-with": "XMLHttpRequest"
        }
        payload = {
            "authorId": self.id,
            "csrf_token": self.csrf_token,
            "orderId": order_id
        }

        response = self.method("post", "orders/reviewDelete", headers, payload)

        if response.status_code == 400:
            json_response = response.json()
            msg = json_response.get("msg")
            raise exceptions.FeedbackEditingError(response, msg, order_id)
        elif response.status_code != 200:
            raise exceptions.RequestFailedError(response)

        return response.json().get("content")

    def refund(self, order_id):
        """
        Оформляет возврат средств за заказ.

        :param order_id: ID заказа.
        :type order_id: :obj:`str`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
        }

        payload = {
            "id": order_id,
            "csrf_token": self.csrf_token
        }

        response = self.method("post", "orders/refund", headers, payload, raise_not_200=True)

        if response.json().get("error"):
            raise exceptions.RefundError(response, response.json().get("msg"), order_id)

    def withdraw(self, currency: enums.Currency, wallet: enums.Wallet, amount: int | float, address: str) -> float:
        """
        Отправляет запрос на вывод средств.

        :param currency: валюта.
        :type currency: :class:`FunPayAPI.common.enums.Currency`

        :param wallet: тип кошелька.
        :type wallet: :class:`FunPayAPI.common.enums.Wallet`

        :param amount: кол-во средств.
        :type amount: :obj:`int` or :obj:`float`

        :param address: адрес кошелька.
        :type address: :obj:`str`

        :return: кол-во выведенных средств с учетом комиссии FunPay.
        :rtype: :obj:`float`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        currencies = {
            enums.Currency.RUB: "rub",
            enums.Currency.USD: "usd",
            enums.Currency.EUR: "eur"
        }

        wallets = {
            enums.Wallet.QIWI: "qiwi",
            enums.Wallet.YOUMONEY: "fps",
            enums.Wallet.BINANCE: "binance",
            enums.Wallet.TRC: "usdt_trc",
            enums.Wallet.CARD_RUB: "card_rub",
            enums.Wallet.CARD_USD: "card_usd",
            enums.Wallet.CARD_EUR: "card_eur",
            enums.Wallet.WEBMONEY: "wmz"
        }
        headers = {
            "accept": "*/*",
            "x-requested-with": "XMLHttpRequest"
        }
        payload = {
            "csrf_token": self.csrf_token,
            "currency_id": currencies[currency],
            "ext_currency_id": wallets[wallet],
            "wallet": address,
            "amount_int": str(amount)
        }
        response = self.method("post", "withdraw/withdraw", headers, payload, raise_not_200=True)
        json_response = response.json()
        if json_response.get("error"):
            error_message = json_response.get("msg")
            raise exceptions.WithdrawError(response, error_message)
        return float(json_response.get("amount_ext"))

    def get_raise_modal(self, category_id: int) -> dict:
        """
        Отправляет запрос на получение modal-формы для поднятия лотов категории (игры).
        !ВНИМАНИЕ! Если на аккаунте только 1 подкатегория, относящаяся переданной категории (игре),
        то FunPay поднимет лоты данной подкатегории без отправления modal-формы с выбором других подкатегорий.

        :param category_id: ID категории (игры).
        :type category_id: :obj:`int`

        :return: ответ FunPay.
        :rtype: :obj:`dict`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()
        category = self.get_category(category_id)
        subcategory = category.get_subcategories()[0]
        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest"
        }
        payload = {
            "game_id": category_id,
            "node_id": subcategory.id
        }
        response = self.method("post", "https://funpay.com/lots/raise", headers, payload, raise_not_200=True)
        json_response = response.json()
        return json_response

    def raise_lots(self, category_id: int, subcategories: Optional[list[int | types.SubCategory]] = None,
                   exclude: list[int] | None = None) -> bool:
        """
        Поднимает все лоты всех подкатегорий переданной категории (игры).

        :param category_id: ID категории (игры).
        :type category_id: :obj:`int`

        :param subcategories: список подкатегорий, которые необходимо поднять. Если не указаны, поднимутся все
            подкатегории переданной категории.
        :type subcategories: :obj:`list` of :obj:`int` or :class:`FunPayAPI.types.SubCategory`

        :param exclude: ID подкатегорий, которые не нужно поднимать.
        :type exclude: :obj:`list` of :obj:`int`, опционально.

        :return: `True`
        :rtype: :obj:`bool`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()
        if not (category := self.get_category(category_id)):
            raise Exception("Not Found")  # todo

        exclude = exclude or []
        if subcategories:
            subcats = []
            for i in subcategories:
                if isinstance(i, types.SubCategory):
                    if i.type is types.SubCategoryTypes.COMMON and i.category.id == category.id and i.id not in exclude:
                        subcats.append(i)
                else:
                    if not (subcat := category.get_subcategory(types.SubCategoryTypes.COMMON, i)):
                        continue
                    subcats.append(subcat)
        else:
            subcats = [i for i in category.get_subcategories() if i.type is types.SubCategoryTypes.COMMON and i.id not in exclude]

        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest"
        }
        payload = {
            "game_id": category_id,
            "node_id": subcats[0].id,
            "node_ids[]": [i.id for i in subcats]
        }

        response = self.method("post", "lots/raise", headers, payload, raise_not_200=True)
        json_response = response.json()
        logger.debug(f"Ответ FunPay (поднятие категорий): {json_response}.")
        if not json_response.get("error"):
            return True
        elif json_response.get("error") and json_response.get("msg") and "Подождите" in json_response.get("msg"):
            wait_time = utils.parse_wait_time(json_response.get("msg"))
            raise exceptions.RaiseError(response, category, json_response.get("MSG"), wait_time)
        else:
            raise exceptions.RaiseError(response, category, None, None)

    def get_user(self, user_id: int) -> types.UserProfile:
        """
        Парсит страницу пользователя.

        :param user_id: ID пользователя.
        :type user_id: :obj:`int`

        :return: объект профиля пользователя.
        :rtype: :class:`FunPayAPI.types.UserProfile`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        response = self.method("get", f"users/{user_id}/", {"accept": "*/*"}, {}, raise_not_200=True)
        html_response = response.content.decode()
        parser = BeautifulSoup(html_response, "html.parser")

        username = parser.find("div", {"class": "user-link-name"})
        if not username:
            raise exceptions.UnauthorizedError(response)

        username = parser.find("span", {"class": "mr4"}).text
        user_status = parser.find("span", {"class": "media-user-status"})
        user_status = user_status.text if user_status else ""
        avatar_link = parser.find("div", {"class": "avatar-photo"}).get("style").split("(")[1].split(")")[0]
        avatar_link = avatar_link if avatar_link.startswith("https") else f"https://funpay.com{avatar_link}"
        banned = bool(parser.find("span", {"class": "label label-danger"}))
        user_obj = types.UserProfile(user_id, username, avatar_link, "Онлайн" in user_status, banned, html_response)

        subcategories_divs = parser.find_all("div", {"class": "offer-list-title-container"})

        if not subcategories_divs:
            return user_obj

        for i in subcategories_divs:
            subcategory_link = i.find("h3").find("a").get("href")
            subcategory_id = int(subcategory_link.split("/")[-2])
            subcategory_type = types.SubCategoryTypes.CURRENCY if "chips" in subcategory_link else \
                types.SubCategoryTypes.COMMON
            subcategory_obj = self.get_subcategory(subcategory_type, subcategory_id)
            if not subcategory_obj:
                continue

            offers = i.parent.find_all("a", {"class": "tc-item"})
            for j in offers:
                offer_id = j["href"].split("id=")[1]
                description = j.find("div", {"class": "tc-desc-text"})
                description = description.text if description else None
                server = j.find("div", {"class": "tc-server hidden-xxs"})
                if not server:
                    server = j.find("div", {"class": "tc-server hidden-xs"})
                server = server.text if server else None

                if subcategory_obj.type is types.SubCategoryTypes.COMMON:
                    price = float(j.find("div", {"class": "tc-price"})["data-s"])
                else:
                    price = float(j.find("div", {"class": "tc-price"}).find("div").text.split(" ")[0])

                lot_obj = types.LotShortcut(offer_id, server, description, price, subcategory_obj, str(j))
                user_obj.add_lot(lot_obj)
        return user_obj

    def get_chat(self, chat_id: int) -> types.Chat:
        """
        Получает информацию о личном чате.

        :param chat_id: ID чата.
        :type chat_id: :obj:`int`

        :return: объект чата.
        :rtype: :class:`FunPayAPI.types.Chat`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        response = self.method("get", f"chat/?node={chat_id}", {"accept": "*/*"}, {}, raise_not_200=True)
        html_response = response.content.decode()
        parser = BeautifulSoup(html_response, "html.parser")
        if (name := parser.find("div", {"class": "chat-header"}).find("div", {"class": "media-user-name"}).find("a").text) == "Чат":
            raise Exception("chat not found")  # todo

        if not (chat_panel := parser.find("div", {"class": "param-item chat-panel"})):
            text, link = None, None
        else:
            a = chat_panel.find("a")
            text, link = a.text, a["href"]

        history = self.get_chat_history(chat_id, interlocutor_username=name)
        return types.Chat(chat_id, name, link, text, html_response, history)

    def get_order(self, order_id: str) -> types.Order:
        """
        Получает полную информацию о заказе.

        :param order_id: ID заказа.
        :type order_id: :obj:`str`

        :return: объекст заказа.
        :rtype: :class:`FunPayAPI.types.Order`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()
        headers = {
            "accept": "*/*"
        }
        response = self.method("get", f"orders/{order_id}/", headers, {}, raise_not_200=True)
        html_response = response.content.decode()
        parser = BeautifulSoup(html_response, "html.parser")
        username = parser.find("div", {"class": "user-link-name"})
        if not username:
            raise exceptions.UnauthorizedError(response)

        if (span := parser.find("span", {"class": "text-warning"})) and span.text == "Возврат":
            status = types.OrderStatuses.REFUNDED
        elif (span := parser.find("span", {"class": "text-success"})) and span.text == "Закрыт":
            status = types.OrderStatuses.CLOSED
        else:
            status = types.OrderStatuses.PAID

        short_description = None
        full_description = None
        sum_ = None
        subcategory = None
        for div in parser.find_all("div", {"class": "param-item"}):
            if not (h := div.find("h5")):
                continue
            if h.text == "Краткое описание":
                short_description = div.find("div").text
            elif h.text == "Подробное описание":
                full_description = div.find("div").text
            elif h.text == "Сумма":
                sum_ = float(div.find("span").text)
            elif h.text in ("Категория", "Валюта"):
                subcategory_link = div.find("a").get("href")
                subcategory_split = subcategory_link.split("/")
                subcategory_id = int(subcategory_split[-2])
                subcategory_type = types.SubCategoryTypes.COMMON if "lots" in subcategory_link else \
                    types.SubCategoryTypes.CURRENCY
                subcategory = self.get_subcategory(subcategory_type, subcategory_id)

        chat = parser.find("div", {"class": "chat-header"})
        chat_link = chat.find("div", {"class": "media-user-name"}).find("a")
        interlocutor_name = chat_link.text
        interlocutor_id = int(chat_link.get("href").split("/")[-2])
        nav_bar = parser.find("ul", {"class": "nav navbar-nav navbar-right logged"})
        active_item = nav_bar.find("li", {"class": "active"})
        if "Продажи" in active_item.find("a").text.strip():
            buyer_id, buyer_username = interlocutor_id, interlocutor_name
            seller_id, seller_username = self.id, self.username
        else:
            buyer_id, buyer_username = self.id, self.username
            seller_id, seller_username = interlocutor_id, interlocutor_name

        review_obj = parser.find("div", {"class": "order-review"})
        if not (stars_obj := review_obj.find("div", {"class": "rating"})):
            stars, text,  = None, None
        else:
            stars = int(stars_obj.find("div").get("class")[0].split("rating")[1])
            text = review_obj.find("div", {"class": "review-item-text"}).text.strip()

        if not (reply_obj := review_obj.find("div", {"class": "review-item-answer review-compiled-reply"})):
            reply = None
        else:
            reply = reply_obj.find("div").text.strip()

        if all([not text, not reply]):
            review = None
        else:
            review = types.Review(stars, text, reply, False, str(reply_obj), order_id, buyer_username, buyer_id)

        order = types.Order(order_id, status, subcategory, short_description, full_description, sum_,
                            buyer_id, buyer_username, seller_id, seller_username, html_response, review)
        return order

    def get_sells(self, start_from: str | None = None, include_paid: bool = True, include_closed: bool = True,
                  include_refunded: bool = True, exclude_ids: list[str] | None = None,
                  id: Optional[int] = None, buyer: Optional[str] = None,
                  state: Optional[Literal["closed", "paid", "refunded"]] = None, game: Optional[int] = None,
                  section: Optional[str] = None, server: Optional[int] = None,
                  side: Optional[int] = None, **more_filters) -> tuple[str | None, list[types.OrderShortcut]]:
        """
        Получает и парсит список заказов со страницы https://funpay.com/orders/trade

        :param start_from: ID заказа, с которого начать список (ID заказа должен быть без '#'!).
        :type start_from: :obj:`str`

        :param include_paid: включить ли в список заказы, ожидающие выполнения?
        :type include_paid: :obj:`bool`, опционально

        :param include_closed: включить ли в список закрытые заказы?
        :type include_closed: :obj:`bool`, опционально

        :param include_refunded: включить ли в список заказы, за которые запрошен возврат средств?
        :type include_refunded: :obj:`bool`, опционально

        :param exclude_ids: исключить заказы с ID из списка (ID заказа должен быть без '#'!).
        :type exclude_ids: :obj:`list` of :obj:`str`, опционально

        :param id: ID заказа.
        :type id: :obj:`int`, опционально

        :param buyer: никнейм покупателя.
        :type buyer: :obj:`str`, опционально

        :param state: статус заказа.
        :type: :obj:`str` `paid`, `closed` or `refunded`, опционально

        :param game: ID игры.
        :type game: :obj:`int`, опционально

        :param section: ID категории в формате `<тип лота>-<ID категории>`.\n
            Типы лотов:\n
            * `lot` - стандартный лот (например: `lot-256`)\n
            * `chip` - игровая валюта (например: `chip-4471`)\n
        :type section: :obj:`str`, опционально

        :param server: ID сервера.
        :type server: :obj:`int`, опционально

        :param side: ID стороны (платформы).
        :type side: :obj:`int`, опционально.

        :param more_filters: доп. фильтры.

        :return: (ID след. заказа (для start_from), список заказов)
        :rtype: :obj:`tuple` (:obj:`str` or :obj:`None`, :obj:`list` of :class:`FunPayAPI.types.OrderShortcut`)
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        exclude_ids = exclude_ids or []
        filters = {"id": id, "buyer": buyer, "state": state, "game": game, "section": section, "server": server,
                   "side": side}
        filters = {name: filters[name] for name in filters if filters[name]}
        filters.update(more_filters)

        link = "https://funpay.com/orders/trade?"
        for name in filters:
            link += f"{name}={filters[name]}&"
        link = link[:-1]

        if start_from:
            filters["continue"] = start_from

        response = self.method("post" if start_from else "get", link, {}, filters, raise_not_200=True)
        html_response = response.content.decode()

        parser = BeautifulSoup(html_response, "html.parser")
        check_user = parser.find("div", {"class": "content-account content-account-login"})
        if check_user:
            raise exceptions.UnauthorizedError(response)

        next_order_id = parser.find("input", {"type": "hidden", "name": "continue"})
        next_order_id = next_order_id.get("value") if next_order_id else None

        order_divs = parser.find_all("a", {"class": "tc-item"})
        if not order_divs:
            return None, []

        sells = []
        for div in order_divs:
            classname = div.get("class")
            if "warning" in classname:
                if not include_refunded:
                    continue
                order_status = types.OrderStatuses.REFUNDED
            elif "info" in classname:
                if not include_paid:
                    continue
                order_status = types.OrderStatuses.PAID
            else:
                if not include_closed:
                    continue
                order_status = types.OrderStatuses.CLOSED

            order_id = div.find("div", {"class": "tc-order"}).text[1:]
            if order_id in exclude_ids:
                continue

            description = div.find("div", {"class": "order-desc"}).find("div").text
            price = float(div.find("div", {"class": "tc-price"}).text.split(" ")[0])

            buyer_div = div.find("div", {"class": "media-user-name"}).find("span")
            buyer_username = buyer_div.text
            buyer_id = int(buyer_div.get("data-href")[:-1].split("https://funpay.com/users/")[1])
            subcategory_name = div.find("div", {"class": "text-muted"}).text

            now = datetime.now()
            order_date_text = div.find("div", {"class": "tc-date-time"}).text
            if "сегодня" in order_date_text:  # сегодня, ЧЧ:ММ
                h, m = order_date_text.split(", ")[1].split(":")
                order_date = datetime(now.year, now.month, now.day, int(h), int(m))
            elif "вчера" in order_date_text:  # вчера, ЧЧ:ММ
                h, m = order_date_text.split(", ")[1].split(":")
                temp = now - timedelta(days=1)
                order_date = datetime(temp.year, temp.month, temp.day, int(h), int(m))
            elif order_date_text.count(" ") == 2:  # ДД месяца, ЧЧ:ММ
                split = order_date_text.split(", ")
                day, month = split[0].split()
                day, month = int(day), utils.MONTHS[month]
                h, m = split[1].split(":")
                order_date = datetime(now.year, month, day, int(h), int(m))
            else:  # ДД месяца ГГГГ, ЧЧ:ММ
                split = order_date_text.split(", ")
                day, month, year = split[0].split()
                day, month, year = int(day), utils.MONTHS[month], int(year)
                h, m = split[1].split(":")
                order_date = datetime(year, month, day, int(h), int(m))

            order_obj = types.OrderShortcut(order_id, description, price, buyer_username, buyer_id, order_status,
                                            order_date, subcategory_name, str(div))
            sells.append(order_obj)

        return next_order_id, sells

    def add_chats(self, chats: list[types.ChatShortcut]):
        """
        Сохраняет чаты.

        :param chats: объекты чатов.
        :type chats: :obj:`list` of :class:`FunPayAPI.types.ChatShortcut`
        """
        for i in chats:
            self.__saved_chats[i.id] = i

    def request_chats(self) -> list[types.ChatShortcut]:
        """
        Запрашивает чаты и парсит их.

        :return: объекты чатов (не больше 50).
        :rtype: :obj:`list` of :class:`FunPayAPI.types.ChatShortcut`
        """
        chats = {
            "type": "chat_bookmarks",
            "id": self.id,
            "tag": utils.random_tag(),
            "data": False
        }
        payload = {
            "objects": json.dumps([chats]),
            "request": False,
            "csrf_token": self.csrf_token
        }
        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest"
        }
        response = self.method("post", "https://funpay.com/runner/", headers, payload, raise_not_200=True)
        json_response = response.json()

        msgs = ""
        for obj in json_response["objects"]:
            if obj.get("type") != "chat_bookmarks":
                continue
            msgs = obj["data"]["html"]
        if not msgs:
            return []

        parser = BeautifulSoup(msgs, "html.parser")
        chats = parser.find_all("a", {"class": "contact-item"})
        chats_objs = []

        for msg in chats:
            chat_id = int(msg["data-id"])
            last_msg_text = msg.find("div", {"class": "contact-item-message"}).text
            unread = True if "unread" in msg.get("class") else False
            chat_with = msg.find("div", {"class": "media-user-name"}).text
            chat_obj = types.ChatShortcut(chat_id, chat_with, last_msg_text, unread, str(msg))
            chats_objs.append(chat_obj)
        return chats_objs

    def get_chats(self, update: bool = False) -> dict[int, types.ChatShortcut]:
        """
        Возвращает словарь с сохраненными чатами ({id: types.ChatShortcut})

        :param update: обновлять ли предварительно список чатов с помощью доп. запроса?
        :type update: :obj:`bool`, опционально

        :return: словарь с сохраненными чатами.
        :rtype: :obj:`dict` {:obj:`int`: :class:`FunPayAPi.types.ChatShortcut`}
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()
        if update:
            chats = self.request_chats()
            self.add_chats(chats)
        return self.__saved_chats

    def get_chat_by_name(self, name: str, make_request: bool = False) -> types.ChatShortcut | None:
        """
        Возвращает чат по его названию (если он сохранен).

        :param name: название чата.
        :type name: :obj:`str`

        :param make_request: обновить ли сохраненные чаты, если чат не был найден?
        :type make_request: :obj:`bool`, опционально

        :return: объект чата или :obj:`None`, если чат не был найден.
        :rtype: :class:`FunPayAPI.types.ChatShortcut` or :obj:`None`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        for i in self.__saved_chats:
            if self.__saved_chats[i].name == name:
                return self.__saved_chats[i]

        if make_request:
            self.add_chats(self.request_chats())
            return self.get_chat_by_name(name)
        else:
            return None

    def get_chat_by_id(self, chat_id: int, make_request: bool = False) -> types.ChatShortcut | None:
        """
        Возвращает личный чат по его ID (если он сохранен).

        :param chat_id: ID чата.
        :type chat_id: :obj:`int`

        :param make_request: обновить ли сохраненные чаты, если чат не был найден?
        :type make_request: :obj:`bool`, опционально

        :return: объект чата или :obj:`None`, если чат не был найден.
        :rtype: :class:`FunPayAPI.types.ChatShortcut` or :obj:`None`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()

        if not make_request or chat_id in self.__saved_chats:
            return self.__saved_chats.get(chat_id)

        self.add_chats(self.request_chats())
        return self.get_chat_by_id(chat_id)

    def get_lot_fields(self, lot_id: int) -> types.LotFields:
        """
        Получает все поля лота.

        :param lot_id: ID лота.
        :type lot_id: :obj:`int`

        :return: объект с полями лота.
        :rtype: :class:`FunPayAPI.types.LotFields`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()
        headers = {}
        response = self.method("get", f"lots/offerEdit?offer={lot_id}", headers, {}, raise_not_200=True)

        html_response = response.content.decode()
        bs = BeautifulSoup(html_response, "html.parser")

        result = {"active": "", "deactivate_after_sale": ""}
        result.update({field["name"]: field.get("value") or "" for field in bs.find_all("input")
                       if field["name"] not in ["active", "deactivate_after_sale"]})
        result.update({field["name"]: field.text or "" for field in bs.find_all("textarea")})
        result.update({field["name"]: field.find("option", selected=True)["value"] for field in bs.find_all("select")})
        result.update({field["name"]: "on" for field in bs.find_all("input", {"type": "checkbox"}, checked=True)})
        return types.LotFields(lot_id, result)

    def save_lot(self, lot_fields: types.LotFields):
        """
        Сохраняет лот на FunPay.

        :param lot_fields: объект с полями лота.
        :type lot_fields: :class:`FunPayAPI.types.LotFields`
        """
        if not self.is_initiated:
            raise exceptions.AccountNotInitiatedError()
        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
        }
        fields = lot_fields.renew_fields().fields
        fields["location"] = "trade"

        response = self.method("post", "lots/offerSave", headers, fields, raise_not_200=True)
        json_response = response.json()
        if json_response.get("error"):
            raise exceptions.LotSavingError(response, json_response.get("error"), lot_fields.lot_id)

    def get_category(self, category_id: int) -> types.Category | None:
        """
        Возвращает объект категории (игры).

        :param category_id: ID категории (игры).
        :type category_id: :obj:`int`

        :return: объект категории (игры) или :obj:`None`, если категория не была найдена.
        :rtype: :class:`FunPayAPI.types.Category` or :obj:`None`
        """
        return self.__sorted_categories.get(category_id)

    @property
    def categories(self) -> list[types.Category]:
        """
        Возвращает все категории (игры) FunPay (парсятся при первом выполнении метода :meth:`FunPayAPI.account.Account.get`).

        :return: все категории (игры) FunPay.
        :rtype: :obj:`list` of :class:`FunPayAPI.types.Category`
        """
        return self.__categories

    def get_sorted_categories(self) -> dict[int, types.Category]:
        """
        Возвращает все категории (игры) FunPay в виде словаря {ID: категория}
        (парсятся при первом выполнении метода :meth:`FunPayAPI.account.Account.get`).

        :return: все категории (игры) FunPay в виде словаря {ID: категория}
        :rtype: :obj:`dict` {:obj:`int`: :class:`FunPayAPI.types.Category`}
        """
        return self.__sorted_categories

    def get_subcategory(self, subcategory_type: types.SubCategoryTypes,
                        subcategory_id: int) -> types.SubCategory | None:
        """
        Возвращает объект подкатегории.

        :param subcategory_type: тип подкатегории.
        :type subcategory_type: :class:`FunPayAPI.common.enums.SubCategoryTypes`

        :param subcategory_id: ID подкатегории.
        :type subcategory_id: :obj:`int`

        :return: объект подкатегории или :obj:`None`, если подкатегория не была найдена.
        :rtype: :class:`FunPayAPI.types.SubCategory` or :obj:`None`
        """
        return self.__sorted_subcategories[subcategory_type].get(subcategory_id)

    @property
    def subcategories(self) -> list[types.SubCategory]:
        """
        Возвращает все подкатегории FunPay (парсятся при первом выполнении метода Account.get).

        :return: все подкатегории FunPay.
        :rtype: :obj:`list` of :class:`FunPayAPI.types.SubCategory`
        """
        return self.__subcategories

    def get_sorted_subcategories(self) -> dict[types.SubCategoryTypes, dict[int, types.SubCategory]]:
        """
        Возвращает все подкатегории FunPay в виде словаря {тип подкатегории: {ID: подкатегория}}
        (парсятся при первом выполнении метода Account.get).

        :return: все подкатегории FunPay в виде словаря {тип подкатегории: {ID: подкатегория}}
        :rtype: :obj:`dict` {:class:`FunPayAPI.common.enums.SubCategoryTypes`: :obj:`dict` {:obj:`int` :class:`FunPayAPI.types.SubCategory`}}
        """
        return self.__sorted_subcategories

    @property
    def is_initiated(self) -> bool:
        """
        Инициализирован ли класс :class:`FunPayAPI.account.Account` с помощью метода :meth:`FunPayAPI.account.Account.get`?

        :return: :obj:`True`, если да, :obj:`False`, если нет.
        :rtype: :obj:`bool`
        """
        return self.__initiated

    def __setup_categories(self, html: str):
        """
        Парсит категории и подкатегории с основной страницы и добавляет их в свойства класса.

        :param html: HTML страница.
        """
        parser = BeautifulSoup(html, "html.parser")
        games_table = parser.find_all("div", {"class": "promo-game-list"})
        if not games_table:
            return

        games_table = games_table[1] if len(games_table) > 1 else games_table[0]
        games_divs = games_table.find_all("div", {"class": "promo-game-item"})
        if not games_divs:
            return

        for i in games_divs:
            gid = int(i.find("div", {"class": "game-title"}).get("data-id"))
            gname = i.find("a").text
            regional_games = {
                gid: types.Category(gid, gname)
            }
            if regional_divs := i.find("div", {"role": "group"}):
                for btn in regional_divs.find_all("button"):
                    regional_game_id = int(btn["data-id"])
                    regional_games[regional_game_id] = types.Category(regional_game_id, f"{gname} ({btn.text})")

            subcategories_divs = i.find_all("ul", {"class": "list-inline"})
            for j in subcategories_divs:
                j_game_id = int(j["data-id"])
                subcategories = j.find_all("li")
                for k in subcategories:
                    a = k.find("a")
                    name, link = a.text, a["href"]
                    stype = types.SubCategoryTypes.CURRENCY if "chips" in link else types.SubCategoryTypes.COMMON
                    sid = int(link.split("/")[-2])
                    sobj = types.SubCategory(sid, name, stype, regional_games[j_game_id])
                    regional_games[j_game_id].add_subcategory(sobj)
                    self.__subcategories.append(sobj)
                    self.__sorted_subcategories[stype][sid] = sobj

            for gid in regional_games:
                self.__categories.append(regional_games[gid])
                self.__sorted_categories[gid] = regional_games[gid]

    def __parse_messages(self, json_messages: dict, chat_id: int | str,
                         interlocutor_id: Optional[int] = None, interlocutor_username: Optional[str] = None,
                         from_id: int = 0) -> list[types.Message]:
        messages = []
        ids = {self.id: self.username, 0: "FunPay"}
        badges = {}
        if interlocutor_id is not None:
            ids[interlocutor_id] = interlocutor_username

        for i in json_messages:
            if i["id"] < from_id:
                continue
            author_id = i["author"]
            parser = BeautifulSoup(i["html"], "html.parser")

            # Если ник или бейдж написавшего неизвестен, но есть блок с данными об авторе сообщения
            if None in [ids.get(author_id), badges.get(author_id)] and (author_div := parser.find("div", {"class": "media-user-name"})):
                if badges.get(author_id) is None:
                    badge = author_div.find("span", {"class": "label label-success"})
                    badges[author_id] = badge.text if badge else 0
                if ids.get(author_id) is None:
                    author = author_div.find("a").text.strip()
                    ids[author_id] = author
                    if self.chat_id_private(chat_id) and author_id == interlocutor_id and not interlocutor_username:
                        interlocutor_username = author
                        ids[interlocutor_id] = interlocutor_username

            if self.chat_id_private and (image_link := parser.find("a", {"class": "chat-img-link"})):
                image_link = image_link.get("href")
                message_text = None
            else:
                image_link = None
                if author_id == 0:
                    message_text = parser.find("div", {"class": "alert alert-with-icon alert-info"}).text.strip()
                else:
                    message_text = parser.find("div", {"class": "message-text"}).text

            by_bot = False
            if message_text and message_text.startswith(self.__bot_character):
                message_text = message_text[1:]
                by_bot = True

            message_obj = types.Message(i["id"], message_text, chat_id, interlocutor_username,
                                        None, author_id, i["html"], image_link, determine_msg_type=False)
            message_obj.by_bot = by_bot
            message_obj.type = types.MessageTypes.NON_SYSTEM if author_id != 0 else message_obj.get_message_type()
            messages.append(message_obj)

        for i in messages:
            i.author = ids.get(i.author_id)
            i.chat_name = interlocutor_username
            i.badge = badges.get(i.author_id) if badges.get(i.author_id) != 0 else None
            parser = BeautifulSoup(i.html, "html.parser")
            default_label = parser.find("div", {"class": "media-user-name"})
            default_label = default_label.find("span", {"class": "label label-default"}) if default_label else None
            i.badge = default_label.text if (i.badge is None and default_label is not None) else i.badge
        return messages

    @staticmethod
    def chat_id_private(chat_id: int | str):
        return isinstance(chat_id, int) or PRIVATE_CHAT_ID_RE.fullmatch(chat_id)

    @property
    def bot_character(self) -> str:
        return self.__bot_character
