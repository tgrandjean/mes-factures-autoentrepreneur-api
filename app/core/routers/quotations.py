from typing import List
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from beanie import PydanticObjectId

from app.users.models import UserDB
from app.core.documents import Customer, Quotation
from app.core.models import (InvoiceCreateSchema, InvoiceUpdateSchema,
                             Message)
from app.core.utils import increment_reference
from app.core.background_tasks import generate_pdf_invoice


def get_quotations_router(app):

    router = APIRouter(tags=['quotations'], prefix='/quotations')

    @router.get('', response_model=List[Quotation],
                summary="Return user's quotations",
                description="List all quotations for a specific user",
                responses={401: {"description": "Unauthorized"}})
    async def list_user_quotations(
        user: UserDB = Depends(app.current_active_user)
            ):
        quotations = await Quotation.find({"issuer": user.id}).to_list()
        return quotations

    @router.get('/{quotation_id}', response_model=Quotation,
                responses={404: {"description": "Not found"},
                           403: {"description": "Forbidden"}})
    async def get_quotation(quotation_id: PydanticObjectId,
                            user: UserDB = Depends(app.current_active_user)):
        quotation = await Quotation.get(quotation_id)
        if not quotation:
            raise HTTPException(status_code=404, detail="Not found")
        if quotation.issuer != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return quotation

    @router.post('', response_model=Quotation, status_code=201,
                 responses={404: {"description": "Not found"},
                            403: {"description": "Forbidden"},
                            201: {"model": Quotation}})
    async def create_quotation(quotation: InvoiceCreateSchema,
                               user: UserDB = Depends(app.current_active_user)
                               ):
        if not quotation.reference:
            last_quotation = await Quotation.find(Quotation.issuer == user.id)\
                .sort('-emited').limit(1).to_list()
            if last_quotation:
                current_ref = last_quotation[0].reference
                quotation.reference = increment_reference(current_ref)
            else:
                quotation.reference = f"{datetime.now().year}-001"
        quotation_db = await Quotation(**quotation.dict(), issuer=user.id)\
            .create()
        return quotation_db

    @router.patch('', response_model=Quotation,
                  responses={404: {"description": "Not found"},
                             403: {"description": "Forbidden"}})
    async def update_quotation(quotation_id: PydanticObjectId,
                               quotation: InvoiceUpdateSchema,
                               user: UserDB = Depends(app.current_active_user)
                               ):
        quotation_db = await Quotation.get(quotation_id)
        if not quotation_db:
            raise HTTPException(status_code=404, detail="Not found")
        if quotation_db.issuer != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        for field, value in quotation.dict(exclude_unset=True).items():
            setattr(quotation_db, field, value)
        quotation_db = await quotation_db.save()

    @router.delete('/{quotation_id}', response_model=Quotation,
                   responses={404: {"description": "Not found"},
                              403: {"description": "Forbidden"}})
    async def delete_quotation(quotation_id: PydanticObjectId,
                               user: UserDB = Depends(app.current_active_user)
                               ):
        quotation_db = await Quotation.get(quotation_id)
        if not quotation_db:
            raise HTTPException(status_code=404, detail="Not found")
        if quotation_db.issuer != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        await quotation_db.delete()
        return quotation_db

    @router.get('/{quotation_id}/generate',
                status_code=202,
                response_model=Message,
                responses={404: {"description": "Not found"},
                           403: {"description": "Forbidden"},
                           202: {"description": "Accepted"}})
    async def generate_pdf(quotation_id: PydanticObjectId,
                           backgroud_tasks: BackgroundTasks,
                           user: UserDB = Depends(app.current_active_user)):
        quotation_db = await Quotation.get(quotation_id)
        customer = await Customer.get(quotation_db.customer)
        if not quotation_db:
            raise HTTPException(status_code=404, detail="Not found")
        if quotation_db.issuer != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        backgroud_tasks.add_task(generate_pdf_invoice,
                                 quotation_db, user, customer,
                                 quotation_name=quotation_db.filename)
        return JSONResponse(status_code=202,
                            content=Message(message="Accepted").dict())

    return router
