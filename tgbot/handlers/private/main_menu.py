from aiogram import Router, flags, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode

from infrastructure.database.repository.requests import RequestsRepo
from l10n.translator import LocalizedTranslator
from tgbot.keyboards.inline import aqi_forecast_kb, WeekAqiForecastFactory
from tgbot.keyboards.reply import feedback_kb
from tgbot.misc.states import FeedbackSG, SettingsSG
from tgbot.services.format_functions import format_current_aqi_info, format_reference_text, format_forecast_aqi_info

menu_router = Router()


@menu_router.message(F.text.in_(["Индекс качества воздуха", "Air quality index", "Havo sifati indeksi"]))
@flags.rate_limit(key="default")
async def get_aqi(
        message: Message,
        repo: RequestsRepo,
        l10n: LocalizedTranslator,
        dialog_manager: DialogManager
):
    await dialog_manager.reset_stack()
    current_aqi = await repo.aqi.get_current_aqi()
    forecast_list = await repo.aqi.get_forecast_aqi()
    if not current_aqi:
        await message.answer(l10n.get_text(key="response-error"))
        return
    text = format_current_aqi_info(current_aqi=current_aqi, l10n=l10n)
    keyboard = aqi_forecast_kb(l10n=l10n) if len(forecast_list) > 0 else None
    await message.answer(text, reply_markup=keyboard)


@menu_router.callback_query(WeekAqiForecastFactory.filter())
async def get_aqi_forecast(
        call: CallbackQuery,
        repo: RequestsRepo,
        l10n: LocalizedTranslator
):
    forecast_list = await repo.aqi.get_forecast_aqi()
    if len(forecast_list) == 0:
        await call.answer(l10n.get_text(key="no-forecast-error"), show_alert=True)
        return
    text = format_forecast_aqi_info(forecast_list=forecast_list, l10n=l10n)
    await call.answer()
    await call.message.answer(text)
    await call.message.edit_reply_markup()


@menu_router.message(F.text.in_(["ℹ️ Полезно", "ℹ️ Informative", "ℹ️ Ma'lumot beruvchi"]))
@flags.rate_limit(key="default")
async def get_reference(
        message: Message,
        l10n: LocalizedTranslator,
        dialog_manager: DialogManager
):
    await dialog_manager.reset_stack()
    text = format_reference_text(l10n=l10n)
    await message.answer(text, disable_web_page_preview=True)


@menu_router.message(F.text.in_(["🔧 Настройки", "🔧 Settings", "🔧 Sozlamalar"]))
@flags.rate_limit(key="default")
async def settings(
        message: Message,
        dialog_manager: DialogManager
):
    await dialog_manager.start(
        state=SettingsSG.overall_settings,
        mode=StartMode.RESET_STACK,
    )


@menu_router.message(F.text.in_(["📩 Обратная связь", "📩 Feedback", "📩 Fikr-mulohaza"]))
@flags.rate_limit(key="default")
async def feedback(
        message: Message,
        state: FSMContext,
        l10n: LocalizedTranslator,
        dialog_manager: DialogManager
):
    await dialog_manager.reset_stack()
    await message.answer(l10n.get_text(key="send-feedback"),
                         reply_markup=feedback_kb(l10n=l10n))
    await state.set_state(FeedbackSG.get_feedback)
