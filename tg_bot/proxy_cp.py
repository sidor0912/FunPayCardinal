"""
В данном модуле описаны функции для ПУ настроек прокси.
Модуль реализован в виде плагина.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from tg_bot import utils, static_keyboards as skb, keyboards as kb, CBT
import telebot.apihelper
from Utils.cardinal_tools import validate_proxy, cache_proxy_dict, check_proxy
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B

if TYPE_CHECKING:
    from cardinal import Cardinal
from tg_bot import keyboards as kb, CBT
from telebot.types import CallbackQuery, Message
import logging
from threading import Thread
from locales.localizer import Localizer

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_proxy_cp(crd: Cardinal, *args):
    tg = crd.telegram
    bot = tg.bot
    pr_dict = {}

    def check_one_proxy(proxy: str):
        try:
            d = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            pr_dict[proxy] = check_proxy(d)
        except:
            pass

    def check_proxies():
        if crd.MAIN_CFG["Proxy"].getboolean("enable") and crd.MAIN_CFG["Proxy"].getboolean("check"):
            while True:
                for proxy in crd.proxy_dict.values():
                    check_one_proxy(proxy)
                time.sleep(3600)

    Thread(target=check_proxies, daemon=True).start()

    def open_proxy_list(c: CallbackQuery):
        """
        Открывает список прокси.
        """
        offset = int(c.data.split(":")[1])
        text = f'\n\nПрокси: {"вкл." if crd.MAIN_CFG["Proxy"].getboolean("enable") else "выкл."}\n' \
               f'Проверка прокси: {"вкл." if crd.MAIN_CFG["Proxy"].getboolean("check") else "выкл."}'
        bot.edit_message_text(f'{_("desc_proxy")}{text}', c.message.chat.id, c.message.id,
                              reply_markup=kb.proxy(crd, offset, pr_dict))

    def act_add_proxy(c: CallbackQuery):
        """
        Активирует режим ввода прокси для добавления.
        """
        offset = int(c.data.split(":")[-1])
        result = bot.send_message(c.message.chat.id, _("act_proxy"), reply_markup=skb.CLEAR_STATE_BTN())
        crd.telegram.set_state(result.chat.id, result.id, c.from_user.id, CBT.ADD_PROXY, {"offset": offset})
        bot.answer_callback_query(c.id)

    def add_proxy(m: Message):
        """
        Добавляет прокси.
        """
        offset = tg.get_state(m.chat.id, m.from_user.id)["data"]["offset"]
        kb = K().add(B(_("gl_back"), callback_data=f"{CBT.PROXY}:{offset}"))
        tg.clear_state(m.chat.id, m.from_user.id, True)
        proxy = m.text
        try:
            login, password, ip, port = validate_proxy(proxy)
            proxy_str = f"{f'{login}:{password}@' if login and password else ''}{ip}:{port}"
            if proxy_str in crd.proxy_dict.values():
                bot.send_message(m.chat.id, _("proxy_already_exists").format(utils.escape(proxy_str)), reply_markup=kb)
                return
            max_id = max(crd.proxy_dict.keys(), default=-1)
            crd.proxy_dict[max_id + 1] = proxy_str
            cache_proxy_dict(crd.proxy_dict)
            bot.send_message(m.chat.id, _("proxy_added").format(utils.escape(proxy_str)), reply_markup=kb)
            Thread(target=check_one_proxy, args=(proxy_str,), daemon=True).start()
        except ValueError:
            bot.send_message(m.chat.id, _("proxy_format"), reply_markup=kb)
        except:
            bot.send_message(m.chat.id, _("proxy_adding_error"), reply_markup=kb)
            logger.debug("TRACEBACK", exc_info=True)

    def choose_proxy(c: CallbackQuery):
        """
        Выбор прокси из списка.
        """
        q, offset, proxy_id = c.data.split(":")
        offset = int(offset)
        proxy_id = int(proxy_id)
        proxy = crd.proxy_dict.get(proxy_id)
        c.data = f"{CBT.PROXY}:{offset}"
        if not proxy:
            open_proxy_list(c)
            return

        login, password, ip, port = validate_proxy(proxy)
        proxy = f"{f'{login}:{password}@' if login and password else ''}{ip}:{port}"
        proxy = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        crd.MAIN_CFG["Proxy"].update({
            "ip": ip,
            "port": port,
            "login": login,
            "password": password
        })
        crd.save_config(crd.MAIN_CFG, "configs/_main.cfg")
        if crd.MAIN_CFG["Proxy"].getboolean("enable"):
            crd.account.proxy = proxy
        open_proxy_list(c)

    def delete_proxy(c: CallbackQuery):
        """
        Удаление прокси.
        """
        q, offset, proxy_id = c.data.split(":")
        offset = int(offset)
        proxy_id = int(proxy_id)
        c.data = f"{CBT.PROXY}:{offset}"
        if proxy_id in crd.proxy_dict.keys():
            proxy = crd.proxy_dict[proxy_id]
            login, password, ip, port = validate_proxy(proxy)
            now_proxy = crd.account.proxy
            if not now_proxy or now_proxy.get("http").replace("http://", "", 1) != proxy:
                del crd.proxy_dict[proxy_id]
                cache_proxy_dict(crd.proxy_dict)
                if proxy in pr_dict:
                    del pr_dict[proxy]
                logger.info(f"Прокси {proxy} удалены.")
                if str(crd.MAIN_CFG["Proxy"]["ip"]) == str(ip) and str(crd.MAIN_CFG["Proxy"]["login"]) == str(login) \
                        and str(crd.MAIN_CFG["Proxy"]["port"]) == str(port) \
                        and str(crd.MAIN_CFG["Proxy"]["password"]) == str(password):
                    for i in ("password", "port", "login", "ip"):
                        crd.MAIN_CFG["Proxy"][i] = ""
                    crd.save_config(crd.MAIN_CFG, "configs/_main.cfg")
            else:
                bot.answer_callback_query(c.id, _("proxy_undeletable"), show_alert=True)
                return

        open_proxy_list(c)

    tg.cbq_handler(open_proxy_list, lambda c: c.data.startswith(f"{CBT.PROXY}:"))
    tg.cbq_handler(act_add_proxy, lambda c: c.data.startswith(f"{CBT.ADD_PROXY}:"))
    tg.cbq_handler(choose_proxy, lambda c: c.data.startswith(f"{CBT.CHOOSE_PROXY}:"))
    tg.cbq_handler(delete_proxy, lambda c: c.data.startswith(f"{CBT.DELETE_PROXY}:"))
    tg.msg_handler(add_proxy, func=lambda m: crd.telegram.check_state(m.chat.id, m.from_user.id, CBT.ADD_PROXY))


BIND_TO_PRE_INIT = [init_proxy_cp]
