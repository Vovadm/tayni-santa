import asyncio
from aiogram import Bot, Dispatcher
from config import settings

import logging

from db.db import init_db
from handlers.admin import router as admin_router
from handlers.register import router as register_router


async def main():
    await init_db()

    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher()
    dp.include_router(register_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("successful exit")
