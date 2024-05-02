from .bot_start import start_router
from .commands.admin_commands import admin_commands_router
from .commands.notify_users import users_notify_router
from .commands.user_commands import user_commands_router
from .main_menu import menu_router
from .feedback import feedback_router
from .dialogs.settings_dialog.dialogs import overall_settings_dialog

private_routers = [
    start_router,
    user_commands_router,
    menu_router,
    feedback_router,
    admin_commands_router,
    users_notify_router,
    overall_settings_dialog,
]

__all__ = ["private_routers"]
