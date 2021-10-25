from typing import List
from fastapi import APIRouter, Depends, HTTPException
import pydantic
from beanie import PydanticObjectId

from app.responses import UNAUTHORIZED, FORBIDDEN, NOT_FOUND, CONFLICT
from app.users.models import UserDB
from app.core.documents import Customer
from app.core.models import CustomerIn


def get_customers_router(app):

    router = APIRouter(tags=['customers'], prefix='/customers')

    @router.get('', responses=dict([UNAUTHORIZED]),
                response_model=List[Customer])
    async def get_user_customers(
                user: UserDB = Depends(app.current_active_user)
            ):
        customers = await Customer.find({'user': user.id}).to_list()
        return customers

    @router.get('/{customer_id}',
                responses=dict([UNAUTHORIZED, FORBIDDEN, NOT_FOUND]),
                response_model=Customer)
    async def get_customer(
                customer_id: PydanticObjectId,
                user: UserDB = Depends(app.current_active_user)
            ):
        customer = await Customer.get(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Not found")
        if customer.user != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return customer

    @router.post('', status_code=201,
                 response_model=Customer,
                 responses=dict([UNAUTHORIZED, CONFLICT]))
    async def create_customer(
                customer: CustomerIn,
                user: UserDB = Depends(app.current_active_user)
            ):
        customer_dict = customer.dict(exclude_unset=True)
        customer_dict['user'] = user.id
        customer_db = await Customer.find_one(customer_dict)
        if customer_db:
            raise HTTPException(status_code=409, detail="Already exists")
        try:
            customer = await Customer(**customer.dict(), user=user.id).create()
        except pydantic.error_wrappers.ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())
        return customer

    return router
