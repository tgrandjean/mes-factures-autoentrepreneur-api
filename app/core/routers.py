from typing import List
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from beanie import PydanticObjectId

from app.users.models import UserDB
from app.users.routers import fastapi_users
from .models import (InvoiceForLatex, Issuer, RefreshUrlSchema,
                     PrestationsAggregation)
from .documents import Invoice, InvoiceCreateSchema, InvoiceUpdateSchema
from .background_tasks import (create_and_upload_invoice,
                               delete_from_s3,
                               update_presigned_url)
from .utils.invoice_reference import increment_reference


current_active_user = fastapi_users.current_user(active=True)

router = APIRouter()


@router.get('/invoices', response_model=List[Invoice], tags=['invoices'])
async def list_user_invoices(user: UserDB = Depends(current_active_user)):
    invoices = await Invoice.find({"issuer": user.id}).to_list()
    return invoices


@router.get('/invoices/{invoice_id}', response_model=Invoice,
            tags=['invoices'])
async def get_invoice(invoice_id: PydanticObjectId,
                      user: UserDB = Depends(current_active_user)):
    invoice = await Invoice.get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Not found")
    if invoice.issuer != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return invoice


@router.post('/invoices/{invoice_id}/refresh-link', status_code=202,
             tags=['invoices'])
async def update_invoice_pdf_url(invoice_id: PydanticObjectId,
                                 refresh_data: RefreshUrlSchema,
                                 background_tasks: BackgroundTasks,
                                 user: UserDB = Depends(current_active_user)):
    invoice = await Invoice.get(invoice_id)
    if invoice.issuer != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    background_tasks.add_task(update_presigned_url, invoice,
                              refresh_data.expiration)


@router.post('/invoices', response_model=Invoice, tags=['invoices'])
async def create_invoice(invoice: InvoiceCreateSchema,
                         background_tasks: BackgroundTasks,
                         user: UserDB = Depends(current_active_user)):
    if not invoice.reference:
        last_invoice = await Invoice.find(Invoice.issuer == user.id)\
            .sort('-emited').to_list()
        if last_invoice:
            invoice.reference = increment_reference(last_invoice[0].reference)
        else:
            invoice.reference = f"{datetime.now().year}-001"
    invoice_db = await Invoice(**invoice.dict(), issuer=user.id).create()
    issuer = Issuer(**user.dict())
    invoice_for_latex = InvoiceForLatex(**invoice.dict(), issuer=issuer)
    background_tasks.add_task(create_and_upload_invoice,
                              invoice_db.id,
                              invoice_for_latex)
    return invoice_db


@router.patch('/invoices/{invoice_id}', response_model=Invoice,
              tags=['invoices'])
async def update_invoice(invoice_id: PydanticObjectId,
                         invoice: InvoiceUpdateSchema,
                         background_tasks: BackgroundTasks,
                         user: UserDB = Depends(current_active_user)):
    invoice_db = await Invoice.get(invoice_id)
    if not invoice_db:
        raise HTTPException(status_code=404, detail="Not found")
    if invoice_db.issuer != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    for field, value in invoice.dict(exclude_unset=True).items():
        setattr(invoice_db, field, value)
    invoice_db.pdf_url = None
    invoice_db = await invoice_db.save()
    issuer = Issuer(**user.dict())
    invoice = invoice_db.dict()
    invoice.pop('issuer')
    invoice_for_latex = InvoiceForLatex(**invoice, issuer=issuer)
    background_tasks.add_task(create_and_upload_invoice,
                              invoice_db.id,
                              invoice_for_latex,
                              invoice_db.filename)
    return invoice_db


@router.delete('/invoices/{invoice_id}', response_model=Invoice,
               tags=['invoices'])
async def delete_invoice(invoice_id: PydanticObjectId,
                         background_tasks: BackgroundTasks,
                         user: UserDB = Depends(current_active_user)):
    invoice_db = await Invoice.get(invoice_id)
    if not invoice_db:
        raise HTTPException(status_code=404, detail="Not found")
    if invoice_db.issuer != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    await invoice_db.delete()
    background_tasks.add_task(delete_from_s3, invoice_db.file_name)
    return invoice_db


@router.get('/prestations', tags=['prestations'],
            response_model=List[PrestationsAggregation])
async def get_user_prestations(user: UserDB = Depends(current_active_user)):
    prestations = await Invoice.find(Invoice.issuer == user.id).aggregate(
        [
            {"$unwind": "$prestations"},
            {"$group": {"_id": "$prestations.title",
                        "total_unit": {"$sum": "$prestations.quantity"},
                        "total_without_charge": {"$sum": "$prestations.total"},
                        "min_price": {"$min": "$prestations.unit_price"},
                        "max_price": {"$max": "$prestations.unit_price"},
                        }
             }
        ], projection_model=PrestationsAggregation
    ).to_list()
    return prestations


# @router.get('/customers/', response_model=List[Customer], tags=['customers'])
# async def list_user_customers(user: UserDB = Depends(current_active_user)):
#     # customers = await Invoice.find(Invoice.issuer == user.id)\
#     #     .aggregate([{'$replaceRoot':
#     #                     {'newRoot':
#     #                         {'$mergeObjects': [
#     #                                            {'_id': "$_id"}, '$customer'
#     #                                           ]
#     #                          }
#     #                      }
#     #                  }
#     #                 ], projection_model=Customer).to_list()
#     # .project(Customer).to_list()
#     # print(customers)
#     # customers = [p.customer for p in customers]
#     # return customers
