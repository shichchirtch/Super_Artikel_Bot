from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter
from postgres_functions import check_user_in_table
from bot_base import users_db


class PRE_START(BaseFilter):
    async def __call__(self, message: Message):
        # data = await check_user_in_table(message.from_user.id)
        # if data:
        if message.from_user.id in users_db:
            return False
        return True

letter_kit = 'abcdefghijklmnopqrstuvwxyzöäüß'

class IS_LETTER(BaseFilter):
    async def __call__(self, message: Message):
        for letter in message.text.strip().lower():
            if letter not in letter_kit:
                return False
        return True

class LAN_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data in ['fr', 'gb', 'ru', 'fa', 'uk', 'pl', 'es', 'tr', 'el', 'ar', 'sr-Cyrl']:
            return True
        return False

class STUNDE_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        if cb.data in '1234567890':
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
                       'ten', 'elevan', 'twelve', 't13', 't14', 't15','t16','Wortschatz'):
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

















class IS_ADMIN(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id == 6685637602:
            return True
        return False
