from telegram import Update, ParseMode, ReplyKeyboardMarkup, KeyboardButton, TelegramError
from telegram.ext import MessageHandler, ConversationHandler, CallbackContext, Filters, CallbackQueryHandler

from config import PHOTOS_URL
from helpers import get_user, wrap_tags
from DB import get_foods, get_food_by_data, get_user_basket, update_user_basket_data
from languages import LANGS
from globalvariables import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from replykeyboards.replykeyboardtypes import reply_keyboard_types

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from inlinekeyboards.inlinekeyboardtypes import inline_keyboard_types

from .orderconversation import order_conversation_handler
import re
import json
import logging

logger = logging.getLogger()

MENUS, ADDITIONALS, PLOVS, SALADS, DRINKS, BREADS, ASK_LAGAN, LAGANS, ORDER, ADD_FOOD, CHOOSE_FOOD = (
    'menus', 'additionals', 'plovs', 'salads', 'drinks', 'breads', 'ask_lagan', 'lagans', 'order', 'add_food',
    'choose_food'
)

# Inverse pattern
pattern = "^(.(?!(some text)))*$"

# Not main menu ot basket
main_menu_pattern = "^(.(?!(Bosh menyu|Главное меню|Бош меню)))*$"


def menu_conversation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    full_text = update.message.text
    text = full_text.split(maxsplit=1)[-1]

    # Menyu
    if text == reply_keyboard_types[client_menu_keyboard][user[LANG]][1]:

        if user[LANG] == LANGS[0]:
            reply_text = "Nima buyurtma qilmoqchisiz"

        if user[LANG] == LANGS[1]:
            reply_text = "Что вы хотите заказать"

        if user[LANG] == LANGS[2]:
            reply_text = "Нима буюртма қилмоқчисиз"

        reply_text = f"{reply_text}? 😊\n" \
                     f"👇👇👇"

        if MESSAGE_ID in user_data:
            context.bot.delete_message(user[TG_ID], user_data[MESSAGE_ID])
            user_data.pop(MESSAGE_ID)

        reply_keyboard = ReplyKeyboard(menu_keyboard, user[LANG]).get_keyboard()
        update.message.reply_photo(PHOTOS_URL + 'menu_all.png', reply_text, reply_markup=reply_keyboard)

        user_data[STATE] = MENUS

        # logger.info('user_data: %s', user_data)
        return MENUS

    # Basket
    elif text == reply_keyboard_types[client_menu_keyboard][user[LANG]][2]:
        user_basket = get_user_basket(update.effective_user.id)

        if user[LANG] == LANGS[0]:
            button1_text = "Tasdiqlash"
            button2_text = "Savatni tozalash"
            price_text = "Narx"
            currency = "so'm"
            text = "Xarid savatingiz bo'sh"
        if user[LANG] == LANGS[1]:
            button1_text = "Подтверждение"
            button2_text = "Очистить корзину"
            price_text = "Цена"
            currency = "сум"
            text = "Ваша корзина пуста"
        if user[LANG] == LANGS[2]:
            button1_text = "Тасдиқлаш"
            button2_text = "Саватни тозалаш"
            price_text = "Нарх"
            currency = "сўм"
            text = "Харид саватингиз бўш"
        unit = inline_keyboard_types[order_keyboard][user[LANG]][3]

        if user_basket[DATA]:
            user_basket_data = json.loads(user_basket[DATA])

            if MESSAGE_ID in user_data:
                context.bot.delete_message(update.effective_user.id, user_data[MESSAGE_ID])
                user_data.pop(MESSAGE_ID)

            keyboard = ReplyKeyboardMarkup([
                [KeyboardButton('✅  ' + button1_text), KeyboardButton('❌  ' + button2_text)],
                [KeyboardButton('🍽  ' + reply_keyboard_types[client_menu_keyboard][user[LANG]][1])]
            ], resize_keyboard=True)
            update.message.reply_text(full_text, reply_markup=keyboard)

            foods_list = []
            total_sum = 0

            for food_type, food_data_dict in user_basket_data.items():
                for food_data, food_quantity in food_data_dict.items():
                    foods_list.append({'food_data': food_data, 'food_type': food_type, 'quantity': food_quantity})
                    total_sum += get_food_by_data(food_data, food_type)[PRICE] * food_quantity

            wanted = 1
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
            message = update.message.reply_photo(photo_url, caption=caption, reply_markup=inline_keyboard,
                                                 parse_mode=ParseMode.HTML)
            state = ORDER
            user_data[STATE] = state
            user_data[MESSAGE_ID] = message.message_id

        else:

            reply_text = f'🙈  {text}!'

            if STATE in user_data:
                state = user_data[STATE]
            else:
                state = ConversationHandler.END

            update.message.reply_text(reply_text)

        # logger.info('user_data: %s', user_data)
        return state


def menus_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    plovs_obj = re.search("Osh|Плов|Ош", text)
    salads_obj = re.search("Salatlar|Салаты|Салатлар", text)
    drinks_obj = re.search("Ichimliklar|Напитки|Ичимликлар", text)
    breads_obj = re.search("Non|Хлеб|Нон", text)
    additionals_obj = re.search("Qo'shimcha|Дополнительный|Қўшимча", text)

    if plovs_obj:
        food_state = PLOVS
    elif salads_obj:
        food_state = SALADS
    elif drinks_obj:
        food_state = DRINKS
    elif breads_obj:
        food_state = BREADS
    elif additionals_obj:
        food_state = ADDITIONALS
    else:
        food_state = None

    if food_state:
        foods_data = get_foods(food_state)

        reply_keyboard = ReplyKeyboard(foods_keyboard, user[LANG], data=foods_data).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data[STATE] = CHOOSE_FOOD
        user_data['food_state'] = food_state

        # logger.info('user_data: %s', user_data)
        return CHOOSE_FOOD


def choose_food_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    full_text = update.message.text
    text = full_text.split(maxsplit=1)[-1]

    if user[LANG] == LANGS[0]:
        price_text = 'Narx'
        currency = "so'm"

    if user[LANG] == LANGS[1]:
        price_text = 'Цена'
        currency = 'сум'

    if user[LANG] == LANGS[2]:
        price_text = 'Нарх'
        currency = 'сўм'

    # Maybe deleted in the future
    if 'food_state' in user_data:
        foods = get_foods(user_data['food_state'])
    else:
        user_data['food_state'] = user_data[STATE]
        foods = get_foods(user_data['food_state'])
    #

    food_data = None
    for food in foods:
        if food[f'name_{user[LANG]}'] == text:
            food_data = food
            break

    if food_data:
        price_in_thousand = f'{food_data[PRICE]:,}'.replace(',', ' ')
        price_text = f'{price_text}: {price_in_thousand} {currency}'
        caption = f'{food_data[f"name_{user[LANG]}"]}\n\n' \
                  f'{food_data[f"description_{user[LANG]}"]}\n\n' \
                  f'{wrap_tags(price_text)}'

        reply_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton('◀️ ' + inline_keyboard_types[order_keyboard][user[LANG]][2])]
        ], resize_keyboard=True)
        update.message.reply_text(text, reply_markup=reply_keyboard)

        photo_url = PHOTOS_URL + user_data['food_state'] + f'/{food_data[PHOTO]}'
        inline_keyboard = InlineKeyboard(order_keyboard, user[LANG], data=food_data[DATA]).get_keyboard()
        message = update.message.reply_photo(photo_url, caption=caption, reply_markup=inline_keyboard,
                                             parse_mode=ParseMode.HTML)

        user_data[MESSAGE_ID] = message.message_id
        user_data[STATE] = ADD_FOOD

        # logger.info('user_data: %s', user_data)
        return ADD_FOOD


def add_food_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    if re.search('add_', data):

        food_data = data.replace('add_', '')

        amount = int(callback_query.message.reply_markup.inline_keyboard[0][1].text.split()[0])

        item = {food_data: amount}
        user_basket = get_user_basket(user[ID])
        # JSON object or None
        user_basket_data = user_basket[DATA]

        if not user_basket_data:
            user_basket_data = dict()
            user_basket_data[user_data['food_state']] = item

        else:
            user_basket_data = json.loads(user_basket_data)

            # Check if user_data['food_state'] in user_basket_data
            if not user_data['food_state'] in user_basket_data:
                user_basket_data[user_data['food_state']] = dict()

            if food_data in user_basket_data[user_data['food_state']]:
                user_basket_data[user_data['food_state']][food_data] += amount
            else:
                user_basket_data[user_data['food_state']].update(item)

        # Check food_state for SALADS and PLOVS to add dishes automatically
        if user_data['food_state'] == SALADS or user_data['food_state'] == PLOVS or \
                user_data['food_state'] == ADDITIONALS:

            dish_type = None

            if user_data['food_state'] == SALADS:
                dish_type = "dish_salad"

            elif user_data['food_state'] == PLOVS or food_data == "pay_0.5" or food_data == "pay_1" or \
                    food_data == "gosht_0.5" or food_data == "gosht_1":
                dish_type = "dish_osh"

            if DISHES not in user_basket_data:
                user_basket_data[DISHES] = dict()

            if dish_type in user_basket_data[DISHES]:
                user_basket_data[DISHES][dish_type] += amount
            elif dish_type is not None:
                user_basket_data[DISHES].update({dish_type: amount})

        if LAGANS in user_basket_data:
            if 'dish_osh' in user_basket_data[DISHES]:
                del user_basket_data[DISHES]['dish_osh']

        # update user basket data
        json_data = json.dumps(user_basket_data)
        update_user_basket_data(json_data, user[TG_ID])

        food = get_food_by_data(food_data, user_data['food_state'])
        # show user laert
        callback_query.answer(f'+{amount}, {food[f"name_{user[LANG]}"]}', show_alert=True)
        callback_query.delete_message()
        user_data.pop(MESSAGE_ID)

        if user[LANG] == LANGS[0]:
            reply_text = "Sizning buyurtmangizni lagan bilan yetkazib berishimizni xohlaysizmi ?"
            yes = "Ha"
            no = "Yo'q"
            text = "Davom etamizmi"

        if user[LANG] == LANGS[1]:
            reply_text = "Хотите чтобы мы доставили ваш заказ с ляганом ?"
            yes = "Да"
            no = "Нет"
            text = "Продолжим"

        if user[LANG] == LANGS[2]:
            reply_text = "Сизнинг буюртмангизни лаган билан етказиб беришимизни хоҳлайсизми ?"
            yes = "Ҳа"
            no = "Йўқ"
            text = "Давом этамизми"

        text = f'{text} ? ☺'

        if user_data['food_state'] == PLOVS:
            reply_keyboard = ReplyKeyboardMarkup([
                [KeyboardButton(f'😊 {yes}'), KeyboardButton(f'😐 {no}')],
            ], resize_keyboard=True)

            callback_query.message.reply_text(reply_text, reply_markup=reply_keyboard)

            user_data[STATE] = ASK_LAGAN
            user_data['food_state'] = LAGANS

            # logger.info('user_data: %s', user_data)
            return ASK_LAGAN
        if user_data['food_state'] == LAGANS:
            user_data['food_state'] = PLOVS
        foods_data = get_foods(user_data['food_state'])

        if user_data['food_state'] == LAGANS:
            user_data['food_state'] = PLOVS
        foods_data = get_foods(user_data['food_state'])

        reply_keyboard = ReplyKeyboard(foods_keyboard, user[LANG], data=foods_data).get_keyboard()
        callback_query.message.reply_text(text, reply_markup=reply_keyboard)

        user_data[STATE] = CHOOSE_FOOD

        # logger.info('user_data: %s', user_data)
        return CHOOSE_FOOD

    elif data == '-' or data == '+' or isinstance(data, str):
        callback_query.answer('Please wait ... ⏳')
        button = callback_query.message.reply_markup.inline_keyboard[0][1]
        button_text = button.text.split()
        unit = button_text[-1]
        counter = button_text[0]
        counter = int(counter) - 1 if data == '-' else int(counter) + 1 if data == '+' else 0

        if counter > 0:
            button.text = f'{counter} {unit}'
            button.callback_data = str(counter)

            # When user clicks the InlineKeyboardButton fast so many times TelegramError will be thrown
            try:
                callback_query.edit_message_reply_markup(callback_query.message.reply_markup)
            except TelegramError:
                pass

        state = user_data[STATE]

    return state


def ask_lagan_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    full_text = update.message.text
    text = full_text.split(maxsplit=1)[-1]

    yes_search = re.search("Ha|Да|Ҳа", text)
    no_search = re.search("Yo'q|Нет|Йўқ", text)

    # Yes
    if yes_search:

        if user[LANG] == LANGS[0]:
            reply_text = "Ajoyib tanlov! 🔥\n"
            reply_text_2 = "Endi laganni tanlang:"
        if user[LANG] == LANGS[1]:
            reply_text = "Отличный выбор!🔥\n"
            reply_text_2 = "Теперь выберите размер лягана:"
        if user[LANG] == LANGS[2]:
            reply_text = "Ажойиб танлов! 🔥\n"
            reply_text_2 = "Энди лаганни танланг:"

        reply_text += reply_text_2
        lagans_data = get_foods(user_data['food_state'])
        # lagans_keyboard
        reply_keyboard = ReplyKeyboard(foods_keyboard, user[LANG], data=lagans_data).get_keyboard()

        update.message.reply_text(reply_text, reply_markup=reply_keyboard)

        user_data[STATE] = CHOOSE_FOOD

        # logger.info('user_data: %s', user_data)
        return CHOOSE_FOOD

    #  No
    elif no_search:
        if user[LANG] == LANGS[0]:
            text = "Davom etamizmi"

        if user[LANG] == LANGS[1]:
            text = "Продолжим"

        if user[LANG] == LANGS[2]:
            text = "Давом этамизми"

        text = f'{text} ? ☺'
        foods_data = get_foods(PLOVS)

        reply_keyboard = ReplyKeyboard(foods_keyboard, user[LANG], data=foods_data).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data[STATE] = CHOOSE_FOOD
        user_data['food_state'] = PLOVS
        # logger.info('user_data: %s', user_data)
        return CHOOSE_FOOD


def fallback_callback(update: Update, context: CallbackContext):
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


def back_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    foods_data = get_foods(user_data['food_state'])

    reply_keyboard = ReplyKeyboard(foods_keyboard, user[LANG], data=foods_data).get_keyboard()
    update.message.reply_text(text, reply_markup=reply_keyboard)

    if MESSAGE_ID in user_data:
        context.bot.delete_message(user[TG_ID], user_data[MESSAGE_ID])
        user_data.pop(MESSAGE_ID)

    user_data[STATE] = CHOOSE_FOOD

    # logger.info('user_data: %s', user_data)
    return CHOOSE_FOOD


# back|back_\w+|\-|\+|add_\w+_(\d[.]\d)|add_\w+

menu_conversation_handler = ConversationHandler(

    entry_points=[
        MessageHandler(Filters.regex(r"(Меню|Menyu|Xarid savati|Корзина|Харид савати)"), menu_conversation_callback)
    ],

    states={
        MENUS: [MessageHandler(Filters.regex(main_menu_pattern) & (~Filters.command) & (~Filters.update.edited_message),
                               menus_callback)],

        CHOOSE_FOOD: [
            MessageHandler(Filters.regex(main_menu_pattern) & (~Filters.command) & (~Filters.update.edited_message),
                           choose_food_callback)],

        ADD_FOOD: [CallbackQueryHandler(add_food_callback),
                   MessageHandler(Filters.regex("Ortga|Назад|Ортга") & (~Filters.update.edited_message),
                                  back_callback)],

        ASK_LAGAN: [MessageHandler(Filters.regex("Ha|Да|Ҳа|Yo'q|Нет|Йўқ") & (~Filters.update.edited_message),
                                   ask_lagan_callback)],

        ORDER: [order_conversation_handler]
    },

    fallbacks=[
        MessageHandler(Filters.text & (~Filters.update.edited_message), fallback_callback),
    ],

    persistent=True,

    name='menu_conversation',

    allow_reentry=True

)
