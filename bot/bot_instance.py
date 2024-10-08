from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis, StorageKey
from config import settings

using_redis = Redis(host=settings.REDIS_HOST)
redis_storage = RedisStorage(redis=using_redis)

class FSM_ST(StatesGroup):
    after_start = State()  # FSM_ST:after_start
    add_wort = State()
    lernen = State()
    admin = State()
    personal_uber = State()
    add_note_1 = State()
    add_note_2 = State()
    schreiben = State()




bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

bot_storage_key = StorageKey(bot_id=bot.id, user_id=bot.id, chat_id=bot.id)

dp = Dispatcher(storage=redis_storage)

bot = Bot(token=settings.BOT_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))

lan_list = ['fr', 'ru', 'fa', 'uk', 'pl', 'es', 'tr', 'el', 'ar', 'sr-Cyrl', 'en']

