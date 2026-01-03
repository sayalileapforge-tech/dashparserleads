"""
Lead service for database operations on the Lead Board.

This service manages:
1. CRUD operations for the Lead Board table
2. Syncing leads from Meta API into the database
3. Deduplication by meta_lead_id
4. Status management
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.lead import Lead, LeadStatus
from app.schemas.lead import LeadCreate

logger = logging.getLogger(__name__)


class LeadService:
    """Service for Lead Board database operations."""

    @staticmethod
    def create_lead(db: Session, lead_data: LeadCreate) -> Lead:
        """
        Create a new lead in the Lead Board.
        
        Checks for duplicates by meta_lead_id to prevent duplicates.
        
        Args:
            db: Database session
            lead_data: Lead data to create
            
        Returns:
            Created or existing Lead model instance
        """
        # Check if lead already exists (by meta_lead_id)
        if lead_data.meta_lead_id:
            existing = (
                db.query(Lead)
                .filter(Lead.meta_lead_id == lead_data.meta_lead_id)
                .first()
            )
            if existing:
                logger.debug(f"Lead {lead_data.meta_lead_id} already exists")
                return existing

        # Create new lead
        first_name = getattr(lead_data, 'first_name', '')
        last_name = getattr(lead_data, 'last_name', '')
        full_name = f"{first_name} {last_name}".strip()
        
        db_lead = Lead(
            meta_lead_id=lead_data.meta_lead_id,
            lead_form_id=getattr(lead_data, 'lead_form_id', None),
            source=getattr(lead_data, 'source', 'facebook'),
            
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            email=getattr(lead_data, 'email', None),
            phone=getattr(lead_data, 'phone', None),
            
            company_name=getattr(lead_data, 'company_name', None),
            job_title=getattr(lead_data, 'job_title', None),
            
            city=getattr(lead_data, 'city', None),
            state=getattr(lead_data, 'state', None),
            country=getattr(lead_data, 'country', None),
            zip_code=getattr(lead_data, 'zip_code', None),
            
            status=LeadStatus.NEW,
            notes=getattr(lead_data, 'notes', None),
            
            auto_premium=getattr(lead_data, 'auto_premium', None),
            home_premium=getattr(lead_data, 'home_premium', None),
            tenant_premium=getattr(lead_data, 'tenant_premium', None),
            
            custom_form_fields=getattr(lead_data, 'custom_form_fields', None),
            raw_payload=getattr(lead_data, 'raw_payload', None),
        )

        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        
        logger.info(f"✅ Created new lead: {db_lead.meta_lead_id} ({full_name})")
        return db_lead

    @staticmethod
    def sync_meta_leads(db: Session, leads_data: List[Dict]) -> Dict:
        """
        Sync leads from Meta API into the Lead Board.
        
        This method:
        1. Checks for duplicates (by meta_lead_id)
        2. Creates new leads
        3. Updates existing leads with new data
        4. Returns sync statistics
        
        Args:
            db: Database session
            leads_data: List of parsed lead dictionaries from Meta
            
        Returns:
            Dictionary with sync statistics:
            {
                "total": 10,
                "created": 8,
                "updated": 2,
                "errors": 0
            }
        """
        stats = {"total": len(leads_data), "created": 0, "updated": 0, "errors": 0}
        
        if not leads_data:
            logger.info("No leads to sync")
            return stats

        logger.info(f"🔄 Syncing {len(leads_data)} lead(s) from Meta...")

        for lead_dict in leads_data:
            try:
                meta_lead_id = lead_dict.get("meta_lead_id")
                
                if not meta_lead_id:
                    logger.warning("Skipping lead without meta_lead_id")
                    stats["errors"] += 1
                    continue

                # Check if lead already exists
                existing_lead = (
                    db.query(Lead)
                    .filter(Lead.meta_lead_id == meta_lead_id)
                    .first()
                )

                if existing_lead:
                    # Update existing lead with new data from Meta
                    existing_lead.lead_form_id = lead_dict.get("lead_form_id")
                    existing_lead.first_name = lead_dict.get("first_name")
                    existing_lead.last_name = lead_dict.get("last_name")
                    existing_lead.full_name = lead_dict.get("full_name")
                    existing_lead.email = lead_dict.get("email")
                    existing_lead.phone = lead_dict.get("phone")
                    existing_lead.company_name = lead_dict.get("company_name")
                    existing_lead.job_title = lead_dict.get("job_title")
                    existing_lead.city = lead_dict.get("city")
                    existing_lead.state = lead_dict.get("state")
                    existing_lead.country = lead_dict.get("country")
                    existing_lead.zip_code = lead_dict.get("zip_code")
                    existing_lead.custom_form_fields = lead_dict.get("custom_form_fields")
                    existing_lead.raw_payload = lead_dict.get("raw_payload")
                    existing_lead.meta_created_at = lead_dict.get("meta_created_at")
                    existing_lead.synced_at = datetime.utcnow()
                    
                    db.commit()
                    db.refresh(existing_lead)
                    logger.debug(f"Updated lead: {meta_lead_id}")
                    stats["updated"] += 1
                else:
                    # Create new lead from Meta data
                    new_lead = Lead(
                        meta_lead_id=meta_lead_id,
                        lead_form_id=lead_dict.get("lead_form_id"),
                        source=lead_dict.get("source", "facebook"),
                        
                        first_name=lead_dict.get("first_name"),
                        last_name=lead_dict.get("last_name"),
                        full_name=lead_dict.get("full_name"),
                        email=lead_dict.get("email"),
                        phone=lead_dict.get("phone"),
                        
                        company_name=lead_dict.get("company_name"),
                        job_title=lead_dict.get("job_title"),
                        
                        city=lead_dict.get("city"),
                        state=lead_dict.get("state"),
                        country=lead_dict.get("country"),
                        zip_code=lead_dict.get("zip_code"),
                        
                        status=LeadStatus.NEW,
                        custom_form_fields=lead_dict.get("custom_form_fields"),
                        raw_payload=lead_dict.get("raw_payload"),
                        meta_created_at=lead_dict.get("meta_created_at"),
                        synced_at=datetime.utcnow(),
                    )
                    
                    db.add(new_lead)
                    db.commit()
                    db.refresh(new_lead)
                    logger.debug(f"Created new lead from Meta: {meta_lead_id}")
                    stats["created"] += 1

            except Exception as e:
                logger.error(f"Error syncing lead {lead_dict.get('meta_lead_id')}: {str(e)}")
                stats["errors"] += 1
                db.rollback()
                continue

        logger.info(
            f"✅ Meta sync complete: "
            f"{stats['created']} created, {stats['updated']} updated, {stats['errors']} errors"
        )
        return stats

    @staticmethod
    def get_lead_by_meta_id(db: Session, meta_lead_id: str) -> Optional[Lead]:
        """
        Get lead by Meta Lead ID.
        
        Args:
            db: Database session
            meta_lead_id: Meta lead ID
            
        Returns:
            Lead model instance or None
        """
        return db.query(Lead).filter(Lead.meta_lead_id == meta_lead_id).first()

    @staticmethod
    def get_leads_by_status(db: Session, status: LeadStatus) -> List[Lead]:
        """
        Get all leads with a specific status.
        
        Args:
            db: Database session
            status: Lead status to filter by
            
        Returns:
            List of Lead model instances
        """
        return db.query(Lead).filter(Lead.status == status).all()

    @staticmethod
    def count_leads_by_status(db: Session) -> Dict[str, int]:
        """
        Count leads grouped by status.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with status counts
        """
        counts = {}
        for status in LeadStatus:
            count = db.query(Lead).filter(Lead.status == status).count()
            counts[status.value] = count
        return counts
