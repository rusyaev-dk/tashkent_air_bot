from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, default_throttle_time: int):
        self.caches = {
            "default": TTLCache(maxsize=10_000, ttl=default_throttle_time)
        }

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        rate_limit = get_flag(data, "rate_limit")
        if rate_limit is not None and rate_limit.get("key") in self.caches:
            limit_key = rate_limit.get("key")
            if event.chat.id in self.caches[limit_key]:
                return
            else:
                self.caches[limit_key][event.chat.id] = None
        return await handler(event, data)
