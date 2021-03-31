from telegram.ext import CallbackQueryHandler, CallbackContext
from telegram import Update, ParseMode
from DB import *

from helpers import wrap_tags
from languages import LANGS

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from inlinekeyboards.inlinekeyboardtypes import inline_keyboard_types

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from globalvariables import *

import re
import logging

logger = logging.getLogger()


def get_alert_text(lang, stat, ad_name=None):
    if lang == LANGS[0]:
        text_1 = f"Siz buyurtmani {stat}"
        text_2 = f"Buyurtma {ad_name} tomonidan {stat.lower()}"
    if lang == LANGS[1]:
        text_1 = f"Вы {stat} заказ"
        text_2 = f"Заказ был {stat.lower()} {ad_name}ом"
    if lang == LANGS[2]:
        text_1 = f"Сиз буюртмани {stat}"
        text_2 = f"Буюртма {ad_name} томонидан {stat.lower()}"

    return_text = text_1

    if ad_name:
        return_text = text_2

    return return_text


def inline_keyboards_handler_callback(update: Update, context: CallbackContext):
    # with open('jsons/callback_query.json', 'w') as callback_query_file:
    #     callback_query_file.write(callback_query.to_json())
    user = get_user(update.effective_user.id)

    callback_query = update.callback_query
    data = callback_query.data

    # for change language
    lang_obj = re.search(r'^(uz|ru|cy)$', data)

    if user:
        if lang_obj:
            new_lang = lang_obj.group()
            update_user_info(user[ID], lang=new_lang)
            flag_uzb = '🇺🇿'
            flag_rus = '🇷🇺'
            flag = flag_rus if new_lang == 'ru' else flag_uzb

            if new_lang == 'uz':
                text = f"Til"
                reply_text = "Til o'zgartirildi"
            if new_lang == 'ru':
                text = "Язык"
                reply_text = "Язык был изменен"
            if new_lang == 'cy':
                text = "Тил"
                reply_text = "Тил ўзгартирилди"

            text = f'{text}: {inline_keyboard_types[langs_keyboard][new_lang]} {flag}'

            main_menu_keyboard = admin_menu_keyboard if user[IS_ADMIN] else client_menu_keyboard
            main_menu_keyboard = ReplyKeyboard(main_menu_keyboard, new_lang).get_keyboard()

            callback_query.edit_message_text(text)
            callback_query.message.reply_text(reply_text, reply_markup=main_menu_keyboard)

        if user[IS_ADMIN]:
            confirm_object = re.search(r'^confirm_\d+$', data)
            cancel_object = re.search(r'^cancel_\d+$', data)
            confirm_yes_no_object = re.search(r'confirm_[yn]_\d+$', data)
            cancel_yes_no_object = re.search(r'cancel_[yn]_\d+$', data)
            # match_obj_3 = re.search(r'^w_\d+$', data)
            # match_obj_4 = re.search(r'^h_w_\d+$', data)

            if confirm_object or cancel_object:
                inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG], data=data.split('_')).get_keyboard()
                callback_query.message.reply_markup.inline_keyboard.pop(0)
                callback_query.message.reply_markup.inline_keyboard[0] = inline_keyboard.inline_keyboard[0]

                callback_query.answer()
                callback_query.edit_message_reply_markup(callback_query.message.reply_markup)

            elif confirm_yes_no_object or cancel_yes_no_object:
                data = data.split('_')
                status = data[0]
                action = data[1]
                order_id = data[-1]

                if action == 'n':
                    inline_keyboard = InlineKeyboard(orders_keyboard, user[LANG], data=[None, order_id]).get_keyboard()
                    callback_query.message.reply_markup.inline_keyboard.pop(0)
                    callback_query.message.reply_markup.inline_keyboard.insert(0, inline_keyboard.inline_keyboard[1])
                    callback_query.message.reply_markup.inline_keyboard.insert(0, inline_keyboard.inline_keyboard[0])

                    callback_query.answer()
                    callback_query.edit_message_reply_markup(callback_query.message.reply_markup)

                if action == 'y':
                    update_status = 'confirmed' if status == 'confirm' else 'canceled'

                    confirm_status_icon = "🟢"
                    cancel_status_icon = "🔴"

                    if user[LANG] == LANGS[0]:
                        confirm_status_text = "Tasqidlangan"
                        cancel_status_text = "Bekor qilingan"
                        confirm = "tasdiqladingiz"
                        cancel = "bekor qildingiz"
                    if user[LANG] == LANGS[1]:
                        confirm_status_text = "Принят"
                        cancel_status_text = "Отменен"
                        confirm = "подтвердили"
                        cancel = "отменили"
                    if user[LANG] == LANGS[2]:
                        confirm_status_text = "Тасқидланган"
                        cancel_status_text = "Бекор қилинган"
                        confirm = "тасдиқладингиз"
                        cancel = "бекор қилдингиз"

                    # Get order
                    order = get_order(order_id)

                    order_status_in_db = order[STATUS]
                    # status_updated_by_admin_id is None by default
                    status_updated_by_admin_id = order['updated_by_admin_id']

                    if order_status_in_db == 'waiting':
                        update_order_status(update_status, order_id)
                        # update updated_by_admin_id
                        update_order_admin_id(user[ID], order_id)
                        x = update_status

                        # Get order client
                        order_client = get_user(order[USER_ID])

                        if order_client[LANG] == LANGS[0]:
                            confirmed_text = "tasdiqlandi 😃"
                            canceled_text = "bekor qilindi 😬"
                            stat = confirmed_text if update_status == 'confirmed' else canceled_text
                            reply_text_client = f"Hurmatli, {wrap_tags(order_client[FULLNAME])}\n" \
                                                f"Sizning buyurtmangiz #{order_id} {stat}!"
                        if order_client[LANG] == LANGS[1]:
                            confirmed_text = "подтверждено 😃"
                            canceled_text = "отменен 😬"
                            stat = confirmed_text if update_status == 'confirmed' else canceled_text
                            reply_text_client = f"Уважаемый, {wrap_tags(order_client[FULLNAME])}\n" \
                                                f"Ваш заказ #{order_id} {stat}!"
                        if order_client[LANG] == LANGS[2]:
                            confirmed_text = "тасдиқланди 😃"
                            canceled_text = "бекор қилинди 😬"
                            stat = confirmed_text if update_status == 'confirmed' else canceled_text
                            reply_text_client = f"Ҳурматли, {wrap_tags(order_client[FULLNAME])}\n" \
                                                f"Сизнинг буюртмангиз #{order_id} {stat}!"

                        # Send message to order client
                        context.bot.send_message(order_client[TG_ID], reply_text_client,
                                                 reply_to_message_id=order[MESSAGE_ID],
                                                 allow_sending_without_reply=True, parse_mode=ParseMode.HTML)

                    else:
                        admin_name = get_user(status_updated_by_admin_id)[FULLNAME]
                        x = order_status_in_db

                    if x == 'confirmed':
                        s = confirm_status_text
                        icon = confirm_status_icon
                        c = confirm
                        ic = "✅"
                    else:
                        s = cancel_status_text
                        icon = cancel_status_icon
                        c = cancel
                        ic = "❌"

                    if status_updated_by_admin_id:
                        alert_text = get_alert_text(user[LANG], s, admin_name)
                    else:
                        alert_text = get_alert_text(user[LANG], c)

                    alert_text = f'{ic} {alert_text}'
                    callback_query.answer(alert_text, show_alert=True)

                    text = callback_query.message.text.split('\n')
                    text[-1] = f'<b>Status: {s} {icon}</b>'
                    text = '\n'.join(text)

                    callback_query.message.reply_markup.inline_keyboard.pop(0)
                    callback_query.edit_message_text(text, parse_mode=ParseMode.HTML,
                                                     reply_markup=callback_query.message.reply_markup)

        elif not user[IS_ADMIN]:
            pass

        else:
            callback_query.answer("Siz aktiv admin emassiz !!!\n"
                                  "Siz siz bu operatsiyani bajara olmaysiz !!!\n\n"
                                  "😬😬😬", show_alert=True)

    else:

        reply_text = "Siz ro'yxatdan o'tmagansiz !\nBuning uchun /start ni bosing\n\n" \
                     "Вы не зарегистрированы !\nДля этого нажмите /start\n\n" \
                     "Сиз рўйхатдан ўтмагансиз !\nБунинг учун /start ни босинг"

        reply_text = f'⚠ {reply_text}'
        update.message.reply_text(reply_text)

    # logger.info('user_data: %s', user_data)


callback_query_handler = CallbackQueryHandler(inline_keyboards_handler_callback)
