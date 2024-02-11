from aiogram import types, Router, flags
from aiogram.filters import StateFilter

echo_router = Router()


@echo_router.message(StateFilter(None))
@flags.rate_limit(key="default")
async def bot_echo(message: types.Message):
    return
