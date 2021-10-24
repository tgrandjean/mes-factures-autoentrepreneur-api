from typing import List
from fastapi import APIRouter, Depends

from app.users.models import UserDB
from app.core.documents import Invoice
from app.core.models import PrestationsAggregation


def get_prestations_router(app):

    router = APIRouter(tags=['prestations'])

    @router.get('/prestations',
                responses={401: {"description": "Unauthorized"}},
                response_model=List[PrestationsAggregation])
    async def get_user_prestations(
        user: UserDB = Depends(app.current_active_user)
            ):
        prestations = await Invoice.find(Invoice.issuer == user.id).aggregate(
            [
                {"$unwind": "$prestations"},
                {"$group": {"_id": "$prestations.title",
                            "total_unit": {"$sum": "$prestations.quantity"},
                            "total_without_charge": {
                                "$sum": "$prestations.total"
                                },
                            "min_price": {"$min": "$prestations.unit_price"},
                            "max_price": {"$max": "$prestations.unit_price"}
                            }
                 }
            ],
            projection_model=PrestationsAggregation
        ).to_list()
        return prestations

    return router
