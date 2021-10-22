from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator


class Address(BaseModel):
    address: str
    zip_code: int
    city: str


class RIB(BaseModel):
    name: Optional[str]
    iban: str
    bic: str


class Customer(BaseModel):
    name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    address: Optional[Address]
    email: Optional[EmailStr]
    phone: Optional[str]


class Prestation(BaseModel):
    title: str
    unit_price: float
    quantity: float
    vat: float = 0.0
    total: float = None

    @validator('total', always=True, pre=True)
    def compute_total(cls, v, values):
        return values['quantity'] * values['unit_price']

    @property
    def total_vat(self):
        return self.unit_price * self.quantity * (self.vat / 100)


class Issuer(BaseModel):
    first_name: str
    last_name: str
    company_name: str
    address: Optional[Address]
    siret: str
    intracom_vat: str
    logo: Optional[str]
    rib: Optional[RIB]
    email: EmailStr


class PrestationsAggregation(BaseModel):
    title: str = Field(None, alias='_id')
    total_unit: int
    total_without_charge: float
    min_price: float
    max_price: float


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
