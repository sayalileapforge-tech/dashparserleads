"""
Meta API sync endpoints.

These endpoints manage synchronization of leads from Meta Lead Ads into the Lead Board database.

IMPORTANT: Sync is DISABLED by default until Meta credentials are provided.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.meta_service import MetaLeadAdsClient
from app.services.lead_service import LeadService
from app.schemas.lead import LeadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.get("/meta/status", tags=["sync"])
def meta_api_status():
    """
    Check Meta API integration status.
    
    Returns whether Meta API is enabled and credentials are configured.
    """
    client = MetaLeadAdsClient()
    
    return {
        "meta_api_enabled": client.is_enabled,
        "page_id_configured": bool(client.page_id),
        "access_token_configured": bool(client.access_token),
        "form_id_configured": bool(client.form_id),
        "app_secret_configured": bool(client.app_secret),
        "message": (
            "✅ Meta API is ENABLED and ready to sync"
            if client.is_enabled
            else "⚠️  Meta API is DISABLED - Missing credentials"
        )
    }


@router.get("/meta/forms")
def list_meta_forms():
    """
    List all Lead Ads forms available in your Meta account.
    
    This endpoint fetches available forms from Meta.
    Useful for identifying which forms you want to sync leads from.
    
    Returns:
        List of available lead forms
    """
    client = MetaLeadAdsClient()
    
    if not client.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meta API is not configured. Please add credentials to .env"
        )
    
    if not client.validate_credentials():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Meta API credentials are invalid. Please check your .env file"
        )
    
    forms = client.get_leadgen_forms()
    
    return {
        "success": True,
        "forms_count": len(forms),
        "forms": forms
    }


@router.post("/meta")
def sync_meta_leads(db: Session = Depends(get_db)):
    """
    Sync leads from Meta Lead Ads into the Lead Board.
    
    This endpoint:
    1. Connects to Meta API using configured credentials
    2. Fetches leads from the configured form
    3. Parses Meta lead data
    4. Syncs into the Lead Board database
    5. Deduplicates by meta_lead_id
    
    CREDENTIAL REQUIREMENT:
    - META_PAGE_ID (in .env)
    - META_PAGE_ACCESS_TOKEN (in .env)
    - META_FORM_ID (in .env)
    
    DISABLED if credentials are not configured.
    
    Returns:
        Sync statistics with counts of created/updated leads
    """
    client = MetaLeadAdsClient()
    
    # ============================================================
    # CHECK: Is Meta API enabled?
    # ============================================================
    if not client.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Meta API is not configured",
                "message": "Add META_PAGE_ID, META_PAGE_ACCESS_TOKEN, and META_FORM_ID to .env",
                "instructions": "See TODO_MARKERS.md for detailed setup instructions"
            }
        )
    
    # ============================================================
    # VALIDATE: Are credentials working?
    # ============================================================
    if not client.validate_credentials():
        logger.error("❌ Meta API credentials validation failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Meta API credentials are invalid",
                "message": "Check your META_PAGE_ID and META_PAGE_ACCESS_TOKEN in .env"
            }
        )
    
    logger.info("🔄 Starting Meta Lead Ads sync...")
    
    try:
        # ============================================================
        # STEP 1: Fetch leads from Meta
        # ============================================================
        logger.info("📥 Fetching leads from Meta API...")
        raw_leads = client.fetch_leads()
        
        if not raw_leads:
            logger.warning("No leads found in Meta API")
            return {
                "success": True,
                "message": "No leads to sync",
                "stats": {
                    "total": 0,
                    "created": 0,
                    "updated": 0,
                    "errors": 0
                }
            }
        
        logger.info(f"Fetched {len(raw_leads)} lead(s) from Meta")
        
        # ============================================================
        # STEP 2: Parse Meta lead data
        # ============================================================
        logger.info("🔍 Parsing leads...")
        parsed_leads = []
        for raw_lead in raw_leads:
            parsed = client.parse_lead_data(raw_lead)
            if parsed:
                parsed_leads.append(parsed)
        
        logger.info(f"Successfully parsed {len(parsed_leads)} lead(s)")
        
        # ============================================================
        # STEP 3: Sync into database
        # ============================================================
        logger.info("💾 Syncing leads into Lead Board database...")
        stats = LeadService.sync_meta_leads(db, parsed_leads)
        
        logger.info(
            f"✅ Sync complete! "
            f"Created: {stats['created']}, Updated: {stats['updated']}, Errors: {stats['errors']}"
        )
        
        return {
            "success": True,
            "message": f"Successfully synced {stats['created'] + stats['updated']} lead(s)",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Meta sync failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Meta sync failed",
                "message": str(e)
            }
        )


@router.get("/meta/test")
def test_meta_connection():
    """
    Test Meta API connection without syncing leads.
    
    Use this endpoint to validate that your credentials are correct
    before running a full sync.
    
    Returns:
        Status of API connection and credential validation
    """
    client = MetaLeadAdsClient()
    
    if not client.is_enabled:
        return {
            "success": False,
            "message": "Meta API is not configured",
            "details": "Add META_PAGE_ID, META_PAGE_ACCESS_TOKEN, and META_FORM_ID to .env"
        }
    
    is_valid = client.validate_credentials()
    
    return {
        "success": is_valid,
        "message": (
            "✅ Meta API credentials are valid and API is accessible"
            if is_valid
            else "❌ Meta API credentials are invalid or API is unreachable"
        ),
        "details": {
            "page_id": "✅ Configured" if client.page_id else "❌ Missing",
            "access_token": "✅ Configured" if client.access_token else "❌ Missing",
            "form_id": "✅ Configured" if client.form_id else "❌ Missing",
        }
    }
