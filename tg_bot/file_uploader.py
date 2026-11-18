"""
В данном модуле реализован загрузчик файлов из телеграм чата.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from cardinal import Cardinal
    from tg_bot.bot import TGBot

from Utils import config_loader as cfg_loader, exceptions as excs, cardinal_tools, updater
from telebot.types import InlineKeyboardButton as Button
from tg_bot import utils, keyboards, CBT
from tg_bot.static_keyboards import CLEAR_STATE_BTN
from telebot import types
import logging
import os

logger = logging.getLogger("TGBot")  # locale#locale#locale


def check_file(tg: TGBot, msg: types.Message, type_: Literal["py", "cfg", "json", "txt"] | None = None) -> bool:
    """
    Проверяет выгруженный файл. Отправляет сообщение в TG в зависимости от ошибки.

    :param tg: экземпляр TG бота.

    :param msg: экземпляр сообщения.

    :param type_: формат файла.

    :return: True, если все ок, False, если файл проверку не прошел.
    """
    if not msg.document:
        tg.bot.send_message(msg.chat.id, "❌ Файл не обнаружен.")
        return False
    if not any((msg.document.file_name.endswith(".cfg"), msg.document.file_name.endswith(".txt"),
                msg.document.file_name.endswith(".py"), msg.document.file_name.endswith(".json"))):
        tg.bot.send_message(msg.chat.id, "❌ Файл должен быть текстовым.")
        return False
    if type_ is not None and not msg.document.file_name.endswith(f".{type_}"):
        tg.bot.send_message(msg.chat.id, f"❌ Неправильный формат файла: "
                                         f"<b><u>.{msg.document.file_name.split('.')[-1]}</u></b> "
                                         f"(вместо <b><u>.{type_}</u></b>)")
        return False
    if msg.document.file_size >= 20971520:
        tg.bot.send_message(msg.chat.id, "❌ Размер файла не должен превышать 20МБ.")
        return False
    return True


def download_file(tg: TGBot, msg: types.Message, file_name: str = "temp_file.txt",
                  custom_path: str = "") -> bool:
    """
    Скачивает выгруженный файл и сохраняет его в папку storage/cache/.

    :param tg: экземпляр TG бота.

    :param msg: экземпляр сообщения.

    :param file_name: название сохраненного файла.

    :param custom_path: кастомный путь (если надо сохранить не в storage/cache/).

    :return: True, если все ок, False, при ошибке.
    """
    tg.bot.send_message(msg.chat.id, "⏬ Загружаю файл...")
    try:
        file_info = tg.bot.get_file(msg.document.file_id)
        file = tg.bot.download_file(file_info.file_path)
    except:
        tg.bot.send_message(msg.chat.id, "❌ Произошла ошибка при загрузке файла.")
        logger.debug("TRACEBACK", exc_info=True)
        return False

    path = f"storage/cache/{file_name}" if not custom_path else os.path.join(custom_path, file_name)
    with open(path, "wb") as new_file:
        new_file.write(file)
    return True


def init_uploader(cardinal: Cardinal):
    tg = cardinal.telegram
    bot = tg.bot

    def act_upload_products_file(c: types.CallbackQuery):
        result = bot.send_message(c.message.chat.id, "Отправьте мне файл с товарами.",
                                  reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.UPLOAD_PRODUCTS_FILE)
        bot.answer_callback_query(c.id)

    def upload_products_file(m: types.Message):
        """
        Загружает файл с товарами.
        """
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_file(tg, m, type_="txt"):
            return
        with cardinal_tools.get_products_file_lock(f"storage/products/{m.document.file_name}"):
            if not download_file(tg, m, m.document.file_name,
                                 custom_path=f"storage/products"):
                return

        try:
            products_count = cardinal_tools.count_products(f"storage/products/{utils.escape(m.document.file_name)}")
        except:
            bot.send_message(m.chat.id, "❌ Произошла ошибка при подсчете товаров.")
            logger.debug("TRACEBACK", exc_info=True)
            return

        file_number = os.listdir("storage/products").index(m.document.file_name)

        keyboard = types.InlineKeyboardMarkup() \
            .add(Button("✏️ Редактировать файл", callback_data=f"{CBT.EDIT_PRODUCTS_FILE}:{file_number}:0"))

        logger.info(f"Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил в бота файл с товарами $YELLOWstorage/products/{m.document.file_name}$RESET.")

        bot.send_message(m.chat.id,
                         f"✅ Файл с товарами <code>storage/products/{m.document.file_name}</code> успешно загружен. "
                         f"Товаров в файле: <code>{products_count}.</code>",
                         reply_markup=keyboard)

    def act_upload_main_config(c: types.CallbackQuery):
        result = bot.send_message(c.message.chat.id, "Отправьте мне основной конфиг.",
                                  reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, "upload_main_config")
        bot.answer_callback_query(c.id)

    def upload_main_config(m: types.Message):
        """
        Загружает и проверяет основной конфиг.
        """
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_file(tg, m, type_="cfg"):
            return
        if not download_file(tg, m, "temp_main.cfg"):
            return

        bot.send_message(m.chat.id, "🔁 Проверяю валидность файла...")
        try:
            new_config = cfg_loader.load_main_config("storage/cache/temp_main.cfg")
        except excs.ConfigParseError as e:
            bot.send_message(m.chat.id, f"❌ Произошла ошибка при обработке основного конфига: "
                                        f"<code>{utils.escape(str(e))}</code>")
            return
        except UnicodeDecodeError:
            bot.send_message(m.chat.id,
                             "Произошла ошибка при расшифровке <code>UTF-8</code>. Убедитесь, что кодировка "
                             "файла = <code>UTF-8</code>, а формат конца строк = <code>LF</code>.")
            return
        except:
            bot.send_message(m.chat.id, "❌ Произошла ошибка при проверке конфига автовыдачи.")
            logger.debug("TRACEBACK", exc_info=True)
            return

        cardinal.save_config(new_config, "configs/_main.cfg")
        logger.info(f"Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил в бота основной конфиг.")
        bot.send_message(m.chat.id, "✅ Основной конфиг успешно загружен. \n"
                                    "Необходимо перезагрузить бота, что бы применить изменения. \n"
                                    "Любое изменение основного конфига через переключатели на ПУ отменит все изменения.")

    def act_upload_auto_response_config(c: types.CallbackQuery):
        result = bot.send_message(c.message.chat.id, "Отправьте мне конфиг автоответчика.",
                                  reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, "upload_auto_response_config")
        bot.answer_callback_query(c.id)

    def upload_auto_response_config(m: types.Message):
        """
        Загружает, проверяет и устанавливает конфиг автовыдачи.
        """
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_file(tg, m, type_="cfg"):
            return
        if not download_file(tg, m, "temp_auto_response.cfg"):
            return

        bot.send_message(m.chat.id, "🔁 Проверяю валидность файла...")
        try:
            new_config = cfg_loader.load_auto_response_config("storage/cache/temp_auto_response.cfg")
            raw_new_config = cfg_loader.load_raw_auto_response_config("storage/cache/temp_auto_response.cfg")
        except excs.ConfigParseError as e:
            bot.send_message(m.chat.id, f"❌ Произошла ошибка при обработке конфига автоответчика: "
                                        f"<code>{utils.escape(str(e))}</code>")
            return
        except UnicodeDecodeError:
            bot.send_message(m.chat.id,
                             "Произошла ошибка при расшифровке <code>UTF-8</code>. Убедитесь, что кодировка "
                             "файла = <code>UTF-8</code>, а формат конца строк = <code>LF</code>.")
            return
        except:
            bot.send_message(m.chat.id, "❌ Произошла ошибка при проверке конфига автоответчика.")
            logger.debug("TRACEBACK", exc_info=True)
            return

        cardinal.RAW_AR_CFG, cardinal.AR_CFG = raw_new_config, new_config
        cardinal.save_config(cardinal.RAW_AR_CFG, "configs/auto_response.cfg")

        logger.info(f"Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил в бота и установил конфиг автоответчика.")
        bot.send_message(m.chat.id, "✅ Конфиг автоответчика успешно применен.")

    def act_upload_auto_delivery_config(c: types.CallbackQuery):
        result = bot.send_message(c.message.chat.id, "Отправьте мне конфиг автовыдачи.",
                                  reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, "upload_auto_delivery_config")
        bot.answer_callback_query(c.id)

    def upload_auto_delivery_config(m: types.Message):
        """
        Загружает, проверяет и устанавливает конфиг автовыдачи.
        """
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_file(tg, m, type_="cfg"):
            return
        if not download_file(tg, m, "temp_auto_delivery.cfg"):
            return

        bot.send_message(m.chat.id, "🔁 Проверяю валидность файла...")
        try:
            new_config = cfg_loader.load_auto_delivery_config("storage/cache/temp_auto_delivery.cfg")
        except excs.ConfigParseError as e:
            bot.send_message(m.chat.id, f"❌ Произошла ошибка при обработке конфига автовыдачи: "
                                        f"<code>{utils.escape(str(e))}</code>")
            return
        except UnicodeDecodeError:
            bot.send_message(m.chat.id,
                             "Произошла ошибка при расшифровке <code>UTF-8</code>. Убедитесь, что кодировка "
                             "файла = <code>UTF-8</code>, а формат конца строк = <code>LF</code>.")
            return
        except:
            bot.send_message(m.chat.id, "❌ Произошла ошибка при проверке конфига автовыдачи.")
            logger.debug("TRACEBACK", exc_info=True)
            return

        cardinal.AD_CFG = new_config
        cardinal.save_config(cardinal.AD_CFG, "configs/auto_delivery.cfg")

        logger.info(f"Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил в бота и установил конфиг автовыдачи.")
        bot.send_message(m.chat.id, "✅ Конфиг автовыдачи успешно применен.")

    def upload_plugin(m: types.Message):
        offset = tg.get_state(m.chat.id, m.from_user.id)["data"]["offset"]
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_file(tg, m, type_="py"):
            return
        if not download_file(tg, m, f"{utils.escape(m.document.file_name)}",
                             custom_path=f"plugins"):
            return

        logger.info(f"[IMPORTANT] Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил в бота плагин $YELLOWplugins/{m.document.file_name}$RESET.")

        keyboard = types.InlineKeyboardMarkup() \
            .add(Button("◀️Назад", callback_data=f"{CBT.PLUGINS_LIST}:{offset}"))
        bot.send_message(m.chat.id,
                         f"✅ Плагин <code>{utils.escape(m.document.file_name)}</code> успешно загружен.\n\n"
                         f"⚠️Чтобы плагин активировался, <u><b>перезагрузите FPC!</b></u> (/restart)",
                         reply_markup=keyboard)

    def send_funpay_image(m: types.Message):
        data = tg.get_state(m.chat.id, m.from_user.id)["data"]
        chat_id, username = data["node_id"], data["username"]
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not m.photo:
            tg.bot.send_message(m.chat.id, "❌ Поддерживаются только форматы <code>.png</code>, <code>.jpg</code>, "
                                           "<code>.gif</code>.")
            return
        photo = m.photo[-1]
        if photo.file_size >= 20971520:
            tg.bot.send_message(m.chat.id, "❌ Размер файла не должен превышать 20МБ.")
            return

        try:
            file_info = tg.bot.get_file(photo.file_id)
            file = tg.bot.download_file(file_info.file_path)
            image_id = cardinal.account.upload_image(file, type_="chat")
            result = cardinal.send_message(chat_id, f"$photo={image_id}", username, watermark=False)
            if not result:
                raise Exception("Нету сообщений")
            tg.bot.reply_to(m, f'✅ Сообщение отправлено в переписку '
                               f'<a href="https://funpay.com/chat/?node={chat_id}">{username}</a>.',
                            reply_markup=keyboards.reply(chat_id, username, again=True))
        except:
            logger.warning("Произошла ошибка при отправке изображения.")
            logger.debug("TRACEBACK", exc_info=True)
            tg.bot.reply_to(m, f'❌ Не удалось отправить сообщение в переписку '
                               f'<a href="https://funpay.com/chat/?node={chat_id}">{username}</a>. '
                               f'Подробнее в файле <code>logs/log.log</code>',
                            reply_markup=keyboards.reply(chat_id, username, again=True))
            return

    def upload_image(m: types.Message, type_: Literal["chat", "offer"] = "chat"):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not m.photo:
            tg.bot.send_message(m.chat.id, "❌ Поддерживаются только форматы <code>.png</code>, <code>.jpg</code>, "
                                           "<code>.gif</code>.")
            return
        photo = m.photo[-1]
        if photo.file_size >= 20971520:
            tg.bot.send_message(m.chat.id, "❌ Размер файла не должен превышать 20МБ.")
            return

        try:
            file_info = tg.bot.get_file(photo.file_id)
            file = tg.bot.download_file(file_info.file_path)
            image_id = cardinal.account.upload_image(file, type_=type_)
        except:
            tg.bot.reply_to(m, f'❌ Не удалось отправить выгрузить изображение. '
                               f'Подробнее в файле <code>logs/log.log</code>')
            return
        if type_ == "chat":
            s = f"Используйте этот ID в текстах автовыдачи/автоответа с переменной " \
                f"<code>$photo</code>\n\n" \
                f"Например: <code>$photo={image_id}</code>"
        elif type_ == "offer":
            s = f"Используйте этот ID для добавления картинок к лотам."
        bot.reply_to(m, f"✅ Изображение выгружено на сервер FunPay.\n\n"
                        f"<b>ID:</b> <code>{image_id}</code>\n\n{s}")

    def upload_chat_image(m: types.Message):
        upload_image(m, type_="chat")

    def upload_offer_image(m: types.Message):
        upload_image(m, type_="offer")

    def upload_backup(m: types.Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not m.document:
            tg.bot.send_message(m.chat.id, "❌ Файл не обнаружен.")
            return
        if not m.document.file_name.endswith(".zip"):
            tg.bot.send_message(m.chat.id, f"❌ Неправильный формат файла: "
                                           f"<b><u>.{m.document.file_name.split('.')[-1]}</u></b> "
                                           f"(вместо <b><u>.zip</u></b>)")
            return
        if not download_file(tg, m, "backup.zip"):
            return
        if not updater.extract_backup_archive():
            tg.bot.send_message(m.chat.id, "❌ Возникла ошибка при распаковке архива.")
            return
        tg.bot.send_message(m.chat.id, "✅ Бекап загружен.")

        if not updater.install_backup():
            tg.bot.send_message(m.chat.id, "❌ Возникла ошибка при переносе файлов.")
            return
        tg.bot.send_message(m.chat.id, "✅ Бекап использован. Используй команду /restart.")

    tg.cbq_handler(act_upload_products_file, lambda c: c.data == CBT.UPLOAD_PRODUCTS_FILE)
    tg.cbq_handler(act_upload_auto_response_config, lambda c: c.data == "upload_auto_response_config")
    tg.cbq_handler(act_upload_auto_delivery_config, lambda c: c.data == "upload_auto_delivery_config")
    tg.cbq_handler(act_upload_main_config, lambda c: c.data == "upload_main_config")

    tg.file_handler(CBT.UPLOAD_PRODUCTS_FILE, upload_products_file)
    tg.file_handler("upload_auto_response_config", upload_auto_response_config)
    tg.file_handler("upload_auto_delivery_config", upload_auto_delivery_config)
    tg.file_handler("upload_main_config", upload_main_config)
    tg.file_handler(CBT.UPLOAD_PLUGIN, upload_plugin)
    tg.file_handler(CBT.SEND_FP_MESSAGE, send_funpay_image)
    tg.file_handler(CBT.UPLOAD_CHAT_IMAGE, upload_chat_image)
    tg.file_handler(CBT.UPLOAD_OFFER_IMAGE, upload_offer_image)
    tg.file_handler(CBT.UPLOAD_BACKUP, upload_backup)


BIND_TO_PRE_INIT = [init_uploader]
