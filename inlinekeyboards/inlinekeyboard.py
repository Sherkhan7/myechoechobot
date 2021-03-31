from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .inlinekeyboardtypes import *


class InlineKeyboard(object):
    def __init__(self, keyb_type, lang=None, data=None, history=None):

        self.__type = keyb_type
        self.__lang = lang
        self.__data = data
        self.__history = history
        self.__keyboard = self.__create_inline_keyboard(self.__type, self.__lang, self.__data, self.__history)

    def __create_inline_keyboard(self, keyb_type, lang, data, history):

        if keyb_type == langs_keyboard:
            return self.__get_langs_keyboard(inline_keyboard_types[keyb_type])

        elif keyb_type == lagans_keyboard:
            return self.__get_lagans_keyboard(lang, data)

        elif keyb_type == order_keyboard:
            return self.__get_order_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == basket_keyboard:
            return self.__get_basket_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == confirm_keyboard:
            return self.__get_confirm_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == orders_keyboard:
            return self.__get_orders_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == yes_no_keyboard:
            return self.__get_yes_no_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == delivery_keyboard:
            return self.__get_delivery_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == paginate_keyboard:
            return self.__get_paginate_keyboard(data, history)

        elif keyb_type == geo_keyboard:
            return self.__get_geo_keyboard(inline_keyboard_types[keyb_type][lang])

    @staticmethod
    def __get_langs_keyboard(button_dict):

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f'🇺🇿  {button_dict["uz"]}', callback_data='uz')],
            [InlineKeyboardButton(f'🇷🇺  {button_dict["ru"]}', callback_data='ru')],
            [InlineKeyboardButton(f'🇺🇿  {button_dict["cy"]}', callback_data='cy')],
        ])

    @staticmethod
    def __get_lagans_keyboard(lang, data):
        if lang == 'uz':
            field = 'name_uz'
        if lang == 'ru':
            field = 'name_ru'
        if lang == 'cy':
            field = 'name_cy'

        length = len(data)

        if length % 2 == 0:

            keyboard = [
                [
                    InlineKeyboardButton(data[i][field], callback_data=data[i]['data']),

                    InlineKeyboardButton(data[i + 1][field], callback_data=data[i + 1]['data'])
                ]

                for i in range(0, length, 2)
            ]

        else:
            keyboard = [
                [
                    InlineKeyboardButton(data[i][field], callback_data=data[i]['data']),
                ] if i == length - 1 else

                [
                    InlineKeyboardButton(data[i][field], callback_data=data[i]['data']),
                    InlineKeyboardButton(data[i + 1][field], callback_data=data[i + 1]['data'])
                ] for i in range(0, length, 2)
            ]

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def __get_order_keyboard(buttons, data):

        button1_text = f'🛒  {buttons[1]}'
        button1_data = f'add_{data}'

        minus_sign = '-'
        pilus_sign = '+'

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(minus_sign, callback_data='-'),
                    InlineKeyboardButton(f'1 {buttons[3]}', callback_data='1'),
                    InlineKeyboardButton(pilus_sign, callback_data='+'),
                ],

                [InlineKeyboardButton(button1_text, callback_data=button1_data)],

            ]
        )

    @staticmethod
    def __get_basket_keyboard(buttons, data):
        food_data = data['food_data']
        total_sum = data['total_sum']
        unit = data['unit']
        wanted = data['wanted']
        length = data['length']

        button1_text = "-"
        button1_data = f"minus|{food_data['food_data']}|{food_data['food_type']}"

        button2_text = f'{food_data["quantity"]} {unit}'
        button2_data = food_data['quantity']

        button3_text = f"+"
        button3_data = f"plus|{food_data['food_data']}|{food_data['food_type']}"

        button4_text = "❌"
        button4_data = f"delete|{food_data['food_data']}|{food_data['food_type']}"

        total_button = f'{buttons[1]}: {total_sum}'

        right_text = '⏩'
        left_text = '⏪'

        if wanted == 1 and length > 1:
            right = wanted + 1
            left = length
        elif wanted == length and length != 1:
            right = 1
            left = length - 1
        elif wanted == length and length == 1:
            right = 'dot1'
            left = 'dot2'
        else:
            right = wanted + 1
            left = wanted - 1

        button5_text = right_text
        button5_data = f'w_{right}'

        button6_text = f'{wanted}/{length}'
        button6_data = 'None'

        button7_text = left_text
        button7_data = f'w_{left}'

        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(button1_text, callback_data=button1_data),
                InlineKeyboardButton(button2_text, callback_data=button2_data),
                InlineKeyboardButton(button3_text, callback_data=button3_data),
                InlineKeyboardButton(button4_text, callback_data=button4_data)
            ],
            [
                InlineKeyboardButton(button7_text, callback_data=button7_data),
                InlineKeyboardButton(button6_text, callback_data=button6_data),
                InlineKeyboardButton(button5_text, callback_data=button5_data),
            ],
            [InlineKeyboardButton(total_button, callback_data='total')]
        ])

    @staticmethod
    def __get_confirm_keyboard(buttons, data):

        button3_text = f'🗺  {buttons[3]}'

        button1_text = f'✅ {buttons[1]}'
        button1_data = 'confirm'

        button2_text = f'❌ {buttons[2]}'
        button2_data = 'cancel'

        inline_keyboard = [
            [InlineKeyboardButton(button1_text, callback_data=button1_data)],
            [InlineKeyboardButton(button2_text, callback_data=button2_data)]
        ]

        if data:
            from_latitude = data['latitude']
            from_longitude = data['longitude']
            inline_keyboard.append(
                [InlineKeyboardButton(button3_text,
                                      url=f'http://www.google.com/maps/place/{from_latitude},{from_longitude}/'
                                          f'@{from_latitude},{from_longitude},12z')])
        # 'https://www.google.com/maps/search/?api=1&query=latitude,longitude'
        return InlineKeyboardMarkup(inline_keyboard)

    @staticmethod
    def __get_orders_keyboard(buttons, data):

        inline_keyboard = []
        button1_text = f"🗺 {buttons[3]}"

        button2_text = f'✅ {buttons[1]}'
        button3_text = f'❌ {buttons[2]}'

        inline_keyboard.extend([
            [InlineKeyboardButton(button2_text, callback_data=f'confirm_{data[-1]}')],
            [InlineKeyboardButton(button3_text, callback_data=f'cancel_{data[-1]}')]
        ])

        if data[0]:
            from_latitude = data[0]['latitude']
            from_longitude = data[0]['longitude']
            inline_keyboard.append(
                [InlineKeyboardButton(button1_text,
                                      url=f'http://www.google.com/maps/place/{from_latitude},{from_longitude}/'
                                          f'@{from_latitude},{from_longitude},12z')])
            # location_button_url = f'https://www.google.com/maps/search/?
            # api=1&query={user_data[ORDER_LOCATION]["latitude"]},{user_data[ORDER_LOCATION]["longitude"]}'
        return InlineKeyboardMarkup(inline_keyboard)

    @staticmethod
    def __get_geo_keyboard(buttons):
        button1_text = f"🗺 {buttons[0]}"
        # from_latitude = data['latitude']
        # from_longitude = data['longitude']
        url = 'https://www.google.com/maps/place/Zigir+Osh/@41.278158,69.2041381,14z/' \
              'data=!4m5!3m4!1s0x0:0x1f9d5920ab128749!8m2!3d41.2736197!4d69.2450345'

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(button1_text, url=url)]
        ])

    @staticmethod
    def __get_yes_no_keyboard(buttons, data):

        return InlineKeyboardMarkup([

            [
                InlineKeyboardButton('✅ ' + buttons[1], callback_data=f'{data[0]}_y_{data[-1]}'),
                InlineKeyboardButton('❌ ' + buttons[2], callback_data=f'{data[0]}_n_{data[-1]}')
            ],
        ])

    @staticmethod
    def __get_delivery_keyboard(buttons, order_id):

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(buttons[0], callback_data=f'd_{order_id}')],
        ])

    @staticmethod
    def __get_paginate_keyboard(data, history=None):

        wanted, orders = data
        length = len(orders)

        state = 'h_' if history else ''

        if wanted == 1 and length == 1:
            button1_text = '.'
            button1_data = 'dot_1'

            button3_text = '.'
            button3_data = 'dot_2'

        elif wanted == 1 and length > 1:
            button1_text = '.'
            button1_data = 'dot'

            button3_text = '⏩'
            button3_data = f'{state}w_{wanted + 1}'

        elif wanted == length:
            button1_text = '⏪'
            button1_data = f'{state}w_{wanted - 1}'

            button3_text = '.'
            button3_data = 'dot'

        else:
            button1_text = '\U000023EA'
            button1_data = f'{state}w_{wanted - 1}'

            button3_text = '\U000023E9'
            button3_data = f'{state}w_{wanted + 1}'

        button2_text = f'{wanted}/{length}'
        button2_data = 'None'

        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(button1_text, callback_data=button1_data),
                InlineKeyboardButton(button2_text, callback_data=button2_data),
                InlineKeyboardButton(button3_text, callback_data=button3_data),
            ],
        ])

    def get_keyboard(self):
        return self.__keyboard
