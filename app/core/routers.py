from typing import List
from fastapi import APIRouter, Depends
from .documents import Invoice
from app.users.models import UserDB


def get_core_router(app):

    core_router = APIRouter()

    @core_router.get('/invoices', response_model=List[Invoice],
                     tags=['invoices'])
    async def list_user_invoices(
        user: UserDB = Depends(app.current_active_user)
            ):
        invoices = await Invoice.find({"issuer": user.id}).to_list()
        return invoices

    return core_router
