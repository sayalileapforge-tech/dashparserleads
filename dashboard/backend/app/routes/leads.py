"""Lead API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.lead import Lead, LeadStatus, LeadSignal
from app.schemas.lead import (
    LeadResponse,
    LeadUpdate,
    LeadStatusUpdate,
    LeadSignalUpdate,
    LeadsListResponse,
)

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("", response_model=LeadsListResponse)
def get_leads(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=1000),
    status: str = Query(None),
    search: str = Query(None),
):
    """Fetch all leads from MySQL with pagination and filtering."""
    query = db.query(Lead)

    # Filter by status if provided
    if status:
        try:
            status_enum = LeadStatus(status)
            query = query.filter(Lead.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

    # Search by name, email, or phone
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Lead.full_name.ilike(search_term))
            | (Lead.email.ilike(search_term))
            | (Lead.phone.ilike(search_term))
        )

    # Count total
    total = query.count()

    # Pagination
    leads = query.offset((page - 1) * page_size).limit(page_size).all()

    return LeadsListResponse(
        total=total,
        page=page,
        page_size=page_size,
        leads=[LeadResponse.from_orm(lead) for lead in leads],
    )


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get a specific lead by ID."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.from_orm(lead)


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int, lead_update: LeadUpdate, db: Session = Depends(get_db)
):
    """Update lead information."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Update fields if provided
    update_data = lead_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)
    return LeadResponse.from_orm(lead)


@router.put("/{lead_id}/status", response_model=LeadResponse)
def update_lead_status(
    lead_id: int, status_update: LeadStatusUpdate, db: Session = Depends(get_db)
):
    """Update lead status."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Validate status
    try:
        new_status = LeadStatus(status_update.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")

    lead.status = new_status
    db.commit()
    db.refresh(lead)
    return LeadResponse.from_orm(lead)


@router.put("/{lead_id}/signal", response_model=LeadResponse)
def update_lead_signal(
    lead_id: int, signal_update: LeadSignalUpdate, db: Session = Depends(get_db)
):
    """Update lead signal (green/red) for Event Manager qualification."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Validate signal
    try:
        new_signal = LeadSignal(signal_update.signal)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid signal. Must be 'green' or 'red'")

    lead.signal = new_signal
    db.commit()
    db.refresh(lead)
    return LeadResponse.from_orm(lead)
