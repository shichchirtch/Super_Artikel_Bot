import translators
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from bot_base import *
import asyncio
from requests.exceptions import HTTPError

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
        try:
            res = translators.translate_text(query_text=slovo, from_language='en', to_language=lan, translator='bing')
        except AttributeError:
                print('\n\n произошла ошибка AttributeError')
                res = 'Es ist ein Fehler aufgetreten, versuchen Sie bitte noch mal'
        except HTTPError:
            print('Произошла ошибка HTTPError:\n\n')
            res = slovo
        except Exception as err:
            print(f'Other error occurred: {err}')
            res = slovo
    else:
        res = slovo
    return res

async def message_sender(slovo:str, lan:str, temp_dict:dict)->str:
    if lan != 'en':
        try:
            if lan not in temp_dict:
                res = translators.translate_text(query_text=slovo, from_language='en', to_language=lan, translator='bing')
                temp_dict[lan]=res
            else:
                res = temp_dict[lan]
        except AttributeError:
                print('\n\n произошла ошибка AttributeError')
                res = 'Es ist ein Fehler aufgetreten, versuchen Sie bitte noch mal'
        except HTTPError:
            print('Произошла ошибка HTTPError:\n\n')
            res = slovo
        except Exception as err:
            print(f'Other error occurred: {err}')
            res = slovo
    else:
        res = slovo
    return res


async def regular_message(slovo:str, lan:str)->str:
    print('regular message works\n\n')
    modifyed_slovo = lan + '_' + slovo[:10]  # Формируется ключ для регулярного сообщения бота ru_For grammatica
    if lan != 'en':
        # modifyed_slovo = lan + '_' + slovo[:10]
        if modifyed_slovo not in bot_lexicon:  # Если никто ещё не запрашиывал команду
            try:
                res = translators.translate_text(query_text=slovo, from_language='en', to_language=lan, translator='bing')
                bot_lexicon[modifyed_slovo]=res
            except AttributeError:
                print('\n\n произошла ошибка AttributeError')
                res = 'Es ist ein Fehler aufgetreten, versuchen Sie bitte noch mal'
        else:
            res = bot_lexicon[modifyed_slovo]
    else:
        res = slovo
        bot_lexicon[modifyed_slovo] = res
    return res


async def form_WS_string(current_stunde:dict, lan:str):
    """Функция формирует лист воршатца урока"""
    form_str = ''
    if lan != 'en' or lan != 'de':
        for k, v in current_stunde.items():
            try:
                perevod = await translates(v, lan)
                form_str += f'<b>{k}</b>  {perevod}\n'
            except Exception:
                print(f'Exception for {k}')
            await asyncio.sleep(0.15)

    elif lan == 'de':
        for k, v in current_stunde.keys():
            form_str += f'<b>{k}</b>\n'

    else:
        for k, v in current_stunde.items():
            try:
                form_str += f'<b>{k}</b>  {v}\n'
            except Exception:
                print(f'Exception for {k}')
            await asyncio.sleep(0.15)
    return form_str




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

async def us_message_trasher(user_id:int, msg:Message|None|CallbackQuery):
    if msg:
        with suppress(TelegramBadRequest):
            await msg.delete()
            users_db[user_id]['user_ans'] = ''
    else:
        pass

async def regular_message_for_grund_menu(slovo:str, lan:str)->str:
    print('regular_message_for_grund_menu works\n\n')
    modifyed_slovo = lan + '_' + slovo[:10]  # Формируется ключ для регулярного сообщения бота ru_For grammatica
    if lan != 'en':
        # modifyed_slovo = lan + '_' + slovo[:10]
        if modifyed_slovo not in bot_lexicon:  # Если никто ещё не запрашиывал команду
            try:
                res = translators.translate_text(query_text=slovo, from_language='en', to_language=lan, translator='bing')
                bot_lexicon[modifyed_slovo]=res
            except AttributeError:
                print('\n\n произошла ошибка AttributeError')
                res = 'Es ist ein Fehler aufgetreten, versuchen Sie bitte noch mal'
        else:
            res = bot_lexicon[modifyed_slovo]
    else:
        res = slovo
        bot_lexicon[modifyed_slovo] = res
    return res