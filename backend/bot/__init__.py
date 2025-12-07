from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from routes import invite_router

from bot.mw import DBSessionMiddleware, ErrorMiddleware
from config import TG_BOT_TOKEN
from db import db

bot = Bot(token=TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))


async def start_bot():
    await db.connect()

    dp = Dispatcher()

    dp.message.middleware(ErrorMiddleware())
    dp.callback_query.middleware(ErrorMiddleware())
    dp.callback_query.middleware(DBSessionMiddleware(db.session))

    dp.include_router(invite_router)

    try:
        await dp.start_polling(bot)
    finally:
        await db.disconnect()
