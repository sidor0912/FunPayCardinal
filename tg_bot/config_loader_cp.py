"""
В данном модуле описаны функции для ПУ загрузки / выгрузки конфиг-файлов.
Модуль реализован в виде плагина.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cardinal import Cardinal

from tg_bot import CBT, static_keyboards
from telebot import types
import logging
import os

from locales.localizer import Localizer


logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_config_loader_cp(cardinal: Cardinal, *args):
    tg = cardinal.telegram
    bot = tg.bot

    def open_config_loader(c: types.CallbackQuery):
        if c.message.text is None:
            bot.send_message(c.message.chat.id, _("desc_cfg"), reply_markup=static_keyboards.CONFIGS_UPLOADER())
            bot.answer_callback_query(c.id)
            return
        bot.edit_message_text(_("desc_cfg"), c.message.chat.id, c.message.id,
                              reply_markup=static_keyboards.CONFIGS_UPLOADER())

    def send_config(c: types.CallbackQuery):
        """
        Отправляет файл конфига.
        """
        config_type = c.data.split(":")[1]
        if config_type == "main":
            path, text = "configs/_main.cfg", _("cfg_main")
        elif config_type == "autoResponse":
            path, text = "configs/auto_response.cfg", _("cfg_ar")
        elif config_type == "autoDelivery":
            path, text = "configs/auto_delivery.cfg", _("cfg_ad")
        else:
            bot.answer_callback_query(c.id)
            return

        back_button = types.InlineKeyboardMarkup()\
            .add(types.InlineKeyboardButton(_("gl_back"), callback_data="config_loader"))

        if not os.path.exists(path):
            bot.answer_callback_query(c.id, _("cfg_not_found_err", path), show_alert=True)
            return

        with open(path, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                bot.answer_callback_query(c.id, _("cfg_empty_err", path), show_alert=True)
                return
            f.seek(0)
            bot.send_document(c.message.chat.id, f, caption=text, reply_markup=back_button)

        logger.info(_("log_cfg_downloaded", c.from_user.username, c.from_user.id, path))
        bot.answer_callback_query(c.id)

    tg.cbq_handler(open_config_loader, lambda c: c.data == "config_loader")
    tg.cbq_handler(send_config, lambda c: c.data.startswith(f"{CBT.DOWNLOAD_CFG}:"))


BIND_TO_PRE_INIT = [init_config_loader_cp]
