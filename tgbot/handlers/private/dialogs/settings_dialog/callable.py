import html
from typing import List, Dict

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
from tgbot.services import generate_random_id
from tgbot.services.micro_functions import find_notification_in_list, compare_notifications_lists
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
    user_notifications = await users_repo.get_user_notifications(telegram_id=call.from_user.id)
    if not user_notifications:
        await dialog_manager.switch_to(state=SettingsSG.change_notification_time)
        return

    user = await users_repo.get_user(telegram_id=call.from_user.id)
    if user.notifications:
        notifications = False
    else:
        notifications = True

    await users_repo.update_user(UserLocal.telegram_id == call.from_user.id, notifications=notifications)
    text = l10n.get_text(key="notifications-enabled") if notifications else l10n.get_text(key="notifications-disabled")

    await call.answer(text)


async def change_user_notification_time(
        call: CallbackQuery,
        select: Select,
        dialog_manager: DialogManager,
        notification_id: str
):
    selected_hours = notification_id[:2]

    chosen_notifications: List[Dict] = dialog_manager.dialog_data.get("chosen_notifications")
    initial_notifications: List[Dict] = dialog_manager.dialog_data.get("initial_notifications")

    if find_notification_in_list(notifications_list=chosen_notifications, hours=selected_hours):
        for notification_time in chosen_notifications:
            if notification_time.get("hours") == selected_hours:
                chosen_notifications.remove(notification_time)
                break
    else:
        chosen_notifications.append(
            {
                "notification_id": selected_hours + generate_random_id(5),
                "hours": selected_hours,
                "minutes": "00",
                "chosen_by_user": True,
                "btn_text": f"✅ {selected_hours}:00"
            }
        )

    equal = compare_notifications_lists(initial_notifications, chosen_notifications)

    dialog_manager.dialog_data.update(
        made_changes_flag=not equal,
        chosen_notifications=chosen_notifications
    )


async def deselect_all_user_notifications(
        call: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    initial_notifications: List[Dict] = dialog_manager.dialog_data.get("initial_notifications")
    initial_notifications_copy: List[Dict] = dialog_manager.dialog_data.get("initial_notifications_copy")
    chosen_notifications: List[Dict] = dialog_manager.dialog_data.get("chosen_notifications")

    if len(initial_notifications_copy) > 0:
        initial_notifications_copy.clear()
        dialog_manager.dialog_data.update(
            initial_notifications_copy=initial_notifications_copy,
        )

    chosen_notifications.clear()

    if compare_notifications_lists(initial_notifications, chosen_notifications):
        made_changes_flag = False
    else:
        made_changes_flag = True

    dialog_manager.dialog_data.update(
        made_changes_flag=made_changes_flag,
        chosen_notifications=chosen_notifications
    )


@inject
async def save_user_notification_settings(
        call: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        users_repo: FromDishka[UsersRepository],
        l10n: FromDishka[Translator]
):
    chosen_notifications: List = dialog_manager.dialog_data.get("chosen_notifications")
    await users_repo.update_user_notifications(
        telegram_id=call.from_user.id,
        notifications=chosen_notifications
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
    language_code = button.widget_id[:2]
    l10n.change_locale(language_code)

    await users_repo.update_user(UserLocal.telegram_id == call.from_user.id, language=language_code)

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
