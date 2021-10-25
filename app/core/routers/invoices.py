from typing import List
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from beanie import PydanticObjectId

from app.responses import ACCEPTED, UNAUTHORIZED, FORBIDDEN, NOT_FOUND
from app.users.models import UserDB
from app.core.documents import Customer, Invoice, S3Link
from app.core.models import (InvoiceCreateSchema, InvoiceUpdateSchema, Message)
from app.core.utils import increment_reference
from app.core.background_tasks import generate_pdf_invoice


def get_invoices_router(app):

    router = APIRouter(tags=['invoices'], prefix='/invoices')

    @router.get('', response_model=List[Invoice],
                summary="Return user's invoices",
                description="List all invoices for a specific user",
                responses=dict([UNAUTHORIZED]))
    async def list_user_invoices(
        user: UserDB = Depends(app.current_active_user)
            ):
        invoices = await Invoice.find({"issuer": user.id}).to_list()
        return invoices

    @router.get('/{invoice_id}', response_model=Invoice,
                responses=dict([FORBIDDEN, NOT_FOUND]))
    async def get_invoice(invoice_id: PydanticObjectId,
                          user: UserDB = Depends(app.current_active_user)):
        invoice = await Invoice.get(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Not found")
        if invoice.issuer != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return invoice

    @router.post('', response_model=Invoice, status_code=201,
                 responses=dict([(201, {"model": Invoice}), UNAUTHORIZED]))
    async def create_invoice(invoice: InvoiceCreateSchema,
                             user: UserDB = Depends(app.current_active_user)):
        if not invoice.reference:
            last_invoice = await Invoice.find(Invoice.issuer == user.id)\
                .sort('-emited').limit(1).to_list()
            if last_invoice:
                current_ref = last_invoice[0].reference
                invoice.reference = increment_reference(current_ref)
            else:
                invoice.reference = f"{datetime.now().year}-001"
        invoice_db = await Invoice(**invoice.dict(), issuer=user.id).create()
        return invoice_db

    @router.patch('', response_model=Invoice,
                  responses=dict([UNAUTHORIZED, FORBIDDEN, NOT_FOUND]))
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

    @router.delete('/{invoice_id}', response_model=Invoice,
                   responses=dict([UNAUTHORIZED, FORBIDDEN, NOT_FOUND]))
    async def delete_invoice(invoice_id: PydanticObjectId,
                             user: UserDB = Depends(app.current_active_user)):
        invoice_db = await Invoice.get(invoice_id)
        if not invoice_db:
            raise HTTPException(status_code=404, detail="Not found")
        if invoice_db.issuer != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        await invoice_db.delete()
        return invoice_db

    @router.get('/{invoice_id}/generate',
                status_code=202,
                response_model=Message,
                responses=dict([ACCEPTED, UNAUTHORIZED, FORBIDDEN, NOT_FOUND]))
    async def generate_pdf(invoice_id: PydanticObjectId,
                           backgroud_tasks: BackgroundTasks,
                           user: UserDB = Depends(app.current_active_user)):
        invoice_db = await Invoice.get(invoice_id)
        customer = await Customer.get(invoice_db.customer)
        if not invoice_db:
            raise HTTPException(status_code=404, detail="Not found")
        if invoice_db.issuer != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        backgroud_tasks.add_task(generate_pdf_invoice,
                                 invoice_db, user, customer,
                                 invoice_name=invoice_db.filename)
        await S3Link(document=invoice_db.id, url="http://example.com")\
            .create()
        return JSONResponse(status_code=202,
                            content=Message(message="Accepted").dict())

    return router
