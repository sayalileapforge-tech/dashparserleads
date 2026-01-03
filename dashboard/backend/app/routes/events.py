"""Event Manager API endpoints - Meta Conversions API Integration."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadResponse
import logging
import requests
import hashlib
import json
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])

# Meta Event Manager Configuration
META_EVENT_MANAGER_URL = "https://graph.facebook.com/v18.0"
META_ACCESS_TOKEN = "EAAlfVZB2VnDsBQftsx2eKEGCu0E3tair0L04lXZB1D7OCU9JBtg5uaZCsFgNh9KBffUuRHf9BlwpSZAyAQSDTGobz4xKREPZAZCeSug9L3POSdPyoLX35w6xwEv3ec3UqHaaecO0Kxi5gIHgkDMJAZCneSOpQkwloNT7vfLrSt7TBi2AAxyk7y1PVTrU5l9LwZDZD"
META_DATASET_ID = "2251357192000496"


def hash_field(value):
    """Hash a field value for Meta Conversions API (SHA-256)."""
    if not value:
        return None
    return hashlib.sha256(str(value).lower().strip().encode()).hexdigest()


def send_to_meta_event_manager(lead):
    """
    Send lead data to Meta's Event Manager (Conversions API).
    
    Args:
        lead: Lead object from database
        
    Returns:
        Response from Meta API
    """
    # Prepare lead data for Meta Conversions API
    # Hashed fields for better matching
    user_data = {
        "em": hash_field(lead.email),  # Email
        "ph": hash_field(lead.phone),  # Phone
        "fn": hash_field(lead.first_name),  # First name
        "ln": hash_field(lead.last_name),  # Last name
        "city": hash_field(lead.city),  # City
        "st": hash_field(lead.state),  # State
        "zp": hash_field(lead.zip_code),  # Zip code
        "ct": hash_field(lead.country),  # Country
    }
    
    # Remove None values
    user_data = {k: v for k, v in user_data.items() if v is not None}
    
    # Prepare event data
    event_data = {
        "event_name": "Lead",  # Event type: Lead
        "event_time": int(datetime.utcnow().timestamp()),
        "event_id": f"lead_{lead.id}_{int(datetime.utcnow().timestamp())}",
        "user_data": user_data,
        "custom_data": {
            "lead_id": str(lead.id),
            "full_name": lead.full_name,
            "company_name": lead.company_name,
            "job_title": lead.job_title,
            "status": lead.status,
            "premium": (lead.auto_premium or 0) + (lead.home_premium or 0) + (lead.tenant_premium or 0),
            "source": "insurance_dashboard",
        }
    }
    
    # Build Meta Conversions API request
    url = f"{META_EVENT_MANAGER_URL}/{META_DATASET_ID}/events"
    params = {
        "access_token": META_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "data": [event_data],
        "test_event_code": "TEST19304"  # Your Meta test event code
    }
    
    try:
        logger.info(f"📤 Sending lead #{lead.id} ({lead.full_name}) to Meta Event Manager")
        logger.info(f"   Event Manager URL: {url}")
        logger.info(f"   Dataset ID: {META_DATASET_ID}")
        
        response = requests.post(url, json=payload, params=params, headers=headers, timeout=10)
        
        logger.info(f"   Response Status: {response.status_code}")
        logger.info(f"   Response: {response.text}")
        
        if response.status_code in [200, 201]:
            return {
                "success": True,
                "message": "Lead sent to Meta Event Manager successfully",
                "event_id": event_data["event_id"],
                "response": response.json()
            }
        else:
            return {
                "success": False,
                "message": f"Failed to send to Meta Event Manager: {response.status_code}",
                "error": response.text
            }
    except Exception as e:
        logger.error(f"Error sending to Meta Event Manager: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@router.post("/send-lead/{lead_id}", response_model=LeadResponse)
def send_lead_to_event_manager(lead_id: int, db: Session = Depends(get_db)):
    """
    Send a qualified lead to Meta Event Manager (Conversions API).
    
    This endpoint:
    1. Fetches the lead from database
    2. Hashes PII data (email, phone, etc.)
    3. Sends lead as conversion event to Meta Event Manager
    4. Returns confirmation
    
    Args:
        lead_id: The ID of the lead to send
        
    Returns:
        The lead data that was sent
        
    Raises:
        404: If lead not found
        500: If Event Manager send fails
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Send to Meta Event Manager
    result = send_to_meta_event_manager(lead)
    
    if not result["success"]:
        logger.error(f"Event Manager Error: {result}")
        raise HTTPException(status_code=500, detail=f"Failed to send to Event Manager: {result['message']}")
    
    logger.info(f"✅ Lead #{lead.id} sent successfully to Meta Event Manager")
    return LeadResponse.from_orm(lead)


@router.post("/webhook/event-manager")
def event_manager_webhook():
    """
    Webhook endpoint for Event Manager to send events back.
    
    This endpoint receives event notifications from Event Manager.
    """
    return {
        "status": "webhook_received",
        "message": "Event received successfully"
    }
