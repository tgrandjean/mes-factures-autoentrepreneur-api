from fastapi import APIRouter

from app.core.routers.invoices import get_invoices_router
from app.core.routers.prestations import get_prestations_router
from app.core.routers.customers import get_customers_router
from app.core.routers.quotations import get_quotations_router


def get_core_router(app):
    core_router = APIRouter()
    core_router.include_router(get_invoices_router(app))
    core_router.include_router(get_prestations_router(app))
    core_router.include_router(get_customers_router(app))
    core_router.include_router(get_quotations_router(app))
    return core_router
