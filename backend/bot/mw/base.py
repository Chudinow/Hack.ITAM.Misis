import asyncio
import logging

from aiogram import BaseMiddleware

logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            return await handler(event, data)
        except Exception as e:
            logger.exception("Error for user %s", getattr(event.from_user, "id", None), exc_info=e)
            if hasattr(event, "answer"):
                await event.answer("Произошла ошибка. Попробуйте позже.")
            return None


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit=1.0):
        self.rate_limit = rate_limit
        self._locks = {}

    async def __call__(self, handler, event, data):
        user_id = getattr(event.from_user, "id", None)
        if user_id is None:
            return await handler(event, data)
        lock = self._locks.setdefault(user_id, asyncio.Lock())
        if lock.locked():
            if hasattr(event, "answer"):
                await event.answer("Слишком часто! Подождите пару секунд.")
            return None
        async with lock:
            await asyncio.sleep(self.rate_limit)
            return await handler(event, data)
