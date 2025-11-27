from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class OperatorCreate(BaseModel):
    name: str
    is_active: bool = True
    max_load: int = 5


class OperatorResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    max_load: int

    class Config:
        from_attributes = True


class SourceCreate(BaseModel):
    name: str
    description: Optional[str] = None


class SourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class LeadCreate(BaseModel):
    external_id: str
    phone: Optional[str] = None
    email: Optional[str] = None
    source_id: int


class LeadResponse(BaseModel):
    id: int
    external_id: str
    phone: Optional[str]
    email: Optional[str]
    source_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ContactCreate(BaseModel):
    lead_id: int
    source_id: int
    operator_id: Optional[int] = None
    is_active: bool = True


class ContactResponse(BaseModel):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int]
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class OperatorSourceWeightCreate(BaseModel):
    operator_id: int
    source_id: int
    weight: float = 1.0


class OperatorSourceWeightResponse(BaseModel):
    id: int
    operator_id: int
    source_id: int
    weight: float

    class Config:
        from_attributes = True
