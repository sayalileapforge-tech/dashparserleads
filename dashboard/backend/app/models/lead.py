"""Database models for leads and status tracking."""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Index, JSON
from app.core.database import Base


class LeadStatus(str, Enum):
    """Lead status enumeration - tracks processing state."""
    NEW = "new"                    # Just received from Meta
    PROCESSING = "processing"      # Currently being processed
    PROCESSED = "processed"        # Fully processed
    CONTACTED = "contacted"        # Legacy - kept for compatibility
    QUOTE_SENT = "quote_sent"      # Legacy - kept for compatibility
    CLOSED_WON = "closed_won"      # Legacy - kept for compatibility
    CLOSED_LOST = "closed_lost"    # Legacy - kept for compatibility
    NO_ANSWER = "no_answer"        # Legacy - kept for compatibility


class LeadSignal(str, Enum):
    """Lead signal enumeration - qualification indicator for Event Manager."""
    GREEN = "green"                # Lead is qualified, can be sent to Event Manager
    RED = "red"                    # Lead is not qualified, do not send


class Lead(Base):
    """
    Lead Board Table - Central repository for all leads from Meta Lead Ads.
    
    This table serves as the single source of truth for all lead data.
    All lead operations should read/write from this table.
    """
    __tablename__ = "leads"

    # ==================== PRIMARY KEY ====================
    id = Column(Integer, primary_key=True, index=True)

    # ==================== FACEBOOK/META FIELDS ====================
    # Unique identifier from Meta API
    meta_lead_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Form information from Meta
    lead_form_id = Column(String(255), index=True, nullable=True)
    
    # Source identifier
    source = Column(String(50), default="facebook", index=True)  # Always "facebook" for Meta leads

    # ==================== CONTACT INFORMATION ====================
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    full_name = Column(String(255), index=True, nullable=True)
    email = Column(String(255), index=True, nullable=True)
    phone = Column(String(20), index=True, nullable=True)
    
    # ==================== ADDITIONAL FIELDS ====================
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)

    # ==================== LOCATION ====================
    city = Column(String(255), nullable=True)
    state = Column(String(2), nullable=True)
    country = Column(String(255), nullable=True)
    zip_code = Column(String(20), nullable=True)

    # ==================== LEAD PROCESSING ====================
    status = Column(
        SQLEnum(LeadStatus), 
        index=True, 
        default=LeadStatus.NEW,
        comment="Processing status: new (from Meta), processing (being handled), or processed (complete)"
    )
    notes = Column(Text, nullable=True)
    
    # ==================== EVENT MANAGER SIGNAL ====================
    signal = Column(
        SQLEnum(LeadSignal),
        index=True,
        default=LeadSignal.RED,
        comment="Signal for Event Manager: green (qualified, send), red (not qualified, don't send)"
    )

    # ==================== INSURANCE PREMIUM FIELDS ====================
    auto_premium = Column(Integer, nullable=True)  # in cents
    home_premium = Column(Integer, nullable=True)  # in cents
    tenant_premium = Column(Integer, nullable=True)  # in cents

    # ==================== META API DATA ====================
    # Custom form fields from the specific lead form (JSON)
    # Stores any custom fields defined in the Meta Lead Form
    custom_form_fields = Column(JSON, nullable=True)
    
    # Complete raw payload from Meta API for debugging/audit
    raw_payload = Column(Text, nullable=True)

    # ==================== TIMESTAMPS ====================
    # When the lead was created in Meta system
    meta_created_at = Column(DateTime, nullable=True, comment="Timestamp from Meta API")
    
    # When we synced this lead from Meta (system time)
    synced_at = Column(DateTime, nullable=True, comment="When lead was synced from Meta")
    
    # When this record was created in our system
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # When this record was last updated
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ==================== INDEXES FOR PERFORMANCE ====================
    __table_args__ = (
        # Composite indexes for common queries
        Index('idx_lead_status_created', 'status', 'created_at'),
        Index('idx_lead_email_phone', 'email', 'phone'),
        Index('idx_lead_form_meta_id', 'lead_form_id', 'meta_lead_id'),
        Index('idx_lead_synced_status', 'synced_at', 'status'),
    )

    def to_dict(self):
        """Convert Lead Board record to dictionary."""
        return {
            # Internal IDs
            "id": self.id,
            "meta_lead_id": self.meta_lead_id,
            "lead_form_id": self.lead_form_id,
            "source": self.source,
            
            # Contact information
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            
            # Additional fields
            "company_name": self.company_name,
            "job_title": self.job_title,
            
            # Location
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "zip_code": self.zip_code,
            
            # Status and notes
            "status": self.status.value if self.status else None,
            "signal": self.signal.value if self.signal else LeadSignal.RED.value,
            "notes": self.notes,
            
            # Insurance premiums
            "auto_premium": self.auto_premium,
            "home_premium": self.home_premium,
            "tenant_premium": self.tenant_premium,
            
            # Meta API data
            "custom_form_fields": self.custom_form_fields,
            
            # Timestamps
            "meta_created_at": self.meta_created_at.isoformat() if self.meta_created_at else None,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
