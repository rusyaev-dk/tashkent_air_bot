import asyncio
import html
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from infrastructure.database.models import User
from infrastructure.database.repositories.users_repo import UsersRepositoryI
from l10n.translator import LocalizedTranslator
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import NotifyUsersApproveFactory, notify_approve_kb, NotifyUsersTargetLanguageFactory
from tgbot.keyboards.reply import main_menu_kb
from tgbot.misc.states import NotifyUsersSG
from tgbot.services.broadcaster import send_animation, send_sticker, send_audio, send_document, send_photo, send_text


users_notify_router = Router()
users_notify_router.message.filter(AdminFilter())


@users_notify_router.callback_query(NotifyUsersSG.get_target_language_code, NotifyUsersTargetLanguageFactory.filter(
    F.target_language_code == "cancel"
))
async def cancel_notifying(
        call: CallbackQuery,
        state: FSMContext,
        l10n: LocalizedTranslator,
):
    await call.message.edit_text("Рассылка отменена.")
    await call.message.answer(l10n.get_text(key='main-menu'), reply_markup=main_menu_kb(l10n=l10n))
    await state.clear()


@users_notify_router.callback_query(NotifyUsersSG.get_target_language_code, NotifyUsersTargetLanguageFactory.filter())
async def get_target_language_code(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: NotifyUsersTargetLanguageFactory
):
    await call.answer()
    target_language_code = callback_data.target_language_code
    await state.update_data(target_language_code=target_language_code)
    await call.message.edit_text("📦 Отправьте текст/фото/файл для оповещения пользователей:")
    await state.set_state(NotifyUsersSG.get_notify_media)


@users_notify_router.message(NotifyUsersSG.get_notify_media)
async def get_notify_media(
        message: Message,
        state: FSMContext
):
    await message.answer("📬 Пользователям придёт следующее уведомление:")

    if not message.caption and not message.text:
        text_to_send = ""
    elif message.caption:
        text_to_send = message.caption
    else:
        text_to_send = message.text

    if message.text:
        await message.answer(html.escape(text_to_send))
        await state.update_data(msg_type="text", text=text_to_send)

    elif message.photo:
        await message.answer_photo(photo=message.photo[-1].file_id, caption=html.escape(text_to_send))
        await state.update_data(msg_type="photo", photo_id=message.photo[-1].file_id, caption=text_to_send)

    elif message.document:
        await message.answer_document(document=message.document.file_id, caption=html.escape(text_to_send))
        await state.update_data(msg_type="document", document_id=message.document.file_id, caption=text_to_send)

    elif message.sticker:
        await message.answer_sticker(sticker=message.sticker.file_id)
        await state.update_data(msg_type="sticker", sticker_id=message.sticker.file_id)

    elif message.audio:
        await message.answer_audio(audio=message.audio.file_id)
        await state.update_data(msg_type="audio", audio_id=message.audio.file_id, caption=text_to_send)

    elif message.animation:
        await message.answer_animation(animation=message.animation.file_id)
        await state.update_data(msg_type="animation", animation_id=message.audio.file_id, caption=text_to_send)

    else:
        await message.answer("❗️ Бот может рассылать только текст, фото, файлы, музыку, гифки и стикеры.")
        return

    await message.answer("Подтвердите отправку:", reply_markup=notify_approve_kb())
    await state.set_state(NotifyUsersSG.notify_approve)


@users_notify_router.callback_query(NotifyUsersSG.notify_approve, NotifyUsersApproveFactory.filter())
@inject
async def notify_approve(
        call: CallbackQuery,
        state: FSMContext,
        users_repo: FromDishka[UsersRepositoryI],
        l10n: LocalizedTranslator,
        callback_data: NotifyUsersApproveFactory,
):
    approved = callback_data.approved
    await call.answer()
    if not approved:
        await state.clear()
        await call.message.delete()
        await call.message.answer("Рассылка отменена.", reply_markup=main_menu_kb(l10n=l10n))
        return

    data = await state.get_data()
    await state.clear()

    msg_type = data.get("msg_type")
    target_language_code = data.get("target_language_code")
    if target_language_code in ["ru", "uz", "en"]:
        users = await users_repo.get_all_users(language_code=target_language_code)
    else:
        users = await users_repo.get_all_users()

    if not users:
        await call.message.answer("Ошибка. Пользователи отсутствуют.")
        return

    counter = 0
    await call.message.delete()
    await call.message.answer("Бот начал рассылку.", reply_markup=main_menu_kb(l10n=l10n))

    if msg_type == "text":
        text = data.get("text")
        try:
            for user in users:
                success = await send_text(bot=call.bot, user_id=user.telegram_id, text=html.escape(text),
                                          disable_notification=True)
                if not success[0] and success[1] == "bot_blocked":
                    await users_repo.update_user(User.telegram_id == user.telegram_id, is_active=False)
                else:
                    counter += 1
                await asyncio.sleep(0.05)
        finally:
            await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
            logging.info(f"Successfully sent messages: {counter}")

    elif msg_type == "photo":
        photo_id = data.get("photo_id")
        caption = data.get("caption")
        try:
            for user in users:
                success = await send_photo(bot=call.bot, user_id=user.telegram_id, photo_id=photo_id,
                                           caption=html.escape(caption), disable_notification=True)
                if not success[0] and success[1] == "bot_blocked":
                    await users_repo.update_user(User.telegram_id == user.telegram_id, is_active=False)
                else:
                    counter += 1
                await asyncio.sleep(0.05)
        finally:
            await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
            logging.info(f"Successfully sent messages: {counter}")

    elif msg_type == "document":
        document_id = data.get("document_id")
        caption = data.get("caption")
        try:
            for user in users:
                success = await send_document(bot=call.bot, user_id=user.telegram_id, document_id=document_id,
                                              caption=html.escape(caption), disable_notification=True)
                if not success[0] and success[1] == "bot_blocked":
                    await users_repo.update_user(User.telegram_id == user.telegram_id, is_active=False)
                else:
                    counter += 1
                await asyncio.sleep(0.05)
        finally:
            await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
            logging.info(f"Successfully sent messages: {counter}")

    elif msg_type == "audio":
        caption = data.get("caption")
        audio_id = data.get("audio_id")
        try:
            for user in users:
                success = await send_audio(bot=call.bot, user_id=user.telegram_id, audio_id=audio_id,
                                           caption=html.escape(caption), disable_notification=True)
                if not success[0] and success[1] == "bot_blocked":
                    await users_repo.update_user(User.telegram_id == user.telegram_id, is_active=False)
                else:
                    counter += 1
                await asyncio.sleep(0.05)
        finally:
            await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
            logging.info(f"Successfully sent messages: {counter}")

    elif msg_type == "animation":
        caption = data.get("caption")
        animation_id = data.get("animation_id")
        try:
            for user in users:
                success = await send_animation(bot=call.bot, user_id=user.telegram_id, animation_id=animation_id,
                                               caption=html.escape(caption), disable_notification=True)
                if not success[0] and success[1] == "bot_blocked":
                    await users_repo.update_user(User.telegram_id == user.telegram_id, is_active=False)
                else:
                    counter += 1
                await asyncio.sleep(0.05)
        finally:
            await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
            logging.info(f"Successfully sent messages: {counter}")

    elif msg_type == "sticker":
        sticker_id = data.get("sticker_id")
        try:
            for user in users:
                success = await send_sticker(bot=call.bot, user_id=user.telegram_id, sticker_id=sticker_id,
                                             disable_notification=True)
                if not success[0] and success[1] == "bot_blocked":
                    await users_repo.update_user(User.telegram_id == user.telegram_id, is_active=False)
                else:
                    counter += 1
                await asyncio.sleep(0.05)
        finally:
            await call.message.answer(f"📬 Успешно отправлено сообщений: {counter}")
            logging.info(f"Successfully sent messages: {counter}")