from typing import Optional
from fastapi_users import models
from app.core.models import Address, RIB


class User(models.BaseUser):
    first_name: str
    last_name: str
    company_name: str
    address: Optional[Address]
    siret: str
    intracom_vat: str
    logo: Optional[str]
    rib: Optional[RIB]


class UserCreate(models.BaseUserCreate):
    first_name: str
    last_name: str
    company_name: str
    address: Optional[Address]
    siret: str
    intracom_vat: str
    logo: Optional[str]
    rib: Optional[RIB]


class UserUpdate(models.BaseUserUpdate):
    first_name: Optional[str]
    last_name: Optional[str]
    company_name: Optional[str]
    address: Optional[Address]
    siret: Optional[str]
    intracom_vat: Optional[str]
    logo: Optional[str]
    rib: Optional[RIB]


class UserDB(User, models.BaseUserDB):
    pass
