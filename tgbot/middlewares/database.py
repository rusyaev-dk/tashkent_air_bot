from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker

from infrastructure.database.models import User
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.keyboards.inline import set_user_language_kb
from tgbot.misc.constants import SET_USER_LANGUAGE_TEXT


class OuterDatabaseMiddleware(BaseMiddleware):
    def __init__(
            self,
            session_pool: async_sessionmaker
    ) -> None:
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            event_from_user = data.get("event_from_user")
            if not event_from_user:
                return await handler(event, data)

            result = await handler(event, data)
        return result


class InnerDatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        session = data["session"]
        repo = RequestsRepo(session)
        data["repo"] = repo
        result = await handler(event, data)
        return result


class UserExistingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        event_from_user = data.get("event_from_user")
        if not event_from_user:
            return await handler(event, data)
        repo: RequestsRepo = data["repo"]
        user = await repo.users.get_user(telegram_id=event.from_user.id)
        if not user:
            await event.answer(SET_USER_LANGUAGE_TEXT, reply_markup=set_user_language_kb())
            return
        if not user.is_active:
            await repo.users.update_user(User.telegram_id == event_from_user.id, is_active=True)
        data["user"] = user
        return await handler(event, data)
