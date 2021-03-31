from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, TelegramError
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters
)

from config import SMM_ADMINS, DEVELOPER_CHAT_ID
from DB import insert_data, get_user, insert_order_items, get_all_users, update_post_status

from languages import LANGS
from globalvariables import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from replykeyboards.replykeyboardtypes import reply_keyboard_types

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

import logging
import re
import json
import datetime
import time

logger = logging.getLogger()

CONFIRMATION_SEND_POST = 'confirmation_send_post'


def sendpost_conversation_callback(update: Update, contextx: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = contextx.user_data

    if user[TG_ID] in SMM_ADMINS:
        if user[LANG] == LANGS[0]:
            text = "Ajoyib, endi menga rasm yoki video yuboring yuboring"
        if user[LANG] == LANGS[1]:
            text = "Отлично, пришлите мне картинку или видео"
        if user[LANG] == LANGS[2]:
            text = "Ажойиб, энди менга расм ёки видео юборинг юборинг"

        text = f'🙂 {text}'

        reply_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(f'🏠 {reply_keyboard_types[menu_keyboard][user[LANG]][6]}')]
        ], resize_keyboard=True)

        update.message.reply_text(text, reply_markup=reply_keyboard)
        user_data[STATE] = PHOTO

        return PHOTO

    else:
        if user[LANG] == LANGS[0]:
            text = "Kechirasiz, siz foydalanuvchilarga xabar yubora olmaysiz"
        if user[LANG] == LANGS[1]:
            text = "Извините, вы не можете отправлять сообщения пользователям"
        if user[LANG] == LANGS[2]:
            text = "Кечирасиз, сиз фойдаланувчиларга хабар юбора олмайсиз"

        text = f'❗ {text} 😬'
        update.message.reply_text(text)

        return ConversationHandler.END


def photoand_video_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'a') as update_file:
    #     update_file.write(json.dumps(update.to_dict(), indent=3, ensure_ascii=False))
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    caption = update.message.caption
    # List of PhotoSize objects
    photo = update.message.photo
    video = update.message.video

    if caption is None:
        if user[LANG] == LANGS[0]:
            error_text = "Kechirasiz, yuborilgan rasmda yoki videoda izoh yo'q.\n\n" \
                         "Rasm yoki videoni izoh bilan yuboring"
        if user[LANG] == LANGS[1]:
            error_text = "К сожалению, нет ни одного комментария на фото или видео, отправленного.\n\n" \
                         "Отправить картинку или видео с комментарием"
        if user[LANG] == LANGS[2]:
            error_text = "Кечирасиз, юборилган расмда ёки видеода изоҳ йўқ.\n\n" \
                         "Расм ёки видеони изоҳ билан юборинг"

        error_text = f'❗ {error_text}!'
        update.message.reply_text(error_text, quote=True)
        return user_data[STATE]

    if user[LANG] == LANGS[0]:
        text = "Xabarni tasdiqlaysizmi"

    if user[LANG] == LANGS[1]:
        text = "Вы подтверждаете сообщение"

    if user[LANG] == LANGS[2]:
        text = "Хабарни тасдиқлайсизми"
    text += ' ?'

    inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG], data=['send', 'post']).get_keyboard()
    inline_keyboard.inline_keyboard.insert(0, [InlineKeyboardButton(text, callback_data='none')])

    if photo:
        user_data[PHOTO] = photo
        message = update.message.reply_photo(photo[-1].file_id, caption=caption, reply_markup=inline_keyboard)
    elif video:
        user_data['video'] = video
        message = update.message.reply_video(video.file_id, caption=caption, reply_markup=inline_keyboard)

    user_data[STATE] = CONFIRMATION_SEND_POST
    user_data[MESSAGE_ID] = message.message_id
    user_data['caption'] = update.message.caption

    # logger.info('user_data: %s', user_data)
    return CONFIRMATION_SEND_POST


def send_messages(context: CallbackContext):
    user = context.job.context[0]
    user_data = context.job.context[-1]
    errors_dict = dict()

    if PHOTO in user_data:
        photo = user_data[PHOTO][-1].file_id

        start_time = datetime.datetime.now()
        for u in range(1, 501):
            try:
                caption = user_data['caption']
                time.sleep(0.05)
                # context.bot.send_photo(u[TG_ID], photo, caption=caption)
                context.bot.send_photo(653634001, photo, caption=caption + f'\n\n{u}')
            except TelegramError as e:
                # errors_dict.update({'user_id': u[ID], 'user_tg_id': u[TG_ID], 'error_message': e.message})
                errors_dict.update({'error_message': e.message})
        end_time = datetime.datetime.now()

    elif 'video' in user_data:
        video = user_data['video'].file_id

        start_time = datetime.datetime.now()
        for u in range(1, 501):
            try:
                caption = user_data['caption']
                time.sleep(0.05)
                # context.bot.send_video(u[TG_ID], video, caption=caption)
                context.bot.send_video(653634001, video, caption=caption + f'\n\n{u}')
            except TelegramError as e:
                # errors_dict.update({'user_id': u[ID], 'user_tg_id': u[TG_ID], 'error_message': e.message})
                errors_dict.update({'error_message': e.message})
        end_time = datetime.datetime.now()

    text = f'✅ Sending this message to all users have been successfully finished !'
    context.bot.send_message(chat_id=user[TG_ID], text=text, reply_to_message_id=user_data[MESSAGE_ID])

    caption = user_data['caption'] + '\n\nStatus: sended 🟢'
    context.bot.edit_message_caption(chat_id=user[TG_ID], message_id=user_data[MESSAGE_ID], caption=caption)

    errors_dict.update({
        'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
        'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
        'delta': (end_time - start_time).total_seconds()
    })
    dev_text = json.dumps(errors_dict, indent=3)
    context.bot.send_message(DEVELOPER_CHAT_ID, dev_text)

    # Update post status
    update_post_status('sended', user_data['post_id'])


def confirmation_send_post_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data

    data_list = callback_query.data.split('_')

    if data != 'none':
        action = data_list[1]

        if action == 'n':
            callback_query.delete_message()

            if user[LANG] == LANGS[0]:
                text = "Xabar tasqdiqlanmadi"
            if user[LANG] == LANGS[1]:
                text = "Сообщение не было подтверждено"
            if user[LANG] == LANGS[2]:
                text = "Хабар тасқдиқланмади"
            icon = "❌"

        else:

            if user[LANG] == LANGS[0]:
                text = "Barcha foydalanuvchilarga xabar yuborish boshlandi\n\n" \
                       "Biroz kuting"
            if user[LANG] == LANGS[1]:
                text = "Отправка сообщений всем пользователям началась\n\n" \
                       "Подождите минуту"
            if user[LANG] == LANGS[2]:
                text = "Барча фойдаланувчиларга хабар юбориш бошланди\n\n" \
                       "Бироз кутинг"
            icon = "✅"

            post_data = dict()
            post_data['caption'] = user_data['caption']
            post_data[STATUS] = 'sending'
            post_data['sent_by'] = user[ID]
            # Write post to database
            post_id = insert_data(post_data, 'posts')
            user_data['post_id'] = post_id

            if PHOTO in user_data:
                post_photo_sizes = []
                for photo in user_data[PHOTO]:
                    photo = photo.to_dict()
                    post_photo_sizes.append(
                        (
                            post_id, photo['file_id'], photo['file_unique_id'],
                            photo['width'], photo['height'], photo['file_size']
                        )
                    )
                fields_list = ["post_id", "file_id", "file_unique_id", "width", "height", "file_size"]

            elif 'video' in user_data:
                fields_list = [
                    "post_id", "file_id", "file_unique_id", "width", "height", "duration", "mime_type", "file_size"
                ]
                post_photo_sizes = [
                    (
                        post_id,
                        user_data['video'].file_id,
                        user_data['video'].file_unique_id,
                        user_data['video'].width,
                        user_data['video'].height,
                        user_data['video'].duration,
                        user_data['video'].mime_type,
                        user_data['video'].file_size,
                    )
                ]

            result = insert_order_items(post_photo_sizes, fields_list, 'post_photo_sizes')

            job_q = context.job_queue
            job_q.run_once(send_messages, 1, name='my_job', context=[user, dict(user_data)])

            if result > 0:
                caption = user_data['caption'] + f'\n\nStatus: {post_data[STATUS]} 🔵'
                callback_query.edit_message_caption(caption)

        text = f'{icon} {text} !'
        callback_query.answer(text, show_alert=True)
        reply_keyboard = ReplyKeyboard(admin_menu_keyboard, user[LANG]).get_keyboard()
        callback_query.message.reply_text(reply_keyboard_types[menu_keyboard][user[LANG]][6],
                                          reply_markup=reply_keyboard)

        user_data.clear()
        return ConversationHandler.END

    callback_query.answer()


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


sendpost_conversation_handler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex(
            r"Foydalanuvchilarga xabar yuborish|Отправить сообщение пользователям|Фойдаланувчиларга хабар юбориш")
                       & (~Filters.update.edited_message), sendpost_conversation_callback)
    ],

    states={
        PHOTO: [
            MessageHandler(Filters.photo | Filters.video & (~Filters.update.edited_message), photoand_video_callback)],

        CONFIRMATION_SEND_POST: [CallbackQueryHandler(confirmation_send_post_callback, pattern=r'\w+_(y|n)_\w+|none')]

    },
    fallbacks=[MessageHandler(Filters.text & (~Filters.update.edited_message), fallback_callback)],

    persistent=True,

    name='sendpost_conversation'
)
