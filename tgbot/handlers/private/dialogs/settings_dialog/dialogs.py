from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Group, Row, Select
from aiogram_dialog.widgets.text import Format, Const

from tgbot.handlers.private.dialogs.settings_dialog.getters import overall_settings_getter, change_language_getter, \
    change_notifications_getter, notification_id_getter
from tgbot.handlers.private.dialogs.settings_dialog.callable import switch_user_notifications, change_user_language, \
    close_settings, select_notification, save_selected_notifications, cancel_notification_setting, \
    deselect_all_notifications, select_all_notifications
from tgbot.misc.constants import SET_USER_LANGUAGE_TEXT
from tgbot.misc.states import SettingsSG

overall_settings_window = Window(
    Format("{choose_option_text}"),
    Button(
        text=Format("{notification_btn_text}"),
        id="btn_toggle_notifications",
        on_click=switch_user_notifications
    ),
    SwitchTo(
        text=Format("{set_notif_time_btn_text}"),
        id="btn_go_to_set_notification_time",
        state=SettingsSG.change_notification_time
    ),
    SwitchTo(
        text=Format("{change_language_btn_text}"),
        id="btn_go_to_change_language",
        state=SettingsSG.change_language
    ),
    Button(
        text=Format("{close_btn_text}"),
        id="btn_close_settings",
        on_click=close_settings
    ),
    getter=overall_settings_getter,
    state=SettingsSG.overall_settings
)

change_user_notifications_window = Window(
    Format("{select_notif_time_text}"),
    Group(
        Select(
            text=Format("{item[btn_text]}"),
            items="notifications",
            item_id_getter=notification_id_getter,
            id="btn_select_notification",
            on_click=select_notification
        ),
        width=3
    ),
    SwitchTo(
        text=Format("{save_btn_text}"),
        id="btn_save_selected_notifications",
        when="has_changes",
        on_click=save_selected_notifications,
        state=SettingsSG.overall_settings
    ),
    Row(
        Button(
            text=Format("{select_all_btn_text}"),
            id="btn_select_all_notifications",
            when="selected_not_all",
            on_click=select_all_notifications
        ),
        Button(
            text=Format("{deselect_all_btn_text}"),
            id="btn_deselect_all_notifications",
            when="selected_more_one",
            on_click=deselect_all_notifications
        )
    ),
    SwitchTo(
        text=Format("{back_btn_text}"),
        id="btn_cancel_notification_setting",
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
            id="btn_set_language_ru",
            on_click=change_user_language
        ),
        Button(
            text=Const("🇺🇿 O'zbek"),
            id="btn_set_language_uz",
            on_click=change_user_language
        )
    ),
    Button(
        text=Const("🇬🇧 English"),
        id="btn_set_language_en",
        on_click=change_user_language
    ),
    SwitchTo(
        text=Format("{back_btn_text}"),
        id="btn_cancel_language_setting",
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
