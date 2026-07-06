from .start import router as start_router
from .screenshots import router as screenshots_router
from .callbacks import router as callbacks_router
from .admin_menu import router as admin_menu_router

__all__ = [
    "start_router",
    "screenshots_router",
    "callbacks_router",
    "admin_menu_router",
]
