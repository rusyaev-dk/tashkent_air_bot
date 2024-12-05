import html

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from infrastructure.database.models import UserLocal
from infrastructure.database.repositories.users_repo import UsersRepository
from l10n.translator import Translator
from tgbot.keyboards.reply import main_menu_kb
from tgbot.misc.states import SettingsSG
from tgbot.services.setup_bot_commands import update_user_commands


@inject
async def close_settings(
        call: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        l10n: FromDishka[Translator]
):
    await call.message.delete()
    await call.message.answer(l10n.get_text(key='main-menu-msg'), reply_markup=main_menu_kb(l10n=l10n))
    await dialog_manager.done()
    await dialog_manager.reset_stack()


@inject
async def switch_user_notifications(
        call: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        users_repo: FromDishka[UsersRepository],
        l10n: FromDishka[Translator]
):
    user_notifications: set = await users_repo.get_user_notification_hours(telegram_id=call.from_user.id)
    if len(user_notifications) == 0:
        await dialog_manager.switch_to(state=SettingsSG.change_notification_time)
        return

    user = await users_repo.get_user(telegram_id=call.from_user.id)
    if user.notifications:
        notifications = False
    else:
        notifications = True

    await users_repo.update_user(
        UserLocal.telegram_id == call.from_user.id,
        notifications=notifications
    )
    text = l10n.get_text(key="notifications-enabled" if notifications else "notifications-disabled")

    await call.answer(text)


@inject
async def select_notification(
        call: CallbackQuery,
        select: Select,
        dialog_manager: DialogManager,
        notification_id: str,
        users_repo: FromDishka[UsersRepository]
):
    selected_hour = notification_id[:2]

    selected_notifications: set = dialog_manager.dialog_data.get("selected_notifications")
    initial_hours: set = await users_repo.get_user_notification_hours(telegram_id=call.from_user.id)

    if selected_hour in selected_notifications:
        selected_notifications.remove(selected_hour)
    else:
        selected_notifications.add(selected_hour)

    has_changes = False
    if selected_notifications != initial_hours:
        has_changes = True

    dialog_manager.dialog_data.update(
        has_changes=has_changes,
        selected_notifications=selected_notifications
    )


@inject
async def select_all_notifications(
        call: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        users_repo: FromDishka[UsersRepository]
):
    selected_notifications: set = dialog_manager.dialog_data.get("selected_notifications")
    initial_hours: set = await users_repo.get_user_notification_hours(telegram_id=call.from_user.id)

    for hour in range(7, 24):
        hour = str(hour).zfill(2)
        selected_notifications.add(hour)

    has_changes = False
    if selected_notifications != initial_hours:
        has_changes = True

    dialog_manager.dialog_data.update(
        has_changes=has_changes,
        selected_notifications=selected_notifications
    )


@inject
async def deselect_all_notifications(
        call: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        users_repo: FromDishka[UsersRepository]
):
    selected_notifications: set = dialog_manager.dialog_data.get("selected_notifications")
    initial_hours: set = await users_repo.get_user_notification_hours(telegram_id=call.from_user.id)

    selected_notifications.clear()

    dialog_manager.dialog_data.update(
        has_changes=len(initial_hours) > 0,
        selected_notifications=selected_notifications
    )


@inject
async def save_selected_notifications(
        call: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        users_repo: FromDishka[UsersRepository],
        l10n: FromDishka[Translator]
):
    selected_notifications: set = dialog_manager.dialog_data.get("selected_notifications")
    await users_repo.update_user_notifications(
        telegram_id=call.from_user.id,
        hours=list(selected_notifications)
    )
    await call.answer(l10n.get_text(key='settings-applied'), show_alert=False)
    dialog_manager.dialog_data.clear()


async def cancel_notification_setting(
        call: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
):
    dialog_manager.dialog_data.clear()


@inject
async def change_user_language(
        call: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        users_repo: FromDishka[UsersRepository],
        l10n: FromDishka[Translator]
):
    language_code = button.widget_id[-2:]
    l10n.change_locale(language_code)

    await users_repo.update_user(UserLocal.telegram_id == call.from_user.id, language_code=language_code)

    await dialog_manager.done()
    await dialog_manager.reset_stack()
    await call.message.delete()
    await update_user_commands(bot=call.bot, l10n=l10n)
    args = {
        "name": html.escape(call.from_user.full_name),
        "terms_of_use": f"<a href='{l10n.get_text(key='terms-of-use-link')}'>"
                        f"<b>{l10n.get_text(key='terms-of-use-name')}</b></a>"
    }
    text = l10n.get_text(key="hello", args=args)
    await call.message.answer(text, reply_markup=main_menu_kb(l10n=l10n), disable_web_page_preview=True)
    await call.message.answer(l10n.get_text(key='hello-info'))
