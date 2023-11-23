"""
В данном модуле описаны функции для ПУ шаблонами ответа.
Модуль реализован в виде плагина.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cardinal import Cardinal

from tg_bot import utils, keyboards, CBT
from tg_bot.static_keyboards import CLEAR_STATE_BTN

from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B, Message, CallbackQuery
import logging

from locales.localizer import Localizer


logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_templates_cp(cardinal: Cardinal, *args):
    tg = cardinal.telegram
    bot = tg.bot

    def check_template_exists(template_index: int, message_obj: Message) -> bool:
        """
        Проверяет, существует ли шаблон с переданным индексом.
        Если шаблон не существует - отправляет сообщение с кнопкой обновления списка шаблонов.

        :param template_index: индекс шаблона.
        :param message_obj: экземпляр Telegram-сообщения.

        :return: True, если команда существует, False, если нет.
        """
        if template_index > len(cardinal.telegram.answer_templates) - 1:
            update_button = K().add(B(_("gl_refresh"), callback_data=f"{CBT.TMPLT_LIST}:0"))
            bot.edit_message_text(_("tmplt_not_found_err", template_index), message_obj.chat.id, message_obj.id,
                                  reply_markup=update_button)
            return False
        return True

    def open_templates_list(c: CallbackQuery):
        """
        Открывает список существующих шаблонов ответов.
        """
        offset = int(c.data.split(":")[1])
        bot.edit_message_text(_("desc_tmplt"), c.message.chat.id, c.message.id,
                              reply_markup=keyboards.templates_list(cardinal, offset))
        bot.answer_callback_query(c.id)

    def open_templates_list_in_ans_mode(c: CallbackQuery):
        """
        Открывает список существующих шаблонов ответов (answer_mode).
        """
        split = c.data.split(":")
        offset, node_id, username, prev_page, extra = int(split[1]), int(split[2]), split[3], int(split[4]), split[5:]
        bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                      reply_markup=keyboards.templates_list_ans_mode(cardinal, offset, node_id,
                                                                                     username, prev_page, extra))

    def open_edit_template_cp(c: CallbackQuery):
        split = c.data.split(":")
        template_index, offset = int(split[1]), int(split[2])
        if not check_template_exists(template_index, c.message):
            bot.answer_callback_query(c.id)
            return

        keyboard = keyboards.edit_template(cardinal, template_index, offset)
        template = cardinal.telegram.answer_templates[template_index]

        message = f"""<code>{utils.escape(template)}</code>"""
        bot.edit_message_text(message, c.message.chat.id, c.message.id, reply_markup=keyboard)
        bot.answer_callback_query(c.id)

    def act_add_template(c: CallbackQuery):
        """
        Активирует режим добавления нового шаблона ответа.
        """
        offset = int(c.data.split(":")[1])
        variables = ["v_username", "v_photo"]
        text = f"{_('V_new_template')}\n\n{_('v_list')}:\n" + "\n".join(_(i) for i in variables)
        result = bot.send_message(c.message.chat.id, text, reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.ADD_TMPLT, {"offset": offset})
        bot.answer_callback_query(c.id)

    def add_template(m: Message):
        offset = tg.get_state(m.chat.id, m.from_user.id)["data"]["offset"]
        tg.clear_state(m.chat.id, m.from_user.id, True)
        template = m.text.strip()

        if template in tg.answer_templates:
            error_keyboard = K().row(B(_("gl_back"), callback_data=f"{CBT.TMPLT_LIST}:{offset}"),
                                     B(_("tmplt_add_another"), callback_data=f"{CBT.ADD_TMPLT}:{offset}"))
            bot.reply_to(m, _("tmplt_already_exists_err"), reply_markup=error_keyboard)
            return

        tg.answer_templates.append(template)
        utils.save_answer_templates(tg.answer_templates)
        logger.info(_("log_tmplt_added", m.from_user.username, m.from_user.id, template))

        keyboard = K().row(B(_("gl_back"), callback_data=f"{CBT.TMPLT_LIST}:{offset}"),
                           B(_("tmplt_add_more"), callback_data=f"{CBT.ADD_TMPLT}:{offset}"))
        bot.reply_to(m, _("tmplt_added"), reply_markup=keyboard)

    def del_template(c: CallbackQuery):
        split = c.data.split(":")
        template_index, offset = int(split[1]), int(split[2])
        if not check_template_exists(template_index, c.message):
            bot.answer_callback_query(c.id)
            return

        template = tg.answer_templates[template_index]
        tg.answer_templates.pop(template_index)
        utils.save_answer_templates(tg.answer_templates)
        logger.info(_("log_tmplt_deleted", c.from_user.username, c.from_user.id, template))
        bot.edit_message_text(_("desc_tmplt"), c.message.chat.id, c.message.id,
                              reply_markup=keyboards.templates_list(cardinal, offset))
        bot.answer_callback_query(c.id)

    def send_template(c: CallbackQuery):
        split = c.data.split(":")
        template_index, node_id, username, prev_page, extra = (int(split[1]), int(split[2]), split[3], int(split[4]),
                                                               split[5:])

        if template_index > len(tg.answer_templates) - 1:
            bot.send_message(c.message.chat.id, _("tmplt_not_found_err", template_index))
            if prev_page == 0:
                bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                              reply_markup=keyboards.reply(node_id, username))
            elif prev_page == 1:
                bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                              reply_markup=keyboards.reply(node_id, username, True))
            elif prev_page == 2:
                bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                              reply_markup=keyboards.new_order(extra[0], username, node_id,
                                                                               no_refund=bool(int(extra[1]))))
            bot.answer_callback_query(c.id)
            return

        text = tg.answer_templates[template_index].replace("$username", username)
        result = cardinal.send_message(node_id, text, username)
        if result:
            bot.send_message(c.message.chat.id, _("tmplt_msg_sent", node_id, username, utils.escape(text)),
                             reply_markup=keyboards.reply(node_id, username, again=True, extend=True))
        else:
            bot.send_message(c.message.chat.id, _("msg_sending_error", node_id, username),
                             reply_markup=keyboards.reply(node_id, username, again=True, extend=True))
        bot.answer_callback_query(c.id)

    tg.cbq_handler(open_templates_list, lambda c: c.data.startswith(f"{CBT.TMPLT_LIST}:"))
    tg.cbq_handler(open_templates_list_in_ans_mode, lambda c: c.data.startswith(f"{CBT.TMPLT_LIST_ANS_MODE}:"))
    tg.cbq_handler(open_edit_template_cp, lambda c: c.data.startswith(f"{CBT.EDIT_TMPLT}:"))
    tg.cbq_handler(act_add_template, lambda c: c.data.startswith(f"{CBT.ADD_TMPLT}:"))
    tg.msg_handler(add_template, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.ADD_TMPLT))
    tg.cbq_handler(del_template, lambda c: c.data.startswith(f"{CBT.DEL_TMPLT}:"))
    tg.cbq_handler(send_template, lambda c: c.data.startswith(f"{CBT.SEND_TMPLT}:"))


BIND_TO_PRE_INIT = [init_templates_cp]
