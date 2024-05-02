from aiogram.fsm.state import StatesGroup, State


class SettingsSG(StatesGroup):
    overall_settings = State()
    change_language = State()
    change_notification_time = State()


class UserNotificationSettingSG(StatesGroup):
    turn_on_approve = State()


class FeedbackSG(StatesGroup):
    get_feedback = State()
    get_answer_to_user = State()


class NotifyUsersSG(StatesGroup):
    get_target_language_code = State()
    get_notify_media = State()
    notify_approve = State()
