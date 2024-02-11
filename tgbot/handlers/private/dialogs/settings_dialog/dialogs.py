from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Group, Row, Select
from aiogram_dialog.widgets.text import Format, Const

from tgbot.handlers.private.dialogs.settings_dialog.getters import overall_settings_getter, change_language_getter, \
    change_notifications_getter, notification_id_getter
from tgbot.handlers.private.dialogs.settings_dialog.callable import switch_user_notifications, change_user_language, \
    close_settings, change_user_notification_time, save_user_notification_settings, cancel_notification_setting, \
    deselect_all_user_notifications
from tgbot.misc.constants import SET_USER_LANGUAGE_TEXT
from tgbot.misc.states import SettingsSG

overall_settings_window = Window(
    Format("{choose_option_text}"),
    Button(
        text=Format("{notification_btn_text}"),
        id="notifications_button",
        on_click=switch_user_notifications
    ),
    SwitchTo(
        text=Format("{set_notif_time_btn_text}"),
        id="go_notif_setting_dialog",
        state=SettingsSG.change_notification_time
    ),
    SwitchTo(
        text=Format("{change_language_btn_text}"),
        id="change_language",
        state=SettingsSG.change_language
    ),
    Button(
        text=Format("{close_btn_text}"),
        id="close_settings",
        on_click=close_settings
    ),
    getter=overall_settings_getter,
    state=SettingsSG.overall_settings
)

change_user_notifications_window = Window(
    Format("{choose_notif_time_text}"),
    Group(
        Select(
            text=Format("{item[btn_text]}"),
            items="notification_objects",
            item_id_getter=notification_id_getter,
            id="select_notif_button",
            on_click=change_user_notification_time
        ),
        width=3
    ),
    Row(
        SwitchTo(
            text=Format("{save_btn_text}"),
            id="save_chosen_notifications",
            when="made_changes",
            on_click=save_user_notification_settings,
            state=SettingsSG.overall_settings
        ),
        Button(
            text=Format("{deselect_all_btn_text}"),
            id="deselect_all_notifications",
            when="chosen_more_one",
            on_click=deselect_all_user_notifications
        )
    ),
    SwitchTo(
        text=Format("{back_btn_text}"),
        id='cancel_notification_setting',
        on_click=cancel_notification_setting,
        state=SettingsSG.overall_settings
    ),
    getter=change_notifications_getter,
    state=SettingsSG.change_notification_time
)

change_user_language_window = Window(
    Const(SET_USER_LANGUAGE_TEXT),
    Row(
        Button(
            text=Const("🇷🇺 Русский"),
            id='ru_language',
            on_click=change_user_language
        ),
        Button(
            text=Const("🇺🇿 O'zbek"),
            id='uz_language',
            on_click=change_user_language
        )
    ),
    Button(
        text=Const("🇬🇧 English"),
        id='en_language',
        on_click=change_user_language
    ),
    SwitchTo(
        text=Format("{back_btn_text}"),
        id='cancel_language_setting',
        state=SettingsSG.overall_settings
    ),
    getter=change_language_getter,
    state=SettingsSG.change_language
)

overall_settings_dialog = Dialog(
    overall_settings_window,
    change_user_language_window,
    change_user_notifications_window,
)
