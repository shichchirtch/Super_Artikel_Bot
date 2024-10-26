from aiogram.types import BotCommand

# Функция для настройки кнопки Menu бота
async def set_main_menu(bot):
    # Создаем список с командами и их описанием для кнопки menu
    # bot
    main_menu_commands = [
        BotCommand(command='/liefern',
                   description='Zeigen meine Worte, die ich fruher gefragt habe'),

        BotCommand(command='/help',
                   description='Bot commands'),

        BotCommand(command='/grund_menu',
                   description='Was kann Bot machen'),

        BotCommand(command='/exit',
                   description='Zurueck nach oben')
    ]

    await bot.set_my_commands(main_menu_commands)

