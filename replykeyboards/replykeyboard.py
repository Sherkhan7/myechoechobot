from telegram import ReplyKeyboardMarkup, KeyboardButton
from .replykeyboardtypes import *


class ReplyKeyboard(object):

    def __init__(self, keyb_type, lang, data=None):

        self.__type = keyb_type
        self.__lang = lang
        self.__data = data

        self.__keyboard = self.__create_reply_keyboard(self.__type, self.__lang, self.__data)

    def __create_reply_keyboard(self, keyb_type, lang, data):

        if keyb_type == client_menu_keyboard or keyb_type == admin_menu_keyboard:
            return self.__get_main_menu_keyboard(reply_keyboard_types[keyb_type][lang], keyb_type)

        elif keyb_type == menu_keyboard:
            return self.__get_menu_keyboard(reply_keyboard_types[keyb_type][lang])

        elif keyb_type == foods_keyboard:
            return self.__get_foods_keyboard(lang, data)

        elif keyb_type == settings_keyboard:
            return self.__get_settings_keyboard(reply_keyboard_types[keyb_type][lang])

        elif keyb_type == phone_number_keyboard:
            return self.__get_phone_number_keyboard(reply_keyboard_types[keyb_type][lang])

        elif keyb_type == location_keyboard:
            return self.__get_location_keyboard(reply_keyboard_types[keyb_type][lang])

    @staticmethod
    def __get_main_menu_keyboard(button, keyb_type):

        emoji_1 = '🍽'
        emoji_2 = '🛒'
        emoji_3 = '☎'
        emoji_4 = '⚙'

        if keyb_type == admin_menu_keyboard:
            emoji_1 = '📒'
            emoji_2 = '📑'
            emoji_3 = '🗄'
            emoji_4 = '⚙'
            emoji_5 = '🍽'
            emoji_6 = '📝'

        reply_keyboard = ReplyKeyboardMarkup([

            [KeyboardButton(f'{emoji_1} {button[1]}')],
            [KeyboardButton(f'{emoji_2} {button[2]}')],
            [
                KeyboardButton(f'{emoji_3} {button[3]}'),
                KeyboardButton(f'{emoji_4} {button[4]}')
            ],

        ], resize_keyboard=True)

        if keyb_type == admin_menu_keyboard:
            reply_keyboard = ReplyKeyboardMarkup([

                [KeyboardButton(f'{emoji_1} {button[1]}')],
                [KeyboardButton(f'{emoji_6} {button[6]}')],
                [
                    KeyboardButton(f'{emoji_5} {button[5]}'),
                    KeyboardButton(f'{emoji_4} {button[4]}')
                ],

            ], resize_keyboard=True)

        return reply_keyboard

    @staticmethod
    def __get_menu_keyboard(buttons):

        button1_text = f'🍛  {buttons[1]}'
        button2_text = f'🥗  {buttons[2]}'
        button3_text = f'🥂  {buttons[3]}'
        button4_text = f'🥯  {buttons[4]}'
        button5_text = f'🥚  {buttons[5]}'
        button6_text = f'🏠  {buttons[6]}'
        button7_text = f'🛒  {buttons[7]}'

        reply_keyboard = [
            [KeyboardButton(button1_text), KeyboardButton(button2_text)],
            [KeyboardButton(button3_text), KeyboardButton(button4_text)],
            [KeyboardButton(button5_text), KeyboardButton(button7_text)],
            [KeyboardButton(button6_text)],
        ]

        return ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    @staticmethod
    def __get_foods_keyboard(lang, data):

        if lang == 'uz':
            field = 'name_uz'
        if lang == 'ru':
            field = 'name_ru'
        if lang == 'cy':
            field = 'name_cy'

        menu_btn_text = '🍽 ' + reply_keyboard_types[client_menu_keyboard][lang][1]
        basket_btn_text = '🛒 ' + reply_keyboard_types[client_menu_keyboard][lang][2]
        main_menu_text = '🏠 ' + reply_keyboard_types[menu_keyboard][lang][6]

        length = len(data)

        if length % 2 == 0:

            keyboard = [
                [
                    KeyboardButton(f'{data[i]["icon"]} {data[i][field]}'),
                    KeyboardButton(f'{data[i + 1]["icon"]} {data[i + 1][field]}')
                ]

                for i in range(0, length, 2)
            ]

            keyboard.append([KeyboardButton(basket_btn_text), KeyboardButton(main_menu_text)])

        else:
            keyboard = [
                [
                    KeyboardButton(f'{data[i]["icon"]} {data[i][field]}'),
                    KeyboardButton(basket_btn_text)
                ] if i == length - 1 else

                [
                    KeyboardButton(f'{data[i]["icon"]} {data[i][field]}'),
                    KeyboardButton(f'{data[i + 1]["icon"]} {data[i + 1][field]}')
                ] for i in range(0, length, 2)
            ]

            keyboard.append([KeyboardButton(main_menu_text)])

        keyboard.insert(0, [KeyboardButton(menu_btn_text)])

        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def __get_settings_keyboard(buttons):

        return ReplyKeyboardMarkup([

            [
                KeyboardButton(f'👤 {buttons[1]}'),
                KeyboardButton(f'🌍 {buttons[2]}')
            ],
            [KeyboardButton(f'◀️ {buttons[3]}')],

        ], resize_keyboard=True)

    @staticmethod
    def __get_phone_number_keyboard(buttons):

        return ReplyKeyboardMarkup([
            [
                KeyboardButton(f'📱  {buttons[1]}', request_contact=True)]
        ], resize_keyboard=True)

    @staticmethod
    def __get_location_keyboard(buttons):

        return ReplyKeyboardMarkup([

            [KeyboardButton(f'📍 {buttons[2]}', request_location=True)],

        ], resize_keyboard=True)

    def get_keyboard(self):
        return self.__keyboard
