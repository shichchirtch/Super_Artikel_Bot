import translators
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from bot_base import users_db

def create_note_collection_keyboard(*args) -> InlineKeyboardMarkup:
    # Создаем объект клавиатуры
    kb_builder = InlineKeyboardBuilder()
    # Наполняем клавиатуру кнопками-закладками в порядке возрастания

    for button in sorted(args):
        kb_builder.row(InlineKeyboardButton(
            text=button,
            callback_data=button))
    return kb_builder.as_markup()




async def translates(slovo:str, lan:str)->str:
    if lan != 'en':
        res = translators.translate_text(query_text=slovo, from_language='en', to_language=lan, translator='bing')
    else:
        res = slovo
    return res

async def translates_in_english(slovo:str)->str:
    try:
        res = translators.translate_text(query_text=slovo, from_language='de', to_language='en', translator='bing')
    except Exception:
        res = "I do not know this Word((("
    return res


async def message_trasher(user_id:int, msg:Message|None|CallbackQuery):
    if msg:
        with suppress(TelegramBadRequest):
            await msg.delete()
            users_db[user_id]['bot_ans'] = ''
    else:
        pass
