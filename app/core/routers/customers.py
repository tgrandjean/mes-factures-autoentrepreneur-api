from typing import List
from fastapi import APIRouter, Depends

from app.users.models import UserDB
from app.core.documents import Invoice
from app.core.models import Customer

from pydantic import BaseModel, Field


class CustomerAgg(BaseModel):
    title: Customer = Field(None, alias='_id')
    total_invoices: int
    total_spent: float


def get_customers_router(app):

    router = APIRouter(tags=['customers'], prefix='/customers')

    @router.get('',
                responses={401: {"description": "Unauthorized"}},
                response_model=List[CustomerAgg])
    async def get_user_customers(
        user: UserDB = Depends(app.current_active_user)
            ):
        customers_agg = await Invoice.find(Invoice.issuer == user.id)\
                .aggregate(
                        [{"$group": {"_id": '$customer',
                                     "total_invoices": {"$sum": 1},
                                     "total_spent": {
                                        "$sum": "$total_without_charge"
                                        }
                                     }
                          }], projection_model=CustomerAgg).to_list()
        return customers_agg
    return router
