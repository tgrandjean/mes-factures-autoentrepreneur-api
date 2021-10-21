from typing import List, Optional
from datetime import datetime
from uuid import UUID
from beanie import Document
from pydantic import BaseModel, HttpUrl, validator
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
    # total: float = None

    @validator("total_without_charge", pre=True, always=True)
    def compute_total_without_charge(cls, v, values):
        return sum([presta.total for presta in values['prestations']])

    class Settings:
        use_revision = False

    class Collection:
        name = "invoices"


class InvoiceCreateSchema(BaseModel):
    reference: Optional[str]
    emited:  Optional[datetime] = None
    customer: Customer
    prestations: List[Prestation]

    @validator('emited', pre=True, always=True)
    def set_emitted(cls, v):
        return v or datetime.now()


class InvoiceUpdateSchema(BaseModel):
    reference: Optional[str]
    emited: Optional[datetime]
    customer: Optional[Customer]
    prestations: Optional[List[Prestation]]
