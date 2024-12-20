from aiogram import Dispatcher
import asyncio
from command_handlers import ch_router
from callback_handlers import cb_router
from start_menu import set_main_menu_2
from bot_instance import bot, bot_storage_key
from postgres_table import init_models

async def main():
    await init_models()

    dp = Dispatcher()
    dp.startup.register(set_main_menu_2)
    await dp.storage.set_data(key=bot_storage_key, data={})
    await set_main_menu_2(bot)
    dp.include_router(ch_router)
    dp.include_router(cb_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
