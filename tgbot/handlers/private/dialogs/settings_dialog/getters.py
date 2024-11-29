from typing import List, Dict

from aiogram.types import User as AIOGRAMuser
from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from infrastructure.database.repositories.users_repo import UsersRepository
from l10n.translator import Translator
from tgbot.services import generate_random_id
from tgbot.services.micro_functions import find_notification_in_list


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


def notification_id_getter(notification: Dict) -> str:
    return notification.get("notification_id")


@inject
async def change_notifications_getter(
        dialog_manager: DialogManager,
        users_repo: FromDishka[UsersRepository],
        l10n: FromDishka[Translator],
        **kwargs
):
    user: AIOGRAMuser = dialog_manager.event.from_user
    chosen_notifications: List[Dict] = dialog_manager.dialog_data.get("chosen_notifications")
    made_changes_flag: bool = dialog_manager.dialog_data.get("made_changes_flag")

    if not chosen_notifications:
        if made_changes_flag:
            chosen_notifications = []
        else:
            chosen_notifications = await users_repo.get_user_notifications(telegram_id=user.id)
            dialog_manager.dialog_data.update(
                chosen_notifications=chosen_notifications,
                initial_notifications=chosen_notifications.copy(),
                initial_notifications_copy=chosen_notifications.copy(),
            )

    all_notifications: List[Dict] = []
    for hour in range(7, 24):
        hours = str(hour).zfill(2)  # Добавляем ведущий ноль, если час однозначный

        if find_notification_in_list(notifications_list=chosen_notifications, hours=hours):
            chosen_by_user = True
        else:
            chosen_by_user = False

        all_notifications.append(
            {
                "notification_id": hours + generate_random_id(5),
                "hours": hours,
                "minutes": "00",
                "chosen_by_user": chosen_by_user,
                "btn_text": f"✅ {hours}:00" if chosen_by_user else f"{hours}:00"
            }
        )
        # all_notifications.append(NotificationTimeModel(hours=hours, minutes="00",
        #                                                chosen_by_user=chosen_by_user))

    data = {
        "notification_objects": all_notifications,
        "made_changes": True if made_changes_flag else False,
        "choose_notif_time_text": l10n.get_text(key='choose-notification-time'),
        "save_btn_text": l10n.get_text(key='save-btn'),
        "chosen_more_one": True if len(chosen_notifications) > 1 else False,
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
