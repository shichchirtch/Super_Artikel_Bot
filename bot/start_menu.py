from aiogram.types import BotCommand

async def set_main_menu_2(bot):

    main_menu_commands_2 = [
        BotCommand(command='/liefern',
                   description='Zeigen meine Worte, die ich fruher gefragt habe'),

        BotCommand(command='/help',
                   description='Bot commands'),

        BotCommand(command='/grund_menu',
                   description='Was kann Bot machen'),

        BotCommand(command='/exit',
                   description='Zurueck nach oben')
    ]

    await bot.set_my_commands(main_menu_commands_2)

