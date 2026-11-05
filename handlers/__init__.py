from aiogram import Router
from .common import router as common_router
from .library import router as library_router
from .quiz import router as quiz_router
from .rating import router as rating_router
from .daily import router as daily_router
from .contact import router as contact_router
from .admin import router as admin_router


def setup_routers() -> Router:
    """Barcha routerlarni bitta asosiy routerga birlashtirish."""
    main_router = Router()
    main_router.include_router(common_router)
    main_router.include_router(library_router)
    main_router.include_router(quiz_router)
    main_router.include_router(rating_router)
    main_router.include_router(daily_router)
    main_router.include_router(contact_router)
    main_router.include_router(admin_router)
    return main_router
