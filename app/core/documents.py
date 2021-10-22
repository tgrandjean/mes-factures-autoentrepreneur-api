from typing import List, Optional
from datetime import datetime
from uuid import UUID
from beanie import Document
from pydantic import HttpUrl, validator
from .models import Customer, Prestation


class Invoice(Document):
    reference: str
    emited:  datetime
    issuer: UUID
    customer: Customer
    prestations: List[Prestation]
    filename: Optional[str]
    pdf_url: Optional[HttpUrl]
    total_without_charge: float = None

    @validator("total_without_charge", pre=True, always=True)
    def compute_total_without_charge(cls, v, values):
        return sum([presta.total for presta in values['prestations']])

    class Settings:
        use_revision = False

    class Collection:
        name = "invoices"
