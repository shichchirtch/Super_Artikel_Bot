from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter
from bot_base import users_db
import re

emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F700-\U0001F77F"  # alchemical symbols
                           u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                           u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           "]+", flags=re.UNICODE)

class STOP_EMODJI(BaseFilter):
    async def __call__(self, message: Message):
        if emoji_pattern.search(message.text):
            return False
        return True

class PRE_START(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id in users_db:
            return False
        return True

letter_kit = 'abcdefghijklmnopqrstuvwxyzöäüß '

class IS_LETTER(BaseFilter):
    async def __call__(self, message: Message):
        for letter in message.text.strip().lower():
            if letter not in letter_kit:
                return False
        return True

class LAN_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data in ['fr', 'gb', 'ru', 'fa', 'uk', 'pl', 'es', 'tr', 'el', 'ar', 'sr-Cyrl', 'en', 'de']:
            return True
        return False

class STUNDE_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data in ('1','2','3','4','5','6','7','8','9','10','11', '12', '13', '14', '15', '16'):
            return True
        return False

class IT_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data in ('IT_A1', 'IT_A2', 'IT_B1'):
            return True
        return False

class WORD_ACCEPT(BaseFilter):
    async def __call__(self, message: Message):
        slovo = message.text.replace(' ', '')
        if slovo.isalpha():
            return True
        return False

class JA_NEIN_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data in ('ja', 'nein'):
            return True
        return False

class LERNEN_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data in ('one', 'two' , 'three', 'four', 'five', 'six', 'sevan', 'eight', 'nine',
                       'ten', 'elevan', 'twelve', 't13', 't14', 't15','t16', 'Wortschatz'):
            return True
        return False

class WEIS_NEIN_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data in ('nicht', 'weis'):
            return True
        return False

class PRIVAT_WORTSCHATZ_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data == 'wh':
            return True
        return False


class SHOW_NOTE_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data == 'zeigen_notiz':
            return True
        return False

class ADD_NEW_NOTE_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data == 'add_notiz':
            return True
        return False

class SPAM_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data in ('no_spam', 'spam'):
            return True
        return False

class EXCLUDE_COMMAND(BaseFilter):
    async def __call__(self, message: Message):
        if message.text:
            if message.text in ('/grammatik', '/wortschatz', '/add_wort',
                                '/set_lan', '/lernen', '/zeigen', '/help', '/settings'):
                return False
            elif message.text.startswith('/grammatik') or message.text.endswith('/grammatik'):
                return False

            elif message.text.startswith('/wortschatz') or message.text.endswith('/wortschatz'):
                return False

            elif message.text.startswith('/add_wort') or message.text.endswith('/add_wort'):
                return False

            elif message.text.startswith('/help') or message.text.endswith('/help'):
                return False
            elif message.text.startswith('/set_lan') or message.text.endswith('/set_lan'):
                return False
            elif message.text.startswith('/lernen') or message.text.endswith('/lernen'):
                return False
            elif message.text.startswith('/zeigen') or message.text.endswith('/zeigen'):
                return False
            elif message.text.startswith('/settings') or message.text.endswith('/settings'):
                return False
            else:
                return True
        else:
            return True



class EXCLUDE_COMMAND_MIT_EXIT(BaseFilter):
    async def __call__(self, message: Message):
        if message.text:
            if message.text in ('/grammatik', '/wortschatz', '/add_wort',
                                '/set_lan', '/lernen', '/zeigen', '/help', '/settings', '/exit'):
                return False
            elif message.text.startswith('/grammatik') or message.text.endswith('/grammatik'):
                return False

            elif message.text.startswith('/exit') or message.text.endswith('/exit'):
                return False

            elif message.text.startswith('/wortschatz') or message.text.endswith('/wortschatz'):
                return False

            elif message.text.startswith('/add_wort') or message.text.endswith('/add_wort'):
                return False

            elif message.text.startswith('/help') or message.text.endswith('/help'):
                return False
            elif message.text.startswith('/set_lan') or message.text.endswith('/set_lan'):
                return False
            elif message.text.startswith('/lernen') or message.text.endswith('/lernen'):
                return False
            elif message.text.startswith('/zeigen') or message.text.endswith('/zeigen'):
                return False
            elif message.text.startswith('/settings') or message.text.endswith('/settings'):
                return False
            else:
                return True
        else:
            return True

class IS_ADMIN(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id == 6685637602:
            return True
        return False

class PERSONAL_TRANSLATION_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data in ('press_exit', 'personal_trans'):
            return True
        return False
