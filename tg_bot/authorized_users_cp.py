"""
В данном модуле описаны функции для ПУ настроек авторизованных пользователей.
Модуль реализован в виде плагина.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import telebot.apihelper

if TYPE_CHECKING:
    from cardinal import Cardinal
from tg_bot import keyboards as kb, CBT
from telebot.types import CallbackQuery
import logging

from locales.localizer import Localizer

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_authorized_users_cp(crd: Cardinal, *args):
    tg = crd.telegram
    bot = tg.bot

    def open_authorized_users_list(c: CallbackQuery):
        """
        Открывает список пользователей, авторизованных в ПУ.
        """
        offset = int(c.data.split(":")[1])
        bot.edit_message_text(_("desc_au"), c.message.chat.id, c.message.id,
                              reply_markup=kb.authorized_users(crd, offset))

    def open_authorized_user_settings(c: CallbackQuery):
        """
        Отркрывает настройки конкретного пользователя
        """
        __, user_id, offset = c.data.split(":")
        user_id = int(user_id)
        offset = int(offset)
        text = _("au_user_settings", f"<a href='tg:user?id={user_id}'>{user_id}</a>")
        try:
            bot.edit_message_text(text, c.message.chat.id,
                                  c.message.id,
                                  reply_markup=kb.authorized_user_settings(crd, user_id, offset, True))
        except telebot.apihelper.ApiTelegramException:
            logger.warning(_("crd_tg_au_err", user_id))
            logger.debug("TRACEBACK", exc_info=True)
            bot.edit_message_text(text, c.message.chat.id, c.message.id,
                                  reply_markup=kb.authorized_user_settings(crd, user_id, offset, False))

    tg.cbq_handler(open_authorized_users_list, lambda c: c.data.startswith(f"{CBT.AUTHORIZED_USERS}:"))
    tg.cbq_handler(open_authorized_user_settings, lambda c: c.data.startswith(f"{CBT.AUTHORIZED_USER_SETTINGS}:"))


BIND_TO_PRE_INIT = [init_authorized_users_cp]
