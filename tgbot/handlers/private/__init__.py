from .bot_start import start_router
from .commands import commands_router
from .main_menu import menu_router
from .feedback import feedback_router
from .admin_commands import admin_router
from .dialogs.settings_dialog.dialogs import overall_settings_dialog

private_routers = [
    start_router,
    commands_router,
    menu_router,
    feedback_router,
    admin_router,
    overall_settings_dialog,
]

__all__ = ["private_routers"]
