from typing import List
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from beanie import PydanticObjectId

from app.users.models import UserDB
from app.core.documents import Invoice
from app.core.models import (InvoiceCreateSchema, InvoiceUpdateSchema, Message)
from app.core.utils import increment_reference
from app.core.background_tasks import generate_pdf_invoice


def get_invoices_router(app):

    router = APIRouter()

    @router.get('/invoices', response_model=List[Invoice],
                tags=['invoices'],
                summary="Return user's invoices",
                description="List all invoices for a specific user",
                responses={403: {"model": Message}})
    async def list_user_invoices(
        user: UserDB = Depends(app.current_active_user)
            ):
        invoices = await Invoice.find({"issuer": user.id}).to_list()
        return invoices

    @router.get('/invoices/{invoice_id}', response_model=Invoice,
                tags=['invoices'], responses={404: {"model": Message},
                                              403: {"model": Message}})
    async def get_invoice(invoice_id: PydanticObjectId,
                          user: UserDB = Depends(app.current_active_user)):
        invoice = await Invoice.get(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Not found")
        if invoice.issuer != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return invoice

    @router.post('/invoices', response_model=Invoice, tags=['invoices'],
                 status_code=201,
                 responses={404: {"model": Message},
                            403: {"model": Message},
                            201: {"model": Message}})
    async def create_invoice(invoice: InvoiceCreateSchema,
                             user: UserDB = Depends(app.current_active_user)):
        if not invoice.reference:
            last_invoice = await Invoice.find(Invoice.issuer == user.id)\
                .sort('-emited').limit(1).to_list()
            if last_invoice:
                current_ref = last_invoice.reference[0]
                invoice.reference = increment_reference(current_ref)
            else:
                invoice.reference = f"{datetime.now().year}-001"
        invoice_db = await Invoice(**invoice.dict(), issuer=user.id).create()
        return invoice_db

    @router.patch('/invoices', response_model=Invoice, tags=['invoices'],
                  responses={404: {"model": Message},
                             403: {"model": Message}})
    async def update_invoice(invoice_id: PydanticObjectId,
                             invoice: InvoiceUpdateSchema,
                             user: UserDB = Depends(app.current_active_user)):
        invoice_db = await Invoice.get(invoice_id)
        if not invoice_db:
            raise HTTPException(status_code=404, detail="Not found")
        if invoice_db.issuer != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        for field, value in invoice.dict(exclude_unset=True).items():
            setattr(invoice_db, field, value)
        invoice_db = await invoice_db.save()

    @router.delete('/invoices/{invoice_id}', response_model=Invoice,
                   responses={404: {"model": Message},
                              403: {"model": Message}},
                   tags=['invoices'])
    async def delete_invoice(invoice_id: PydanticObjectId,
                             user: UserDB = Depends(app.current_active_user)):
        invoice_db = await Invoice.get(invoice_id)
        if not invoice_db:
            raise HTTPException(status_code=404, detail="Not found")
        if invoice_db.issuer != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        await invoice_db.delete()
        return invoice_db

    @router.get('/invoices/{invoice_id}/generate', tags=['invoices'],
                status_code=202,
                responses={404: {"model": Message},
                           403: {"model": Message},
                           202: {"model": Message}})
    async def generate_pdf(invoice_id: PydanticObjectId,
                           backgroud_tasks: BackgroundTasks,
                           user: UserDB = Depends(app.current_active_user)):
        invoice_db = await Invoice.get(invoice_id)
        if not invoice_db:
            raise HTTPException(status_code=404, detail="Not found")
        if invoice_db.issuer != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        backgroud_tasks.add_task(generate_pdf_invoice,
                                 invoice_db, user,
                                 invoice_name=invoice_db.filename)
        return JSONResponse(status_code=202,
                            content=Message(message="Accepted").dict())

    return router
