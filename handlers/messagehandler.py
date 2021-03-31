from telegram.ext import Filters, MessageHandler, CallbackContext
from telegram import Update, ParseMode

from DB import *
from helpers import wrap_tags
from config import BOT_USERNAME, SMM_ADMINS

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardtypes import reply_keyboard_types
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from inlinekeyboards.inlinekeyboardtypes import inline_keyboard_types

from globalvariables import *
from languages import LANGS
import json


def message_handler_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)

    full_text = update.message.text
    text = full_text.split(maxsplit=1)[-1]

    if user:

        if user[IS_ADMIN]:

            # New orders
            if text == reply_keyboard_types[admin_menu_keyboard][user[LANG]][1]:

                if user[TG_ID] in SMM_ADMINS:

                    if user[LANG] == LANGS[0]:
                        text = "Kechirasiz, siz yangi buyurtmalarni ko'ra olmaysiz"
                    if user[LANG] == LANGS[1]:
                        text = "К сожалению, вы не можете видеть новые заказы"
                    if user[LANG] == LANGS[2]:
                        text = "Кечирасиз, сиз янги буюртмаларни кўра олмайсиз"

                    text = f'❗ {text} 😬'
                    update.message.reply_text(text)

                else:
                    waiting_orders = get_orders_by_status(status='waiting')

                    if waiting_orders:

                        for order in waiting_orders:
                            order_itmes = get_order_items(order[ID])
                            client = get_user(order[USER_ID])
                            geo = json.loads(order[GEOLOCATION]) if order[GEOLOCATION] else None

                            if user[LANG] == LANGS[0]:
                                label = "Yangi buyurtma"
                                nomer_text = "Telefon raqam"
                                tg_account_text = "Telegram"
                                delivery_method_text = "Yetkazib berish turi"
                                order_coomment_text = "Buyurtmaga izoh"
                                payment_method_text = "To'lov turi"
                                currency = "so'm"
                                delivery_method = "Yetkazib berish"
                                payment_method = "Naqd pul"
                                s = "Kutish"
                            if user[LANG] == LANGS[1]:
                                label = "Новый заказ"
                                nomer_text = "Телефон номер"
                                tg_account_text = "Telegram"
                                delivery_method_text = "Тип доставки"
                                order_coomment_text = "Комментарий к заказу"
                                payment_method_text = "Тип платежа"
                                currency = 'сум'
                                delivery_method = "Доставка"
                                payment_method = "Наличные"
                                s = "Ожидание"
                            if user[LANG] == LANGS[2]:
                                label = "Янги буюртма"
                                nomer_text = "Телефон рақам"
                                tg_account_text = "Telegram"
                                delivery_method_text = "Етказиб бериш тури"
                                order_coomment_text = "Буюртмага изоҳ"
                                payment_method_text = "Тўлов тури"
                                currency = 'сўм'
                                delivery_method = "Етказиб бериш"
                                payment_method = "Нақд пул"
                                s = "Кутиш"
                            unit = inline_keyboard_types[order_keyboard][user[LANG]][3]
                            num = 1
                            basket_text = ''
                            icon = '🟡'
                            for item in order_itmes:
                                food_data_from_db = get_food_by_id(item['product_id'], item['product_type'])
                                item_price = f'{item[PRICE]:,}'.replace(',', ' ')
                                item_total_price = f'{item["total_price"]:,}'.replace(',', ' ')

                                basket_text += f'{num}. {food_data_from_db[f"name_{user[LANG]}"]}\n'
                                basket_text += f'\t\t{item["quantity"]} {unit} x {item_price} {currency} = {item_total_price} {currency}\n' \
                                               f'______________________________\n'
                                num += 1

                            total_sum_text = f'{inline_keyboard_types[basket_keyboard][user[LANG]][1]}: ' \
                                             f'{order["total_sum"]:,}'.replace(',', ' ') + f' {currency}'
                            text_for_admin = f'🆔 {order[ID]} [{label}]\n\n'

                            tg_account = f'{tg_account_text}: @{client[USERNAME]}\n' if client[USERNAME] else ''
                            text_for_admin += f"{nomer_text}: {wrap_tags(order[PHONE_NUMBER])}\n" \
                                              f"{tg_account}" \
                                              f"{delivery_method_text}: {'🚕 ' + delivery_method}\n" \
                                              f"{payment_method_text}: {'💰 ' + payment_method}\n" \
                                              f"{order_coomment_text}: {order['comment']}\n\n"

                            inline_keyboard = InlineKeyboard(orders_keyboard, user[LANG],
                                                             data=[geo, order[ID]]).get_keyboard()
                            text_for_admin += basket_text + total_sum_text + f'\n\n<b>Status: {s} {icon}</b>'
                            update.message.reply_html(text_for_admin, reply_markup=inline_keyboard)

                    else:
                        if user[LANG] == LANGS[0]:
                            reply_text = "Yangi buyurtmalar yo'q!"
                        if user[LANG] == LANGS[1]:
                            reply_text = "Новых заказов нет!"
                        if user[LANG] == LANGS[2]:
                            reply_text = "Янги буюртмалар йўқ!"

                        reply_keyboard = ReplyKeyboard(admin_menu_keyboard, user[LANG]).get_keyboard()
                        update.message.reply_text(reply_text, reply_markup=reply_keyboard)

            # History
            # elif text == reply_keyboard_types[admin_menu_keyboard][user[LANG]][3]:
            #     orders = get_orders_by_status(('confirmed', 'canceled'))
            #
            #     if orders:
            #
            #         if user[LANG] == LANGS[0]:
            #             label = "Tarix"
            #         if user[LANG] == LANGS[1]:
            #             label = "История"
            #         if user[LANG] == LANGS[2]:
            #             label = "Тарих"
            #
            #     else:
            #         if user[LANG] == LANGS[0]:
            #             reply_text = "История пуста!"
            #         if user[LANG] == LANGS[1]:
            #             reply_text = "Новых заказов нет!"
            #         if user[LANG] == LANGS[2]:
            #             reply_text = "Тарих  бўш!"
            #
            #         reply_keyboard = ReplyKeyboard(admin_menu_keyboard, user[LANG]).get_keyboard()
            #         update.message.reply_text(reply_text, reply_markup=reply_keyboard)

            # Settings button
            elif text == reply_keyboard_types[client_menu_keyboard][user[LANG]][4]:
                keyboard = ReplyKeyboard(settings_keyboard, user[LANG]).get_keyboard()
                update.message.reply_text(full_text, reply_markup=keyboard)

            # Change lang button
            elif text == reply_keyboard_types[settings_keyboard][user[LANG]][2]:
                if user[LANG] == LANGS[0]:
                    text = "Tilni tanlang"

                if user[LANG] == LANGS[1]:
                    text = "Выберите язык"

                if user[LANG] == LANGS[2]:
                    text = "Тилни танланг"

                keyboard = InlineKeyboard(langs_keyboard).get_keyboard()
                update.message.reply_text(text, reply_markup=keyboard)

            # Back button
            elif text == reply_keyboard_types[settings_keyboard][user[LANG]][3]:
                main_menu_keyboard = admin_menu_keyboard if user[IS_ADMIN] else client_menu_keyboard
                main_menu_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()

                update.message.reply_text(full_text, reply_markup=main_menu_keyboard)

        else:

            # Contact us
            if text == reply_keyboard_types[client_menu_keyboard][user[LANG]][3]:
                phone_1 = '(93)-675-00-86'
                phone_2 = '(94)-656-00-86'
                phone_3 = '(94)-656-00-46'
                tg_channel = 'https://t.me/payshanbaosh'

                if user[LANG] == LANGS[0]:
                    address_text = "Bizning manzil"
                    address = "Yakkasaroy tumani, Qushbegi ko'chasi 12 uy"
                    phone_text = "Telefonlar"
                    work_day_text = "Ish tartibi"
                    work_days = "Xar kuni"
                    work_hours_text = "11:00 dan - 15:00 gacha"
                    tg_channel_text = "Telegram kanalimiz"
                    bot_creator_text = "Bot yaratuvchisi"
                    bot_contacts_text = "Bot yaratish uchun @cardel_admin ga murojaat qiling"

                if user[LANG] == LANGS[1]:
                    address_text = "Наш адрес"
                    address = "Яккасарайский район, улица Кушбеги 12"
                    phone_text = "Наши телефоны"
                    work_day_text = "График работы"
                    work_days = "Каждый день"
                    work_hours_text = "c 11:00 до 15:00"
                    tg_channel_text = "Наш Telegram канал"
                    bot_creator_text = "Создатель бота"
                    bot_contacts_text = "Свяжитесь с @cardel_admin, чтобы создать бота"

                if user[LANG] == LANGS[2]:
                    address_text = "Бизнинг манзил"
                    address = "Яккасарой тумани, Кушбеги кучаси 12 уй"
                    phone_text = "Телефонларимиз"
                    work_day_text = "Иш тартиби"
                    work_days = "Хар куни"
                    work_hours_text = "11:00 дан - 15:00 гача"
                    tg_channel_text = "Телеграм каналимиз"
                    bot_creator_text = "Бот яратувчиси"
                    bot_contacts_text = "Бот яратиш учун @cardel_admin га мурожаат қилинг"

                text = f"{address_text}:\n" \
                       f"📍  {wrap_tags(address)}\n\n" \
                       f"{phone_text}:\n" \
                       f"📞  {wrap_tags(phone_1)}\n" \
                       f"📞  {wrap_tags(phone_2)}\n" \
                       f"📞  {wrap_tags(phone_3)}\n\n" \
                       f"{work_day_text}:\n" \
                       f"🕒  {wrap_tags(work_days + ' ' + work_hours_text)}\n\n" \
                       f"📷  Instagram: {wrap_tags('https://www.instagram.com/payshanba_zigirosh')}\n" \
                       f"📣  {tg_channel_text}: {wrap_tags(tg_channel)}\n\n" \
                       f"🌐 {bot_creator_text}: Cardel Group ™ ®\n" \
                       f"ℹ  {bot_contacts_text} 😉\n\n" \
                       f"🤖  @{BOT_USERNAME} ©"

                keyboard = InlineKeyboard(geo_keyboard, user[LANG]).get_keyboard()

                update.message.reply_photo(
                    photo='https://lh5.googleusercontent.com/p/AF1QipMUSOwybMWD0_Z3v4HLpQbfCU2IwYgwxU1Y1wdi=w426-h240-k-no',
                    caption=text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                # update.message.reply_html(text, reply_markup=keyboard)

            # Settings button
            elif text == reply_keyboard_types[client_menu_keyboard][user[LANG]][4]:
                keyboard = ReplyKeyboard(settings_keyboard, user[LANG]).get_keyboard()
                update.message.reply_text(full_text, reply_markup=keyboard)

            # Change lang button
            elif text == reply_keyboard_types[settings_keyboard][user[LANG]][2]:
                if user[LANG] == LANGS[0]:
                    text = "Tilni tanlang"

                if user[LANG] == LANGS[1]:
                    text = "Выберите язык"

                if user[LANG] == LANGS[2]:
                    text = "Тилни танланг"

                keyboard = InlineKeyboard(langs_keyboard).get_keyboard()
                update.message.reply_text(text, reply_markup=keyboard)

            # Back button
            elif text == reply_keyboard_types[settings_keyboard][user[LANG]][3]:
                main_menu_keyboard = admin_menu_keyboard if user[IS_ADMIN] else client_menu_keyboard
                main_menu_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()

                update.message.reply_text(full_text, reply_markup=main_menu_keyboard)

            else:
                thinking_emoji = '🤔🤔🤔'
                if user[LANG] == LANGS[0]:
                    text = "/start ni bosing !"
                if user[LANG] == LANGS[1]:
                    text = "Нажмите /start !"
                if user[LANG] == LANGS[2]:
                    text = "/start ни босинг !"
                text = f'{thinking_emoji}\n\n' \
                       f'❗ {text}'

                update.message.reply_text(text, quote=True)

    else:

        reply_text = "Siz ro'yxatdan o'tmagansiz !\nBuning uchun /start ni bosing\n\n" \
                     "Вы не зарегистрированы !\nДля этого нажмите /start\n\n" \
                     "Сиз рўйхатдан ўтмагансиз !\nБунинг учун /start ни босинг"

        reply_text = f'⚠ {reply_text}'
        update.message.reply_text(reply_text)


message_handler = MessageHandler(Filters.text & (~ Filters.command) & (~Filters.update.edited_message),
                                 message_handler_callback)
