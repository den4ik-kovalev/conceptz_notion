import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import dotenv_values
from loguru import logger

from src import handlers
from src.lexicon import LEXICON_COMMANDS


logger.add("error.log", format="{time} {level} {message}", level="ERROR")
token = dotenv_values(".env")["TOKEN"]


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in LEXICON_COMMANDS.items()
    ]
    await bot.set_my_commands(main_menu_commands)


@logger.catch
async def main():

    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_router(handlers.router)

    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
