from aiogram.types import User as AIOGRAMuser
from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from infrastructure.database.repositories.users_repo import UsersRepository
from l10n.translator import Translator


@inject
async def overall_settings_getter(
        dialog_manager: DialogManager,
        users_repo: FromDishka[UsersRepository],
        l10n: FromDishka[Translator],
        **kwargs
):
    user: AIOGRAMuser = dialog_manager.event.from_user

    db_user = await users_repo.get_user(telegram_id=user.id)
    key = 'turn-notifications-off-btn' if db_user.notifications else 'turn-notifications-on-btn'

    data = {
        "choose_option_text": l10n.get_text(key='choose-option'),
        "notification_btn_text": l10n.get_text(key=key),
        "set_notif_time_btn_text": l10n.get_text(key='change-notification-time-btn'),
        "change_language_btn_text": l10n.get_text(key='change-language-btn'),
        "close_btn_text": l10n.get_text(key='close-btn')
    }

    return data


def notification_id_getter(notification: dict) -> str:
    return notification.get("hour")


@inject
async def change_notifications_getter(
        dialog_manager: DialogManager,
        users_repo: FromDishka[UsersRepository],
        l10n: FromDishka[Translator],
        **kwargs
):
    user: AIOGRAMuser = dialog_manager.event.from_user
    selected_notifications: set = dialog_manager.dialog_data.get("selected_notifications", set())
    has_changes: bool = dialog_manager.dialog_data.get("has_changes")

    initial_hours: set = await users_repo.get_user_notification_hours(telegram_id=user.id)

    if len(selected_notifications) == 0 and not has_changes:
        for hour in initial_hours:
            selected_notifications.add(hour)

        dialog_manager.dialog_data.update(
            made_changes_flag=False,
            selected_notifications=selected_notifications
        )

    notifications: list[dict] = []
    for hour in range(7, 24):  # keyboard buttons generating
        hour = str(hour).zfill(2)  # Add a leading zero if the hour is single-digit

        activated = hour in selected_notifications is not None
        notifications.append(
            {
                "hour": hour,
                "activated": activated,
                "btn_text": f"✅ {hour}:00" if activated else f"{hour}:00"
            }
        )

    data = {
        "notifications": notifications,
        "has_changes": has_changes,
        "chosen_more_one": len(selected_notifications) > 1,
        "choose_notif_time_text": l10n.get_text(key='choose-notification-time'),
        "save_btn_text": l10n.get_text(key='save-btn'),
        "deselect_all_btn_text": l10n.get_text(key='deselect-all-notifications-btn'),
        "back_btn_text": l10n.get_text(key='back-btn')
    }

    return data


@inject
async def change_language_getter(
        dialog_manager: DialogManager,
        l10n: FromDishka[Translator],
        **kwargs
):
    data = {
        "back_btn_text": l10n.get_text(key='back-btn')
    }

    return data
