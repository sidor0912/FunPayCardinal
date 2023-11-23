from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cardinal import Cardinal

import FunPayAPI.types
from FunPayAPI.account import Account
from logging import getLogger
from telebot.types import Message
from tg_bot import static_keyboards as skb
import time
import json


NAME = "Lots Copy Plugin"
VERSION = "0.0.3"
DESCRIPTION = "Данный плагин позволяет быстро переносить лоты с одного аккаунта на другой."
CREDITS = "@woopertail"
UUID = "5693f220-bcc6-4f6e-9745-9dee8664cbb2"
SETTINGS_PAGE = False


logger = getLogger("FPC.lots_copy_plugin")
RUNNING = False


# Callback'и
CBT_COPY_LOTS = "lots_copy_plugin.copy"
"""
Callback для активации режима ожидания ввода токена аккаунта, на который необходимо скопировать лоты.

User-state: ожидается токен аккаунта, на который необходимо скопировать лоты.
"""

CBT_CREATE_LOTS = "lots_copy_plugin.create"
"""
Callback для активации режима ожидания файла с лотами, полученного с помощью команды /cache_lots.

User-state: ожидается файл с лотами, полученного с помощью команды /cache_lots.
"""


def download_file(tg, msg: Message, file_name: str = "temp_file.txt"):
    """
    Скачивает выгруженный файл и сохраняет его в папку storage/cache/.

    :param tg: экземпляр TG бота.
    :param msg: экземпляр сообщения.
    :param file_name: название сохраненного файла.
    """
    tg.bot.send_message(msg.chat.id, "⏬ Загружаю файл...")
    try:
        file_info = tg.bot.get_file(msg.document.file_id)
        file = tg.bot.download_file(file_info.file_path)
    except:
        tg.bot.send_message(msg.chat.id, "❌ Произошла ошибка при загрузке файла.")
        logger.debug("TRACEBACK", exc_info=True)
        raise Exception

    path = f"storage/cache/{file_name}"
    with open(path, "wb") as new_file:
        new_file.write(file)
    return True


def init_commands(cardinal: Cardinal):
    if not cardinal.telegram:
        return
    tg = cardinal.telegram
    bot = cardinal.telegram.bot

    def get_current_account(tg_msg: Message) -> FunPayAPI.types.UserProfile:
        """
        Получает данные о текущем аккаунте.

        :param tg_msg: экземпляр Telegram-сообщения-триггера.

        :return: экземпляр текущего аккаунта.
        """
        attempts = 3
        while attempts:
            try:
                profile = cardinal.account.get_user(cardinal.account.id)
                return profile
            except:
                logger.error("[LOTS COPY] Не удалось получить данные о текущем профиле.")
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(1)
                attempts -= 1
        else:
            bot.send_message(tg_msg.chat.id, "❌ Не удалось получить данные текущего профиля.")
            raise Exception

    def get_second_account(tg_msg: Message, token: str) -> FunPayAPI.account.Account:
        """
        Получает данные об аккаунте, на который нужно скопировать лоты.

        :param tg_msg: экземпляр Telegram-сообщения-триггера.
        :param token: токен (golden_key) аккаунта, на который нужно скопировать лоты.

        :return: экземпляр аккаунта, на который необходимо скопировать лоты.
        """
        attempts = 3
        while attempts:
            try:
                acc = FunPayAPI.account.Account(token).get()
                return acc
            except:
                logger.error("[LOTS COPY] Не удалось получить данные об аккаунте для копирования лотов.")
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(1)
                attempts -= 1
        else:
            bot.send_message(tg_msg.chat.id, "❌ Не удалось получить данные об аккаунте для копирования лотов.")
            raise Exception

    def get_lots_info(tg_msg: Message, profile: FunPayAPI.types.UserProfile) -> list[FunPayAPI.types.LotFields]:
        """
        Получает данные о всех лотах (кроме валюты) на текущем аккаунте.

        :param tg_msg: экземпляр Telegram-сообщения-триггера.
        :param profile: экземпляр текущего аккаунта.

        :return: список экземпляров лотов.
        """
        result = []
        for i in profile.get_lots():
            if i.subcategory.type == FunPayAPI.types.SubCategoryTypes.CURRENCY:
                continue
            attempts = 3
            while attempts:
                try:
                    result.append(cardinal.account.get_lot_fields(i.id))
                    logger.info(f"[LOTS COPY] Получил данные о лоте {i.id}.")
                    break
                except:
                    logger.error(f"[LOTS COPY] Не удалось получить данные о лоте {i.id}.")
                    logger.debug("TRACEBACK", exc_info=True)
                    time.sleep(2)
                    attempts -= 1
            else:
                bot.send_message(tg_msg.chat.id, f"❌ Не удалось получить данные о "
                                                 f"<a href=\"https://funpay.com/lots/offer?id={i.id}\">лоте {i.id}</a>."
                                                 f" Пропускаю.")
                time.sleep(1)
                continue
            time.sleep(0.5)
        return result

    def create_lot(acc: Account, lot: FunPayAPI.types.LotFields):
        """
        Создает лот на переданном аккаунте.

        :param acc: экземпляр аккаунта, на котором нужно создать лот.
        :param lot: экземпляр лота.
        """
        lot_id = lot.lot_id
        fields = lot.fields
        fields["offer_id"] = "0"
        fields["csrf_token"] = acc.csrf_token
        lot.set_fields(fields)
        lot.lot_id = 0

        attempts = 3
        while attempts:
            try:
                acc.save_lot(lot)
                logger.info(f"[LOTS COPY] Создал лот {lot_id}.")
                return
            except Exception as e:
                logger.error(f"[LOTS COPY] Не удалось создать лот {lot_id}.")
                logger.debug("TRACEBACK", exc_info=True)
                if isinstance(e, FunPayAPI.exceptions.RequestFailedError):
                    logger.debug(e.response.content.decode())
                time.sleep(2)
                attempts -= 1
        else:
            raise Exception

    def act_copy_lots(m: Message):
        """
        Активирует режим ожидания ввода токена для копирования лотов.
        """
        if RUNNING:
            bot.send_message(m.chat.id,
                             "❌ Процесс копирования лотов уже начался! "
                             "Дождитесь конца текущего процесса или перезапустите бота.")
            return
        result = bot.send_message(m.chat.id, "Отправьте токен (golden_key) аккаунта, на который нужно скопировать лоты.",
                                  reply_markup=skb.CLEAR_STATE_BTN())
        tg.set_state(m.chat.id, result.id, m.from_user.id, CBT_COPY_LOTS)

    def copy_lots(m: Message):
        """
        Копирует лоты.
        """
        tg.clear_state(m.chat.id, m.from_user.id, True)
        token = m.text.strip()
        if len(token) != 32:
            bot.send_message(m.chat.id, "❌ Неверный формат токена.")
            return

        global RUNNING
        RUNNING = True
        try:
            bot.send_message(m.chat.id, "Получаю данные о текущем профиле...")
            profile = get_current_account(m)

            bot.send_message(m.chat.id, "Получаю данные о втором аккаунте...")
            second_account = get_second_account(m, token)

            bot.send_message(m.chat.id, "Получаю данные о текущих лотах (это может занять кое-какое время (1 лот/сек))...")
            lots = get_lots_info(m, profile)

            bot.send_message(m.chat.id, "Копирую лоты (это может занять кое-какое время (1 лот/сек))...")
            for i in lots:
                lot_id = i.lot_id
                time.sleep(1)
                try:
                    create_lot(second_account, i)
                except:
                    bot.send_message(m.chat.id, f"❌ Не удалось скопировать лот "
                                                f"https://funpay.com/lots/offer?id={lot_id}\n"
                                                f"Пропускаю.")
                    continue

            RUNNING = False
            bot.send_message(m.chat.id, "✅ Копирование активных лотов завершено!")
        except:
            RUNNING = False
            logger.error("[LOTS COPY] Не удалось скопировать лоты.")
            logger.debug("TRACEBACK", exc_info=True)
            bot.send_message("❌ Не удалось скопировать лоты.")
            return

    def cache_lots(m: Message):
        """
        Кэширует лоты в файл и отправляет его в Telegram чат.
        """
        global RUNNING
        if RUNNING:
            bot.send_message(m.chat.id, "❌ Процесс копирования лотов уже начался! "
                                        "Дождитесь конца текущего процесса или перезапустите бота.")
            return
        RUNNING = True
        try:
            bot.send_message(m.chat.id, "Получаю данные о текущем профиле...")
            profile = get_current_account(m)

            bot.send_message(m.chat.id, "Получаю данные о текущих лотах (это может занять кое-какое время (1 лот/сек))...")
            result = []
            for i in get_lots_info(m, profile):
                fields = i.fields
                del fields["csrf_token"]
                del fields["offer_id"]
                result.append(fields)

            bot.send_message(m.chat.id, "Сохраняю данные о текущих лотах в файл и отправляю сюда...")
            with open("storage/cache/lots.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(result, indent=4, ensure_ascii=False))
            with open("storage/cache/lots.json", "r", encoding="utf-8") as f:
                bot.send_document(m.chat.id, f)
            RUNNING = False
        except:
            RUNNING = False
            logger.error("[LOTS COPY] Не удалось кэшировать лоты.")
            logger.debug("TRACEBACK", exc_info=True)
            bot.send_message("❌ Не удалось кэшировать лоты.")
            return

    def act_create_lots(m: Message):
        """
        Активирует режим ожидания файла с лотами для создания лотов на текущем аккаунте.
        """
        if RUNNING:
            bot.send_message(m.chat.id,
                             "❌ Процесс копирования лотов уже начался! "
                             "Дождитесь конца текущего процесса или перезапустите бота.")
            return
        result = bot.send_message(m.chat.id,
                                  "Отправьте мне файл с лотами, полученный с помощью команды /cache_lots.",
                                  reply_markup=skb.CLEAR_STATE_BTN())
        tg.set_state(m.chat.id, result.id, m.from_user.id, CBT_CREATE_LOTS)

    def create_lots(m: Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        global RUNNING
        if not m.document.file_name.endswith(".json"):
            bot.send_message(m.chat.id, "❌ Это не файл с лотами.")
            return
        if m.document.file_size >= 20971520:
            bot.send_message(m.chat.id, "❌ Размер файла не должен превышать 20МБ.")
            return

        RUNNING = True
        try:
            bot.send_message(m.chat.id, "Загружаю файл...")
            download_file(tg, m, "lots.json")

            with open("storage/cache/lots.json", "r", encoding="utf-8") as f:
                data = json.loads(f.read())
            bot.send_message(m.chat.id, f"Получено {len(data)} лот(-a/-ов).\n"
                                        f"Создаю лоты на текущем аккаунте (это может занять кое-какое время (1 лот/сек))...")

            for i in data:
                try:
                    time.sleep(1)
                    lot = FunPayAPI.types.LotFields(0, i)
                    create_lot(cardinal.account, lot)
                except:
                    bot.send_message(m.chat.id, f"❌ Не удалось создать лот."
                                                f"Пропускаю.")
                    continue
            RUNNING = False
            bot.send_message(m.chat.id, "✅ Создание лотов завершено!")
        except:
            RUNNING = False
            logger.error("[LOTS COPY] Не удалось создать лоты.")
            logger.debug("TRACEBACK", exc_info=True)
            bot.send_message(m.chat.id, "❌ Не удалось создать лоты.")
            return

    cardinal.add_telegram_commands(UUID, [
        ("copy_lots", "копирует активные лоты с текущего аккаунта на другой.", True),
        ("cache_lots", "кэширует активные лоты в файл", True),
        ("create_lots", "создает лоты на текущем аккаунте", True)
    ])

    tg.msg_handler(act_copy_lots, commands=["copy_lots"])
    tg.msg_handler(copy_lots, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT_COPY_LOTS))
    tg.msg_handler(cache_lots, commands=["cache_lots"])
    tg.msg_handler(act_create_lots, commands=["create_lots"])
    tg.file_handler(CBT_CREATE_LOTS, create_lots)


BIND_TO_PRE_INIT = [init_commands]
BIND_TO_DELETE = None
