"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LeadCreate(BaseModel):
    """Schema for creating a new lead."""
    meta_lead_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    raw_payload: Optional[str] = None


class LeadUpdate(BaseModel):
    """Schema for updating lead information."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    notes: Optional[str] = None


class LeadStatusUpdate(BaseModel):
    """Schema for updating lead status."""
    status: str


class LeadSignalUpdate(BaseModel):
    """Schema for updating lead signal."""
    signal: str


class LeadPremiumUpdate(BaseModel):
    """Schema for updating premium values."""
    auto_premium: Optional[int] = None
    home_premium: Optional[int] = None
    tenant_premium: Optional[int] = None


class LeadResponse(BaseModel):
    """Schema for lead response."""
    id: int
    meta_lead_id: str
    first_name: str
    last_name: str
    full_name: Optional[str] = None
    email: str
    phone: str
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    status: str
    signal: str = "red"
    notes: Optional[str] = None
    auto_premium: Optional[int] = None
    home_premium: Optional[int] = None
    tenant_premium: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    meta_created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeadsListResponse(BaseModel):
    """Schema for list of leads with pagination."""
    total: int
    page: int
    page_size: int
    leads: list[LeadResponse]
