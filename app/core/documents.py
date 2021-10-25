from typing import List, Optional
from datetime import datetime
from uuid import UUID
from beanie import Document, PydanticObjectId
import pymongo
from pymongo import IndexModel
from pydantic import EmailStr, HttpUrl, validator, root_validator
from .models import Address, Prestation


class Customer(Document):
    user: UUID
    company: bool
    name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    address: Optional[Address]
    email: Optional[EmailStr]
    phone: Optional[str]

    @root_validator(pre=True)
    def check_name(cls, values):
        if values['company'] and not values['name']:
            raise ValueError('Name cannot be left empty for company.')
        return values

    class Collection:
        name = "customers"

    class Settings:
        use_revision = False


class Invoice(Document):
    reference: str
    emited:  datetime
    issuer: UUID
    customer: PydanticObjectId
    prestations: List[Prestation]
    filename: Optional[str]
    total_without_charge: float = None

    @validator("total_without_charge", pre=True, always=True)
    def compute_total_without_charge(cls, v, values):
        return sum([presta.total for presta in values['prestations']])

    class Settings:
        use_revision = False

    class Collection:
        name = "invoices"


class Quotation(Invoice):
    title: str = 'Devis'
    
    class Collection:
        name = "quotations"


class S3Link(Document):
    document: PydanticObjectId
    created: datetime = None
    url: Optional[HttpUrl]

    @validator('created', pre=True, always=True)
    def set_created(cls, v):
        return v or datetime.now()

    class Collection:
        name = "s3_links"
        indexes = [
            IndexModel(
                [('created', pymongo.DESCENDING)],
                expireAfterSeconds=3600
            )
        ]
