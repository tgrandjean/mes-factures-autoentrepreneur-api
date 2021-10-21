from datetime import date
from typing import Optional, List
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


class InvoiceForLatex(BaseModel):
    reference: str
    emited:  date
    issuer: Issuer
    customer: Customer
    prestations: List[Prestation]

    @property
    def total_without_charge(self):
        return sum([presta.total for presta in self.prestations])

    @property
    def total_by_vat(self):
        _ = dict.fromkeys(set([presta.vat for presta in self.prestations]),
                          0.0)
        for presta in self.prestations:
            _[presta.vat] += presta.total_vat
        return _

    @property
    def total_vat(self):
        return sum([presta.total_vat for presta in self.prestations])

    @property
    def total(self):
        return self.total_without_charge + self.total_vat

    @property
    def paginated_prestations(self):
        if len(self.prestations) <= 8:
            return [self.prestations]
        elif len(self.prestations) <= 12:
            return [self.prestations[:10], self.prestations[10:]]
        elif len(self.prestations) <= 24:
            return [self.prestations[:16], self.prestations[16:]]
        else:
            pages = []
            pages.append(self.prestations[:12])  # first page
            values = self.prestations[12:]
            num_pages = len(values) // 20
            for i in range(num_pages):
                pages.append(values[i * 20: (i + 1) * 20])
            offset = num_pages * 20
            pages.append(values[offset:])  # last page
            return pages


class RefreshUrlSchema(BaseModel):
    expiration: int = 7


# class InvoiceCustomerProjection(BaseModel):
#     customer: Customer

class PrestationsAggregation(BaseModel):
    title: str = Field(None, alias='_id')
    total_unit: int
    total_without_charge: float
    min_price: float
    max_price: float
