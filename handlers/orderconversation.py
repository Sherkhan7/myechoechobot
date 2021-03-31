from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, ParseMode, InputMediaPhoto, \
    TelegramError
from telegram.ext import MessageHandler, ConversationHandler, CallbackContext, Filters, CallbackQueryHandler

from config import PHOTOS_URL, ADMINS
from helpers import get_user, wrap_tags
from DB import get_food_by_data, get_user_basket, update_user_basket_data, insert_order_items, insert_data
from languages import LANGS
from globalvariables import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from replykeyboards.replykeyboardtypes import reply_keyboard_types

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from inlinekeyboards.inlinekeyboardtypes import inline_keyboard_types

from layouts import get_phone_number_layout
from filters import phone_number_filter
import re
import json
import logging
import datetime

logger = logging.getLogger()

MENUS, CHECK_PHONE_NUMBER, ORDER_DELIVERY_METHOD, ORDER_COMMENT, ORDER, ORDER_PAYMENT_METHOD, LAGANS, ORDER_TOTAL_SUM = (
    'menus', 'check_phone_number', 'order_delivery_method', 'order_comment', 'order', 'order_payment_method',
    'lagans', 'order_total_sum'
)

main_menu_pattern = "^(.(?!(Bosh menyu|Главное меню|Бош меню)))*$"


def order_conversation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    full_text = update.message.text
    text = full_text.split(maxsplit=1)[-1]

    if text == "Tasdiqlash" or text == "Подтверждение" or text == "Тасдиқлаш":
        if user[LANG] == LANGS[0]:
            text = f"Buyurtmani ushbu {wrap_tags(user[PHONE_NUMBER])} telefon raqami bilan bermoqchimisiz ?\n\n" \
                   f"Aks holda, iltimos, {get_phone_number_layout(user[LANG])}"
        if user[LANG] == LANGS[1]:
            text = f"Хотите разместить свой заказ по этому номеру телефона {wrap_tags(user[PHONE_NUMBER])} ?\n\n" \
                   f"В противном случае, {get_phone_number_layout(user[LANG])}"

        if user[LANG] == LANGS[2]:
            text = f"Буюртмани ушбу {wrap_tags(user[PHONE_NUMBER])} телефон рақами билан бермоқчимисиз ?\n\n" \
                   f"Aкс ҳолда, илтимос, {get_phone_number_layout(user[LANG])}"

        yes_text = f"✅ {inline_keyboard_types[yes_no_keyboard][user[LANG]][1]}"
        main_menu_text = f"🏠 {reply_keyboard_types[menu_keyboard][user[LANG]][6]}"

        if MESSAGE_ID in user_data:
            context.bot.delete_message(user[TG_ID], user_data[MESSAGE_ID])
            user_data.pop(MESSAGE_ID)

        if 'food_state' in user_data:
            user_data.pop('food_state')

        reply_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(yes_text)],
            [KeyboardButton(main_menu_text)],
        ], resize_keyboard=True)
        update.message.reply_html(text, reply_markup=reply_keyboard)

        user_data[STATE] = CHECK_PHONE_NUMBER

        # logger.info('user_data: %s', user_data)
        return CHECK_PHONE_NUMBER

    elif text == "Savatni tozalash" or text == "Саватни тозалаш" or text == "Очистить корзину":
        update_user_basket_data(None, user[ID])

        if user[LANG] == LANGS[0]:
            text = "Savat tozalandi!"
        if user[LANG] == LANGS[1]:
            text = "Корзина очищена!"
        if user[LANG] == LANGS[2]:
            text = "Сават тозаланди!"

        text = f'🧹  {text}'

        if MESSAGE_ID in user_data:
            context.bot.delete_message(user[TG_ID], user_data[MESSAGE_ID])

        reply_keyboard = ReplyKeyboard(client_menu_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        # logger.info('user_data: %s', user_data)
        user_data.clear()
        return ConversationHandler.END


def basket_callback_qery_handler(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    minus_obj = re.search('^minus', callback_query.data)
    plus_obj = re.search('^plus', callback_query.data)
    delete_obj = re.search('^delete', callback_query.data)
    wanted_obj = re.search(r'^w_\d+$', callback_query.data)

    if user[LANG] == LANGS[0]:
        price_text = 'Narx'
        currency = "so'm"

    if user[LANG] == LANGS[1]:
        price_text = 'Цена'
        currency = 'сум'

    if user[LANG] == LANGS[2]:
        price_text = 'Нарх'
        currency = 'сўм'
    unit = inline_keyboard_types[order_keyboard][user[LANG]][3]

    if minus_obj or plus_obj or delete_obj:
        current_quantity = callback_query.message.reply_markup.inline_keyboard[0][1].text
        current_quantity = int(current_quantity.split()[0])

        data = callback_query.data.split('|')
        action = data[0]
        food_data = data[1]
        food_type = data[-1]

        # Dict object
        user_basket_data = json.loads(get_user_basket(user[ID])[DATA])

        if food_type != DISHES:
            if action == 'minus':
                new_quantity = current_quantity - 1
            elif action == 'plus':
                new_quantity = current_quantity + 1
            elif action == 'delete':
                new_quantity = None

            if new_quantity == 0 or action == 'delete':

                if food_type == 'plovs' or food_type == 'salads' or food_type == 'additionals':
                    dish_type = None

                    if food_type == 'plovs' or food_data == "pay_0.5" or food_data == "pay_1" or \
                            food_data == "gosht_0.5" or food_data == "gosht_1":
                        dish_type = 'dish_osh'

                    elif food_type == 'salads':
                        dish_type = 'dish_salad'

                    # Delete Dishes
                    if dish_type in user_basket_data[DISHES]:
                        if user_basket_data[DISHES][dish_type] > current_quantity:
                            user_basket_data[DISHES][dish_type] -= current_quantity

                        else:
                            del user_basket_data[DISHES][dish_type]

                del user_basket_data[food_type][food_data]

                # Add osh dishes if lagan removes
                if food_type == 'lagans' and len(user_basket_data['lagans']) == 0:
                    if 'plovs' in user_basket_data:
                        user_basket_data[DISHES]['dish_osh'] = sum(list(user_basket_data['plovs'].values()))

                    if 'additionals' in user_basket_data:
                        for key in user_basket_data['additionals'].keys():
                            if key == 'pay_1' or key == 'pay_0.5' or key == 'gosht_1' or key == 'gosht_0.5':
                                user_basket_data[DISHES]['dish_osh'] += user_basket_data['additionals'][key]

            else:
                if food_type == 'plovs' or food_type == 'salads' or food_type == 'additionals':
                    dish_type = None

                    if food_type == 'plovs' or food_data == "pay_0.5" or food_data == "pay_1" or \
                            food_data == "gosht_0.5" or food_data == "gosht_1":
                        dish_type = 'dish_osh'

                    elif food_type == 'salads':
                        dish_type = 'dish_salad'

                    if dish_type in user_basket_data[DISHES]:
                        if action == 'minus':
                            user_basket_data[DISHES][dish_type] -= 1
                        elif action == 'plus':
                            user_basket_data[DISHES][dish_type] += 1

                # change to new quantity
                user_basket_data[food_type][food_data] = new_quantity

            # update user basket data
            json_data = json.dumps(user_basket_data)
            update_user_basket_data(json_data, user[TG_ID])

            foods_list = []
            total_sum = 0

            for food_type, food_data_dict in user_basket_data.items():
                for food_data, food_quantity in food_data_dict.items():
                    foods_list.append({'food_data': food_data, 'food_type': food_type, 'quantity': food_quantity})
                    total_sum += get_food_by_data(food_data, food_type)[PRICE] * food_quantity

            wanted = int(callback_query.message.reply_markup.inline_keyboard[1][1].text.split('/')[0])

            if wanted > len(foods_list):
                wanted = 1

            if not foods_list:
                if user[LANG] == LANGS[0]:
                    text = "Xarid savatingiz bo'sh"
                if user[LANG] == LANGS[1]:
                    text = "Ваша корзина пуста"
                if user[LANG] == LANGS[2]:
                    text = "Харид саватингиз бўш"

                reply_text = f'🙈  {text}!'
                update_user_basket_data(None, user[TG_ID])

                callback_query.delete_message()

                reply_keyboard = ReplyKeyboard(client_menu_keyboard, user[LANG]).get_keyboard()
                callback_query.message.reply_text(reply_text, reply_markup=reply_keyboard)
                user_data.clear()

                return ConversationHandler.END

            wanted_item = foods_list[wanted - 1]
            wanted_item_data = get_food_by_data(wanted_item['food_data'], wanted_item['food_type'])

            if new_quantity is None:
                counted_price = wanted_item_data[PRICE] * wanted_item['quantity']
            else:
                counted_price = wanted_item_data[PRICE] * new_quantity

            counted_price = f'{counted_price:,}'.replace(',', ' ')
            price = f'{wanted_item_data[PRICE]:,}'.replace(',', ' ')
            price_text = f'{price_text}: {new_quantity} {unit} x {price} {currency} = {counted_price} {currency}'
            total_sum = f'{total_sum:,}'.replace(',', ' ') + f' {currency}'

            caption = f'{wanted_item_data[f"name_{user[LANG]}"]}\n\n' \
                      f'{wanted_item_data[f"description_{user[LANG]}"]}\n\n' \
                      f'{wrap_tags(price_text)}'

            data = dict()
            data['total_sum'] = total_sum
            data['food_data'] = wanted_item
            data['wanted'] = wanted
            data['unit'] = unit
            data['length'] = len(foods_list)
            inline_keyboard = InlineKeyboard(basket_keyboard, user[LANG], data=data).get_keyboard()

            callback_query.answer('Please wait ... ⏳')
            if new_quantity is None:
                media_photo = InputMediaPhoto(PHOTOS_URL + wanted_item['food_type'] + f'/{wanted_item_data[PHOTO]}',
                                              caption=caption,
                                              parse_mode=ParseMode.HTML)
                callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)
            else:
                callback_query.edit_message_caption(caption=caption, reply_markup=inline_keyboard,
                                                    parse_mode=ParseMode.HTML)

            return ORDER

        else:
            if user[LANG] == LANGS[0]:
                text = "Plastik idishlarni ko'paytirish/kamaytirish/o'chirish mumkin emas"
            if user[LANG] == LANGS[1]:
                text = "Пластиковые контейнеры нельзя увеличивать/уменьшать/снимать"
            if user[LANG] == LANGS[2]:
                text = "Пластик идишларни кўпайтириш/камайтириш/ўчириш мумкин эмас"

            text = f'⚠  {text}!'
            callback_query.answer(text, show_alert=True)

    elif wanted_obj:
        wanted = int(callback_query.data.split('_')[-1])
        callback_query.answer()
        # Dict object
        user_basket_data = json.loads(get_user_basket(user[ID])[DATA])

        foods_list = []
        total_sum = 0

        for food_type, food_data_dict in user_basket_data.items():
            for food_data, food_quantity in food_data_dict.items():
                foods_list.append({'food_data': food_data, 'food_type': food_type, 'quantity': food_quantity})
                total_sum += get_food_by_data(food_data, food_type)[PRICE] * food_quantity

        wanted_item = foods_list[wanted - 1]
        wanted_item_data = get_food_by_data(wanted_item['food_data'], wanted_item['food_type'])
        photo_url = PHOTOS_URL + f'{wanted_item["food_type"]}/{wanted_item_data[PHOTO]}'
        counted_price = wanted_item_data[PRICE] * wanted_item['quantity']
        counted_price = f'{counted_price:,}'.replace(',', ' ')
        price = f'{wanted_item_data[PRICE]:,}'.replace(',', ' ')
        total_sum = f'{total_sum:,}'.replace(',', ' ') + f' {currency}'
        price_text = f'{price_text}: {wanted_item["quantity"]} {unit} x {price} {currency} = {counted_price} {currency}'

        caption = f'{wanted_item_data[f"name_{user[LANG]}"]}\n\n' \
                  f'{wanted_item_data[f"description_{user[LANG]}"]}\n\n' \
                  f'{wrap_tags(price_text)}'

        data = dict()
        data['total_sum'] = total_sum
        data['food_data'] = wanted_item
        data['unit'] = unit
        data['wanted'] = wanted
        data['length'] = len(foods_list)
        inline_keyboard = InlineKeyboard(basket_keyboard, user[LANG], data=data).get_keyboard()
        media_photo = InputMediaPhoto(photo_url, caption=caption, parse_mode=ParseMode.HTML)

        # When user clicks the InlineKeyboardButton fast so many times TelegramError will be thrown
        try:
            callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)
        except TelegramError:
            pass

        return ORDER

    else:
        callback_query.answer()


def check_phone_number(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    full_text = update.message.text
    text = full_text.split(maxsplit=1)[-1]

    yes_search = re.search("Ha|Да|Ҳа", text)

    if yes_search or phone_number_filter(full_text):
        user_data[ORDER_PHONE_NUMBER] = user[PHONE_NUMBER]

        if user[LANG] == LANGS[0]:
            text = "Buyurtmani qanday qabul qilishni xohlaysiz?"
            delivery_text = "Yetkazib berish"

        if user[LANG] == LANGS[1]:
            text = "Как вы хотите получить свой заказ?"
            delivery_text = "Доставка"

        if user[LANG] == LANGS[2]:
            text = "Буюртмани қандай қабул қилишни хоҳлайсиз?"
            delivery_text = "Етказиб бериш"

        delivery_text = f'🚕 {delivery_text}'
        main_menu_text = f'🏠 {reply_keyboard_types[menu_keyboard][user[LANG]][6]}'

        reply_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(delivery_text)],
            [KeyboardButton(main_menu_text)],
        ], resize_keyboard=True)

        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data[STATE] = ORDER_DELIVERY_METHOD

        # logger.info('user_data: %s', user_data)
        return ORDER_DELIVERY_METHOD

    else:
        if user[LANG] == LANGS[0]:
            error_text = "Telefon raqami xato formatda yuborildi!\n"
        if user[LANG] == LANGS[1]:
            error_text = "Номер телефона введен в неправильном формате!\n"
        if user[LANG] == LANGS[2]:
            error_text = "Телефон рақами хато форматда юборилди!\n"

        layout = get_phone_number_layout(user[LANG])
        error_text = f'❌ {error_text}' + layout

        update.message.reply_html(error_text, quote=True)

        # logger.info('user_data: %s', user_data)
        return user_data[STATE]


def delivery_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    full_text = update.message.text
    text = full_text.split(maxsplit=1)[-1]

    delivery_search = re.search("Yetkazib berish|Доставка|Етказиб бериш", text)

    if delivery_search:
        user_data[ORDER_DELIVERY_METHOD] = full_text

        if user[LANG] == LANGS[0]:
            text = "Buyurtmani qayerga yetkazib berishimizni ko'rsating"
        if user[LANG] == LANGS[1]:
            text = "Укажите куда нужно доставить Ваш заказ"
        if user[LANG] == LANGS[2]:
            text = "Буюртмани қаерга етказиб беришимизни кўрсатинг"

        reply_keyboard = ReplyKeyboard(location_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data[STATE] = GEOLOCATION

        # logger.info('user_data: %s', user_data)
        return GEOLOCATION


def geo_location_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    location = update.message.location

    if not location:

        if user[LANG] == LANGS[0]:
            error_text = "Geolokatsiya yuborilmadi!"
        if user[LANG] == LANGS[1]:
            error_text = "Геолокация не отправлена!"
        if user[LANG] == LANGS[2]:
            error_text = "Геолокация юборилмади!"

        error_text = f'⚠ {error_text}'

        update.message.reply_text(error_text, quote=True)

        state = user_data[STATE]

        # logger.info('user_data: %s', user_data)
        return state

    else:
        longitude = update.message.location.longitude
        latitude = update.message.location.latitude

        user_data[ORDER_LOCATION] = {
            "longitude": longitude,
            "latitude": latitude
        }
        if user[LANG] == LANGS[0]:
            text = "Buyurtma va manzilga sharhlaringizni qoldiring. 👇\n\n" \
                   "Masalan: uy,xonadon raqami, orientir, shuningdek buyurtma uchun istaklar."
        if user[LANG] == LANGS[1]:
            text = "Оставьте комментарии к заказу и адресу. 👇\n\n" \
                   "Например: дом, номер квартиры, ориентиры, а также пожелания к заказу."
        if user[LANG] == LANGS[2]:
            text = "Буюртма ва манзилга шарҳларингизни қолдиринг. 👇\n\n" \
                   "Масалан: уй,хонадон рақами, ориентир, шунингдек буюртма учун истаклар."

        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

        user_data[STATE] = ORDER_COMMENT

        # logger.info('user_data: %s', user_data)
        return ORDER_COMMENT


def order_comments_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text
    payment_method_search = re.search("Naqd pul|Наличные|Нақд пул", text)

    if payment_method_search:
        user_data[ORDER_PAYMENT_METHOD] = text
        delivery_cost = f'{10000:,}'.replace(',', ' ')
        delivery_cost_counter = f'{2000:,}'.replace(',', ' ')

        if user[LANG] == LANGS[0]:
            text = "Yaxshi! Endi buyurtmani tekshirib olaylik"
            nomer_text = "Telefon raqam"
            tg_account_text = "Telegram"
            delivery_method_text = "Yetkazib berish turi"
            order_coomment_text = "Buyurtmaga izoh"
            payment_method_text = "To'lov turi"
            currency = "so'm"
            delivery_cost += f" {currency}"
            delivery_cost_counter += f" {currency}"
            delivery_cost_text = f"Eslatma: yetkazib berish narxi {wrap_tags(f'3 km(kilometr) gacha {delivery_cost}')}!\n\n" \
                                 f"Undan so'ng {wrap_tags(f'har bir km(kilometr) uchun {delivery_cost_counter} dan')} hisoblanadi!"
        if user[LANG] == LANGS[1]:
            text = "Отлично! Теперь давайте проверим заказ"
            nomer_text = "Телефон номер"
            tg_account_text = "Telegram"
            delivery_method_text = "Тип доставки"
            order_coomment_text = "Комментарий к заказу"
            payment_method_text = "Тип платежа"
            currency = "сум"
            delivery_cost += f" {currency}"
            delivery_cost_counter += f" {currency}"
            delivery_cost_text = f"Примечание: стоимость доставки {wrap_tags(f'от {delivery_cost} до 3 км (километр)')}!\n\n" \
                                 f"Потом {wrap_tags(f'по {delivery_cost_counter} за каждый км (километр)')}!"
        if user[LANG] == LANGS[2]:
            text = "Яхши! Энди буюртмани текшириб олайлик"
            nomer_text = "Телефон рақам"
            tg_account_text = "Telegram"
            delivery_method_text = "Етказиб бериш тури"
            order_coomment_text = "Буюртмага изоҳ"
            payment_method_text = "Тўлов тури"
            currency = "сўм"
            delivery_cost += f" {currency}"
            delivery_cost_counter += f" {currency}"
            delivery_cost_text = f"Эслатма: етказиб бериш нархи {wrap_tags(f'3 км(километр) гача {delivery_cost}')}!\n\n" \
                                 f"Ундан сўнг {wrap_tags(f'ҳар бир км(километр) учун {delivery_cost_counter}')} дан ҳисобланади!"

        delivery_cost_text = f'‼ {delivery_cost_text}'
        unit = inline_keyboard_types[order_keyboard][user[LANG]][3]
        text += f' 😊:\n\n'
        tg_account = f'{tg_account_text}: @{user[USERNAME]}\n' if user[USERNAME] else ''
        layout_text = f"{nomer_text}: {wrap_tags(user_data[ORDER_PHONE_NUMBER])}\n" \
                      f"{tg_account}" \
                      f"{delivery_method_text}: {user_data[ORDER_DELIVERY_METHOD]}\n" \
                      f"{payment_method_text}: {user_data[ORDER_PAYMENT_METHOD]}\n" \
                      f"{order_coomment_text}: {user_data[ORDER_COMMENT]}\n\n"
        user_basket = get_user_basket(user[ID])
        user_basket_data = json.loads(user_basket[DATA])

        basket_text = ''
        total_sum = 0
        num = 1
        for food_type, food_data_dict in user_basket_data.items():
            for food_data, food_quantity in food_data_dict.items():
                food_data_from_db = get_food_by_data(food_data, food_type)
                counted_price = food_data_from_db[PRICE] * food_quantity
                total_sum += counted_price

                counted_price = f'{counted_price:,}'.replace(',', ' ')
                food_price = f'{food_data_from_db[PRICE]:,}'.replace(',', ' ')

                basket_text += f'{num}. {food_data_from_db[f"name_{user[LANG]}"]}\n'
                basket_text += f'\t\t{food_quantity} {unit} x {food_price} {currency} = {counted_price} {currency}\n' \
                               f'______________________________\n'
                num += 1

        total_sum_text = f'{inline_keyboard_types[basket_keyboard][user[LANG]][1]}: ' \
                         f'{total_sum:,}'.replace(',', ' ') + f' {currency}'
        total_sum_text = f'\n{wrap_tags(total_sum_text)}\n\n'

        reply_text = text + layout_text + basket_text + total_sum_text + delivery_cost_text
        inline_keyboard = InlineKeyboard(confirm_keyboard, user[LANG], data=user_data[ORDER_LOCATION]).get_keyboard()

        reply_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(f'🏠 {reply_keyboard_types[menu_keyboard][user[LANG]][6]}')]
        ], resize_keyboard=True)

        update.message.reply_text(update.message.text, reply_markup=reply_keyboard)

        message = update.message.reply_html(reply_text, reply_markup=inline_keyboard)
        state = CONFIRMATION
        user_data[STATE] = state
        user_data[MESSAGE_ID] = message.message_id
        user_data[ORDER_TOTAL_SUM] = total_sum

        return state

    else:
        user_data[ORDER_COMMENT] = text

        if user[LANG] == LANGS[0]:
            text = "Siz uchun qulay bo'lgan to'lov usulini tanlang 👇"
            button_text = "Naqd pul"
        if user[LANG] == LANGS[1]:
            text = "Выберите удобный для Вас метод оплаты 👇"
            button_text = "Наличные"
        if user[LANG] == LANGS[2]:
            text = "Сиз учун қулай бўлган тўлов усулини танланг 👇"
            button_text = "Нақд пул"

        button_text = f'💰   {button_text}'
        reply_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(button_text)]
        ], resize_keyboard=True)

        update.message.reply_text(text, reply_markup=reply_keyboard)
        user_data[STATE] = ORDER_PAYMENT_METHOD

        # logger.info('user_data: %s', user_data)
        return ORDER_PAYMENT_METHOD


def confirma_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query:
        data = callback_query.data

        if data == 'cancel':
            callback_query.delete_message()

            if user[LANG] == LANGS[0]:
                reply_text = "Buyurtma bekor qilindi!"
            if user[LANG] == LANGS[1]:
                reply_text = "Заказ отменен!"
            if user[LANG] == LANGS[2]:
                reply_text = "Буюртма бекор қилинди!"

            reply_text = f'😬  {reply_text}'

            main_menu_keyboard = admin_menu_keyboard if user[IS_ADMIN] else client_menu_keyboard
            reply_keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()
            callback_query.message.reply_text(reply_text, reply_markup=reply_keyboard)

            user_data.clear()

            return ConversationHandler.END

        elif data == 'confirm':

            if user[IS_ADMIN]:
                if user[LANG] == LANGS[0]:
                    error_text = "Kechirasiz, siz adminstratorsiz!\n" \
                                 "🛑 Adminstrator buyurtma bera olmaydi"
                if user[LANG] == LANGS[1]:
                    error_text = "Извините, вы администратор! \n" \
                                 "🛑 Администратор не может заказать"
                if user[LANG] == LANGS[2]:
                    error_text = "Кечирасиз, сиз админстраторсиз!\n" \
                                 "🛑 Админстратор буюртма бера олмайди"

                error_text = f'❗ {error_text}!'
                callback_query.answer(error_text, show_alert=True)

                return user_data[STATE]

            current_time = datetime.datetime.now()
            if 11 <= current_time.hour < 15:
                user_basket = get_user_basket(user[ID])

                order_data_dict = dict()
                order_data_dict[STATUS] = 'waiting'
                order_data_dict[USER_ID] = user[ID]
                order_data_dict[PHONE_NUMBER] = user_data[ORDER_PHONE_NUMBER]
                order_data_dict['delivery_method'] = 'delivery'
                order_data_dict['payment_method'] = 'cash'
                order_data_dict[GEOLOCATION] = json.dumps(user_data[ORDER_LOCATION])
                order_data_dict['comment'] = user_data[ORDER_COMMENT]
                order_data_dict['total_sum'] = user_data[ORDER_TOTAL_SUM]
                order_data_dict[MESSAGE_ID] = user_data[MESSAGE_ID]
                order_data_dict['json_data'] = user_basket[DATA]

                new_order_id = insert_data(order_data_dict, 'orders')

                # Dict object
                user_basket_data = json.loads(user_basket[DATA])
                ordet_items_list = []
                for food_type, food_data_dict in user_basket_data.items():
                    for food_data, food_quantity in food_data_dict.items():
                        food_data_from_db = get_food_by_data(food_data, food_type)
                        total_price = food_data_from_db[PRICE] * food_quantity
                        ordet_items_list.append((new_order_id, food_data_from_db[ID], food_type, food_quantity,
                                                 food_data_from_db[PRICE], total_price))

                fields_list = ["order_id", "product_id", "product_type", "quantity", "price", "total_price"]
                result = insert_order_items(ordet_items_list, fields_list, 'order_items')

                if result > 0:
                    icon = '🟡'
                    if user[LANG] == LANGS[0]:
                        reply_text = f"Siznig buyurtmangiz 🆔 {new_order_id} adminga yetkazildi!\n\n" \
                                     f"Tez orada siz bilan bog'lanamiz!"
                        s = "Kutish"
                        label = "Yangi buyurtma"
                    if user[LANG] == LANGS[1]:
                        reply_text = f"Ваш заказ 🆔 {new_order_id} доставлен администратору!\n\n" \
                                     f"Мы скоро свяжемся с вами!"
                        s = "Ожидание"
                        label = "Новый заказ"
                    if user[LANG] == LANGS[2]:
                        reply_text = f"Сизниг буюртмангиз 🆔 {new_order_id} админга етказилди!\n\n" \
                                     f"Тез орада сиз билан боғланамиз!"
                        s = "Кутиш"
                        label = "Янги буюртма"

                    message_to_admin = callback_query.message.text.split('\n')
                    message_to_admin[0] = f'🆔 {new_order_id} [{label}]'
                    message_to_admin = '\n'.join(message_to_admin)
                    message_to_admin += f'\n\n<b>Status: {s} {icon}</b>'
                    admin_lang = get_user(ADMINS['sherzodbek']['chat_id'])[LANG]

                    current_inline_keyboard = callback_query.message.reply_markup
                    current_inline_keyboard.inline_keyboard[0][
                        0].text = f'✅ {inline_keyboard_types[orders_keyboard][admin_lang][1]}'
                    current_inline_keyboard.inline_keyboard[1][
                        0].text = f'❌ {inline_keyboard_types[orders_keyboard][admin_lang][2]}'
                    current_inline_keyboard.inline_keyboard[0][0].callback_data = f'confirm_{new_order_id}'
                    current_inline_keyboard.inline_keyboard[1][0].callback_data = f'cancel_{new_order_id}'

                    # Send message to admins
                    admin_inline_keyboard = current_inline_keyboard
                    for admin in ADMINS.values():
                        context.bot.send_message(admin['chat_id'], message_to_admin,
                                                 reply_markup=admin_inline_keyboard, parse_mode=ParseMode.HTML)

                    current_inline_keyboard.inline_keyboard.pop(0)
                    current_inline_keyboard.inline_keyboard.pop(0)

                    callback_query.edit_message_text(message_to_admin, parse_mode=ParseMode.HTML,
                                                     reply_markup=current_inline_keyboard)

                    reply_text += '\n😉'
                    reply_keyboard = ReplyKeyboard(client_menu_keyboard, user[LANG]).get_keyboard()
                    callback_query.message.reply_text(reply_text, reply_markup=reply_keyboard)

                    user_data.clear()
                    update_user_basket_data(None, user[ID])

                    return ConversationHandler.END

            else:
                if user[LANG] == LANGS[0]:
                    hour_text = "soat"
                    minute_text = "daqiqa"
                    second_text = "soniya"
                    error_text = "Kechirasiz, ish vaqtimiz tugadi!\n" \
                                 "Ertaga urinib ko'ring"
                    error_text_2 = "Kechirasiz, ish vaqtimiz hali boshlanmadi!\n" \
                                   "Keyinroq urinib ko'ring"
                    left_time_text = "Qolgan vaqt"

                if user[LANG] == LANGS[1]:
                    hour_text = "часов"
                    minute_text = "минут"
                    second_text = "секунд"
                    error_text = "Извините, у нас закончилось рабочее время!\n" \
                                 "Попробуйте завтра"
                    error_text_2 = "К сожалению, наше время работы еще не началось!\n" \
                                   "Попробуйте еще раз позже"
                    left_time_text = "Оставшееся время"

                if user[LANG] == LANGS[2]:
                    hour_text = "соат"
                    minute_text = "дақиқа"
                    second_text = "сония"
                    error_text = "Кечирасиз, иш вақтимиз тугади!\n" \
                                 "Эртага уриниб кўринг"
                    error_text_2 = "Кечирасиз, иш вақтимиз ҳали бошланмади!\n" \
                                   "Кейинроқ уриниб кўринг"
                    left_time_text = "Қолган вақт"

                if current_time.hour >= 15:
                    start_time = datetime.datetime(current_time.year, current_time.month, current_time.day,
                                                   11) + datetime.timedelta(days=1)
                elif current_time.hour < 11:
                    start_time = datetime.datetime(current_time.year, current_time.month, current_time.day, 11)
                    error_text = error_text_2

                left_time = start_time - current_time
                hour = left_time.seconds // 60 ** 2
                minute = (left_time.seconds // 60) % 60
                second = (left_time.seconds % 60 ** 2) % 60

                error_text = f'❗ {error_text}! 😊\n\n' + \
                             f'⏳ {left_time_text}: {hour} {hour_text}, {minute} {minute_text}, {second} {second_text}'

                callback_query.answer(error_text, show_alert=True)

                return user_data[STATE]


def fallback_callback_in_order(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text
    main_menu_obj = re.search("(Bosh menyu|Главное меню|Бош меню)$", text)

    if text == '/start' or main_menu_obj:

        if text == '/start':
            if user[LANG] == LANGS[0]:
                text = "Siz ro'yxatdan o'tgansiz"

            if user[LANG] == LANGS[1]:
                text = "Вы зарегистрированы"

            if user[LANG] == LANGS[2]:
                text = "Сиз рўйхатдан ўтгансиз"

            text = f'⚠  {text}, {user[FULLNAME]}!'

        main_menu_keyboard = admin_menu_keyboard if user[IS_ADMIN] else client_menu_keyboard

        keyboard = ReplyKeyboard(main_menu_keyboard, user[LANG]).get_keyboard()

        if MESSAGE_ID in user_data:
            context.bot.delete_message(update.effective_user.id, user_data[MESSAGE_ID])

        update.message.reply_text(text, reply_markup=keyboard)
        user_data.clear()

        # logger.info('user_data: %s', user_data)
        return ConversationHandler.END


order_conversation_handler = ConversationHandler(

    entry_points=[
        MessageHandler(Filters.text & (~Filters.command & ~Filters.update.edited_message), order_conversation_callback),
        CallbackQueryHandler(basket_callback_qery_handler)
    ],

    states={
        CHECK_PHONE_NUMBER: [
            MessageHandler(Filters.regex(main_menu_pattern) & (~ Filters.command) & (~Filters.update.edited_message),
                           check_phone_number)],

        ORDER_DELIVERY_METHOD: [
            MessageHandler(Filters.regex(main_menu_pattern) & (~ Filters.command) & (~Filters.update.edited_message),
                           delivery_callback)],

        GEOLOCATION: [
            MessageHandler(Filters.location |
                           Filters.regex(main_menu_pattern) & (~Filters.command) & (~Filters.update.edited_message),
                           geo_location_callback)],

        ORDER_COMMENT: [
            MessageHandler(Filters.regex(main_menu_pattern) & (~ Filters.command) & (~Filters.update.edited_message),
                           order_comments_callback)],

        ORDER_PAYMENT_METHOD: [MessageHandler(Filters.text & (~ Filters.command) & (~Filters.update.edited_message),
                                              order_comments_callback)],

        CONFIRMATION: [CallbackQueryHandler(confirma_callback, pattern='^confirm|cancel$')]
    },

    map_to_parent={
        MENUS: MENUS,
        ORDER: ORDER,
        ConversationHandler.END: ConversationHandler.END
    },
    fallbacks=[
        MessageHandler(Filters.text & (~Filters.update.edited_message), fallback_callback_in_order)
    ],

    persistent=True,

    name='order_conversation'

)
