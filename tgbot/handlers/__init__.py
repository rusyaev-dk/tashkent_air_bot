from .echo import echo_router
from .private import private_routers
from .errors import errors_router

routers_list = [
    *private_routers,
    echo_router,
    errors_router
]

__all__ = ["routers_list"]
