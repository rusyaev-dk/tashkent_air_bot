import html

from aiogram import Router, F, flags
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from l10n.translator import Translator
from tgbot.config import Config
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import answer_to_user_kb, FeedbackFactory
from tgbot.keyboards.reply import main_menu_kb
from tgbot.misc.constants import CANCEL_BUTTONS
from tgbot.misc.states import FeedbackSG

feedback_router = Router()


@feedback_router.message(FeedbackSG.get_feedback, F.text.in_(CANCEL_BUTTONS))
@inject
async def cancel_feedback(
        message: Message,
        state: FSMContext,
        l10n: FromDishka[Translator]
):
    await message.answer(l10n.get_text(key="action-cancelled"), reply_markup=main_menu_kb(l10n=l10n))
    await state.clear()


@feedback_router.message(F.text, FeedbackSG.get_feedback)
@flags.rate_limit(key="default")
@inject
async def send_feedback(
        message: Message,
        state: FSMContext,
        config: Config,
        l10n: FromDishka[Translator]
):
    text = f"💬 Сообщение от пользователя {message.from_user.full_name}:\n\n" + message.text
    await message.bot.send_message(
        text=html.escape(text),
        chat_id=config.tg_bot.operator_ids[0],
        reply_markup=answer_to_user_kb(
           user_id=message.from_user.id,
           msg_to_reply_id=message.message_id
        )
    )
    await state.clear()
    await message.answer(l10n.get_text(key="feedback-sent"),
                         reply_markup=main_menu_kb(l10n=l10n))


@feedback_router.message(FeedbackSG.get_feedback)
@flags.rate_limit(key="default")
@inject
async def incorrect_feedback_message(
        message: Message,
        l10n: FromDishka[Translator]
):
    await message.answer(l10n.get_text(key="incorrect-content-type"))


@feedback_router.callback_query(AdminFilter(), FeedbackFactory.filter())
async def answer_to_user(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: FeedbackFactory
):
    user_id = callback_data.user_id
    msg_to_reply_id = callback_data.msg_to_reply_id
    await call.answer()
    await call.message.delete_reply_markup()
    await call.message.answer("✉️ Что ответить пользователю?")
    await state.set_state(FeedbackSG.get_answer_to_user)
    data = {"user_id": user_id, "msg_to_reply_id": msg_to_reply_id}
    await state.update_data(data=data)


@feedback_router.message(AdminFilter(), F.text, FeedbackSG.get_answer_to_user)
@inject
async def get_answer_text(
        message: Message,
        state: FSMContext,
        l10n: FromDishka[Translator]
):
    data = await state.get_data()
    user_id = data.get("user_id")
    msg_to_reply_id = data.get("msg_to_reply_id")
    text = f"{l10n.get_text(key='reply-from-admin')}\n\n" + message.text
    await state.clear()
    try:
        await message.bot.send_message(chat_id=user_id, text=text,
                                       reply_to_message_id=msg_to_reply_id)
    except TelegramForbiddenError:
        await message.answer("❌ Сообщение не доставлено: пользователь заблокировал бота.")
        return
    await message.answer("✅ Сообщение доставлено.")


@feedback_router.message(AdminFilter(), FeedbackSG.get_answer_to_user)
@flags.rate_limit(key="default")
async def incorrect_answer_message(
        message: Message,
):
    await message.answer("❗️ Пожалуйста, отправьте текст.")
