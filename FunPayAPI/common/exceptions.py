"""
В данном модуле описаны все кастомные исключения, используемые в пакете FunPayAPI.
"""
import requests
from .. import types


class AccountNotInitiatedError(Exception):
    """
    Исключение, которое возбуждается, если предпринята попытка вызвать метод класса :class:`FunPayAPI.account.Account`
    без предварительного получения данных аккаунта с помощью метода :meth:`FunPayAPI.account.Account.get`.
    """
    def __init__(self):
        pass

    def __str__(self):
        return "Необходимо получить данные об аккаунте с помощью метода Account.get()"


class RequestFailedError(Exception):
    """
    Исключение, которое возбуждается, если статус код ответа != 200.
    """
    def __init__(self, response: requests.Response):
        """
        :param response: объект ответа.
        """
        self.response = response
        self.status_code = response.status_code
        self.url = response.request.url
        self.request_headers = response.request.headers
        if "cookie" in self.request_headers:
            self.request_headers["cookie"] = "HIDDEN"
        self.request_body = response.request.body
        self.log_response = False

    def short_str(self):
        return f"Ошибка запроса к {self.url}. (Статус-код: {self.status_code})"

    def __str__(self):
        msg = f"Ошибка запроса к {self.url} .\n" \
              f"Метод: {self.response.request.method} .\n" \
              f"Статус-код ответа: {self.status_code} .\n" \
              f"Заголовки запроса: {self.request_headers} .\n" \
              f"Тело запроса: {self.request_body} ."
        if self.log_response:
            msg += f"\n{self.response.content.decode()}"
        return msg


class UnauthorizedError(RequestFailedError):
    """
    Исключение, которое возбуждается, если не удалось найти идентифицирующий аккаунт элемент и / или произошло другое
    событие, указывающее на отсутствие авторизации.
    """
    def __init__(self, response):
        super(UnauthorizedError, self).__init__(response)

    def short_str(self):
        return "Не авторизирован (возможно, введен неверный golden_key?)."


class WithdrawError(RequestFailedError):
    """
    Исключение, которое возбуждается, если произошла ошибка при попытке вывести средства с аккаунта.
    """
    def __init__(self, response, error_message: str | None):
        super(WithdrawError, self).__init__(response)
        self.error_message = error_message
        if not self.error_message:
            self.log_response = True

    def short_str(self):
        return f"Произошла ошибка при выводе средств с аккаунта{f': {self.error_message}' if self.error_message else '.'}"


class RaiseError(RequestFailedError):
    """
    Исключение, которое возбуждается, если произошла ошибка при попытке поднять лоты.
    """
    def __init__(self, response, category: types.Category, error_message: str | None, wait_time: int | None):
        super(RaiseError, self).__init__(response)
        self.category = category
        self.error_message = error_message
        self.wait_time = wait_time

    def short_str(self):
        return f"Не удалось поднять лоты категории \"{self.category.name}\"" \
               f"{f': {self.error_message}' if self.error_message else '.'}"


class ImageUploadError(RequestFailedError):
    """
    Исключение, которое возбуждается, если произошла ошибка при выгрузке изображения.
    """
    def __init__(self, response: requests.Response, error_message: str | None):
        super(ImageUploadError, self).__init__(response)
        self.error_message = error_message
        if not self.error_message:
            self.log_response = True

    def short_str(self):
        return f"Произошла ошибка при выгрузке изображения{f': {self.error_message}' if self.error_message else '.'}"


class MessageNotDeliveredError(RequestFailedError):
    """
    Исключение, которое возбуждается, если при отправке сообщения произошла ошибка.
    """
    def __init__(self, response: requests.Response, error_message: str | None, chat_id: int):
        super(MessageNotDeliveredError, self).__init__(response)
        self.error_message = error_message
        self.chat_id = chat_id
        if not self.error_message:
            self.log_response = True

    def short_str(self):
        return f"Не удалось отправить сообщение в чат {self.chat_id}" \
               f"{f': {self.error_message}' if self.error_message else '.'}"


class FeedbackEditingError(RequestFailedError):
    """
    Исключение, которое возбуждается, если при добавлении / редактировании / удалении отзыва / ответа на отзыв
    произошла ошибка.
    """
    def __init__(self, response: requests.Response, error_message: str | None, order_id: str):
        super(FeedbackEditingError, self).__init__(response)
        self.error_message = error_message
        self.order_id = order_id
        if not self.error_message:
            self.log_response = True

    def short_str(self):
        return f"Не удалось изменить состояние отзыва / ответа на отзыв на заказ {self.order_id}" \
               f"{f': {self.error_message}' if self.error_message else '.'}"


class LotSavingError(RequestFailedError):
    """
    Исключение, которое возбуждается, если при сохранении лота произошла ошибка.
    """
    def __init__(self, response: requests.Response, error_message: str | None, lot_id: int):
        super(LotSavingError, self).__init__(response)
        self.error_message = error_message
        self.lot_id = lot_id
        if not self.error_message:
            self.log_response = True

    def short_str(self):
        return f"Не удалось сохранить лот {self.lot_id}" \
               f"{f': {self.error_message}' if self.error_message else '.'}"


class RefundError(RequestFailedError):
    """
    Исключение, которое возбуждается, если при возврате средств за заказ произошла ошибка.
    """
    def __init__(self, response: requests.Response, error_message: str | None, order_id: str):
        super(RefundError, self).__init__(response)
        self.error_message = error_message
        self.order_id = order_id
        if not self.error_message:
            self.log_response = True

    def short_str(self):
        return f"Не удалось вернуть средства по заказу {self.order_id}" \
               f"{f': {self.error_message}' if self.error_message else '.'}"
