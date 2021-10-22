from fastapi import APIRouter

from app.core.routers.invoices import get_invoices_router


def get_core_router(app):
    core_router = APIRouter()
    core_router.include_router(get_invoices_router(app))
    return core_router
