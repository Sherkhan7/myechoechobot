from telegram import Update, ReplyKeyboardRemove
from telegram.ext import MessageHandler, ConversationHandler, CallbackContext, Filters

from helpers import get_user, wrap_tags
from filters import fullname_filter
from layouts import get_fullname_error_text
from DB import update_user_info
from languages import LANGS
from globalvariables import *
from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

NEW_FULLNAME = 'new_fullname'


def change_name_conversation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)

    if user[LANG] == LANGS[0]:
        reply_text = "yangi ism, familyangizni yuboring"

    if user[LANG] == LANGS[1]:
        reply_text = "отправьте свое новое имя, фамилию"

    if user[LANG] == LANGS[2]:
        reply_text = "янги исм, фамилянгизни юборинг"

    reply_text = f'{wrap_tags(user[FULLNAME])}, {reply_text}:'
    update.message.reply_html(reply_text, reply_markup=ReplyKeyboardRemove())

    return NEW_FULLNAME


def change_fullname_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    fullname = update.message.text

    if fullname == '/cancel' or fullname == '/main' or fullname == '/start':

        if user[LANG] == LANGS[0]:
            text = "Ism, familyani o'zgartirish bekor qilindi"

        if user[LANG] == LANGS[1]:
            text = 'Смена имени и фамилии отменена.'

        if user[LANG] == LANGS[2]:
            text = "Исм, фамиляни ўзгартириш бекор қилинди"

        text = f'⚠  {text}!'

    else:
        fullname = fullname_filter(fullname)

        if fullname:
            result = update_user_info(user[TG_ID], fullname=fullname)

            if result == 'updated':

                if user[LANG] == LANGS[0]:
                    text = "Ism, familyangiz o'zgartirildi"

                if user[LANG] == LANGS[1]:
                    text = "Ваше имя, фамилия изменены"

                if user[LANG] == LANGS[2]:
                    text = "Исм, фамилянгиз ўзгартирилди"

                text = f'✅  {text} !'

            elif result == 'not updated':

                if user[LANG] == LANGS[0]:
                    text = "Ism,familyangiz o'zgartirilmadi"

                if user[LANG] == LANGS[1]:
                    text = 'Ваше имя, фамилия не менялись'

                if user[LANG] == LANGS[2]:
                    text = "Исм, фамилянгиз ўзгартирилмади"

                text = f'❌  {text}!'

        else:

            fullname_error_text = get_fullname_error_text(user[LANG])
            update.message.reply_html(fullname_error_text, quote=True)

            return NEW_FULLNAME

    reply_keyboard = ReplyKeyboard(settings_keyboard, user[LANG]).get_keyboard()
    update.message.reply_text(text, reply_markup=reply_keyboard)

    return ConversationHandler.END


change_name_conversation_handler = ConversationHandler(

    entry_points=[
        MessageHandler(
            Filters.regex(r"Исм,фамиляни ўзгартириш|Изменить имя, фамилию|Ism,familyani o'zgartirish"),
            change_name_conversation_callback
        )
    ],

    states={
        NEW_FULLNAME: [MessageHandler(Filters.text, change_fullname_callback)],
    },
    fallbacks=[],

    persistent=True,

    name='changename_conversation'
)
