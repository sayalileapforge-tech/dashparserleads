"""
Meta Graph API integration for fetching leads from Meta Lead Ads.

This module handles all communication with the Meta API and is designed to be
activated once credentials are provided.

CREDENTIAL INJECTION POINTS:
===========================
1. META_PAGE_ID (in .env)
2. META_PAGE_ACCESS_TOKEN (in .env)
3. META_FORM_ID (in .env)
4. META_APP_SECRET (optional, in .env)

Once these are provided in the .env file, the Meta sync will be automatically enabled.
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class MetaLeadAdsClient:
    """
    Production-ready client for Meta Graph API to fetch leads from Lead Ads.
    
    IMPORTANT: This client is prepared but will remain disabled until credentials
    are provided via environment variables.
    
    Official Meta Documentation:
    - GET /{page_id}/leadgen_forms
    - GET /{form_id}/leads
    
    References:
    - https://developers.facebook.com/docs/marketing-api/reference/leadgen-form
    - https://developers.facebook.com/docs/marketing-api/reference/leadgen-form-field
    """

    # Meta API v18.0 or later
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    # API timeout (seconds)
    API_TIMEOUT = 30
    
    # Max retries for failed requests
    MAX_RETRIES = 3

    def __init__(self):
        """
        Initialize Meta API client with credentials from environment.
        
        CREDENTIALS REQUIRED:
        - META_APP_ID: Your Facebook App ID
        - META_APP_SECRET: Your Facebook App Secret
        - META_PAGE_ID: Your Facebook Page ID from Lead Ads setup
        - META_PAGE_ACCESS_TOKEN: Long-lived Page Access Token with leads access
        - META_LEAD_FORM_ID: Your specific Lead Form ID
        """
        # ============================================================
        # TODO: CREDENTIAL INJECTION POINT #1 - APP ID
        # ============================================================
        # Get from .env file (META_APP_ID)
        # Example: META_APP_ID=824389240430169
        self.app_id = settings.meta_app_id
        
        # ============================================================
        # TODO: CREDENTIAL INJECTION POINT #2 - APP SECRET
        # ============================================================
        # Get from .env file (META_APP_SECRET)
        # Example: META_APP_SECRET=5ddcbd165cf003632e8aa85c84cade43
        self.app_secret = settings.meta_app_secret
        
        # ============================================================
        # TODO: CREDENTIAL INJECTION POINT #3 - PAGE ID
        # ============================================================
        # Get from .env file (META_PAGE_ID)
        # Example: META_PAGE_ID=894819586548747
        # This is your Facebook Page ID that owns the Lead Ads forms
        self.page_id = settings.meta_page_id
        
        # ============================================================
        # TODO: CREDENTIAL INJECTION POINT #4 - ACCESS TOKEN
        # ============================================================
        # Get from .env file (META_PAGE_ACCESS_TOKEN)
        # Example: META_PAGE_ACCESS_TOKEN=EAALtxxPVHlkBQeoGRCbadQx...
        # This token must have these permissions:
        # - leads_retrieval
        # - read_insights
        # - read_page_mailboxes
        self.access_token = settings.meta_page_access_token
        
        # ============================================================
        # TODO: CREDENTIAL INJECTION POINT #5 - FORM ID
        # ============================================================
        # Get from .env file (META_LEAD_FORM_ID)
        # Example: META_LEAD_FORM_ID=1395244698621351
        # This is the specific Lead Form you want to fetch leads from
        self.form_id = settings.meta_lead_form_id
        
        self.is_enabled = self._check_enabled()

    def _parse_datetime(self, dt_str: str) -> Optional[str]:
        """
        Parse Meta's ISO datetime format to MySQL datetime format.
        Meta: "2025-11-28T20:37:28+0000" → MySQL: "2025-11-28 20:37:28"
        """
        if not dt_str:
            return None
        try:
            # Parse ISO format with timezone
            from datetime import datetime
            dt = datetime.fromisoformat(dt_str.replace("+0000", "+00:00"))
            # Return in MySQL format
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return None

    def _check_enabled(self) -> bool:
        """
        Check if Meta API integration is enabled and ready.
        
        Requires: PAGE_ID, ACCESS_TOKEN, and FORM_ID
        """
        required_fields = {
            'PAGE_ID': self.page_id,
            'ACCESS_TOKEN': self.access_token,
            'FORM_ID': self.form_id
        }
        
        missing = [name for name, value in required_fields.items() if not value]
        
        if missing:
            logger.warning(
                f"⚠️  Meta API integration is DISABLED - missing credentials: {', '.join(missing)}. "
                f"Set META_PAGE_ID, META_PAGE_ACCESS_TOKEN, and META_FORM_ID in .env to enable."
            )
            return False
        
        logger.info("✅ Meta API integration is ENABLED and ready")
        return True

    def validate_credentials(self) -> bool:
        """
        Validate Meta API credentials by making a test request.
        
        This should be called before attempting to fetch leads.
        
        Returns:
            True if credentials are valid and API is accessible
        """
        if not self.is_enabled:
            logger.error(
                "❌ Meta API is DISABLED - credentials not configured. "
                "Please add META_PAGE_ID, META_PAGE_ACCESS_TOKEN, and META_FORM_ID to .env"
            )
            return False

        try:
            # Test connectivity with page info request
            url = f"{self.BASE_URL}/{self.page_id}"
            params = {
                "access_token": self.access_token,
                "fields": "id,name,leads_allowed"
            }
            
            logger.info("🔍 Validating Meta API credentials...")
            response = requests.get(url, params=params, timeout=self.API_TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Meta API credentials validated - Page: {data.get('name')}")
                return True
            else:
                logger.error(f"❌ Meta API validation failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error validating Meta credentials: {str(e)}")
            return False

    def get_leadgen_forms(self) -> List[Dict]:
        """
        Fetch all Lead Ads forms associated with this page.
        
        Endpoint: GET /{page_id}/leadgen_forms
        
        Returns:
            List of lead form objects with id, name, etc.
        """
        if not self.is_enabled:
            logger.warning("Meta API is disabled - cannot fetch forms")
            return []

        try:
            url = f"{self.BASE_URL}/{self.page_id}/leadgen_forms"
            params = {
                "access_token": self.access_token,
                "fields": "id,name,created_time,status"
            }
            
            logger.info("📋 Fetching Lead Ads forms from Meta...")
            response = requests.get(url, params=params, timeout=self.API_TIMEOUT)

            if response.status_code != 200:
                logger.error(f"Failed to fetch forms: {response.text}")
                return []

            data = response.json()
            forms = data.get("data", [])
            logger.info(f"✅ Found {len(forms)} lead form(s)")
            return forms
            
        except Exception as e:
            logger.error(f"Error fetching leadgen forms: {str(e)}")
            return []

    def fetch_leads(self, form_id: Optional[str] = None) -> List[Dict]:
        """
        Fetch leads from Meta Lead Ads forms with automatic pagination.
        
        Endpoint: GET /{form_id}/leads
        
        Handles pagination automatically by fetching all available leads
        across multiple requests if needed.
        
        Args:
            form_id: The specific form to fetch leads from.
                    If None, uses the form_id from initialization
        
        Returns:
            List of all lead objects from Meta (merged from all pages)
        """
        if not self.is_enabled:
            logger.warning("Meta API is disabled - cannot fetch leads")
            return []

        # Use provided form_id or fall back to configured one
        target_form_id = form_id or self.form_id
        
        if not target_form_id:
            logger.error(
                "No form ID available. Pass form_id parameter or set META_LEAD_FORM_ID in .env"
            )
            return []

        all_leads = []
        after_cursor = None
        page_count = 0
        
        try:
            while True:
                url = f"{self.BASE_URL}/{target_form_id}/leads"
                
                # Request all available fields from Meta
                params = {
                    "access_token": self.access_token,
                    "fields": (
                        "id,"                      # Lead ID from Meta
                        "ad_id,"                   # Associated ad ID
                        "ad_name,"                 # Associated ad name
                        "created_time,"            # When lead was created
                        "field_data,"              # Custom form fields (array)
                        "form_id"                  # Form this lead came from
                    ),
                    "limit": 100  # Max 100 leads per request
                }
                
                # Add pagination cursor if we have one
                if after_cursor:
                    params["after"] = after_cursor
                
                logger.info(f"📥 Fetching leads from form {target_form_id} (page {page_count + 1})...")
                response = requests.get(url, params=params, timeout=self.API_TIMEOUT)

                if response.status_code != 200:
                    logger.error(f"Failed to fetch leads: {response.text}")
                    break

                data = response.json()
                leads = data.get("data", [])
                
                if not leads:
                    logger.info(f"No more leads to fetch (page {page_count + 1})")
                    break
                
                all_leads.extend(leads)
                logger.info(f"✅ Fetched {len(leads)} lead(s) from page {page_count + 1}")
                page_count += 1
                
                # Check for next page
                paging = data.get("paging", {})
                after_cursor = paging.get("cursors", {}).get("after")
                
                if not after_cursor:
                    logger.info(f"✅ Pagination complete. Fetched {len(all_leads)} total lead(s) across {page_count} page(s)")
                    break
            
            return all_leads
            
        except Exception as e:
            logger.error(f"Error fetching leads: {str(e)}")
            return all_leads  # Return whatever we've fetched so far

    def parse_lead_data(self, lead_raw: Dict) -> Dict:
        """
        Parse raw Meta lead data into our Lead Board schema.
        
        Converts Meta's field_data array format into a clean dictionary
        that matches our database schema.
        
        Args:
            lead_raw: Raw lead object from Meta API
            
        Returns:
            Structured lead dictionary matching Lead Board schema
        """
        try:
            # Extract field_data array from Meta
            field_data = lead_raw.get("field_data", [])
            
            # Convert Meta's array format to dictionary
            # Meta format: [{"name": "first_name", "values": ["John"]}, ...]
            lead_fields = {}
            custom_fields = {}
            
            for field in field_data:
                name = field.get("name", "").lower()
                # Meta returns "values" as array, get first value or empty string
                values = field.get("values", [])
                value = values[0] if values else ""
                
                # Store all fields
                lead_fields[name] = value
                
                # Keep non-standard fields in custom_fields
                if name not in ['first_name', 'last_name', 'email', 'phone_number', 'full_name',
                                'company', 'job_title', 'city', 'state', 'country', 'zip', 'phone']:
                    custom_fields[name] = value

            # Map Meta fields to our Lead Board schema
            parsed_lead = {
                # IDs and sources
                "meta_lead_id": lead_raw.get("id", ""),
                "lead_form_id": lead_raw.get("form_id", ""),
                "source": "facebook",
                
                # Contact information
                "first_name": lead_fields.get("first_name", ""),
                "last_name": lead_fields.get("last_name", ""),
                "email": lead_fields.get("email", ""),
                "phone": lead_fields.get("phone", "") or lead_fields.get("phone_number", ""),
                
                # Additional fields
                "company_name": lead_fields.get("company", ""),
                "job_title": lead_fields.get("job_title", ""),
                
                # Location
                "city": lead_fields.get("city", ""),
                "state": lead_fields.get("state", ""),
                "country": lead_fields.get("country", ""),
                "zip_code": lead_fields.get("zip", ""),
                
                # Status - all new leads from Meta start as NEW
                "status": "new",
                
                # Meta-specific data
                "meta_created_at": self._parse_datetime(lead_raw.get("created_time")),
                "synced_at": datetime.utcnow().isoformat(),
                "custom_form_fields": custom_fields if custom_fields else None,
                
                # Full raw payload for audit/debugging
                "raw_payload": json.dumps(lead_raw),
            }

            # Set full name - prefer full_name field if available
            full_name = lead_fields.get("full_name", "").strip()
            if not full_name:
                first = lead_fields.get("first_name", "").strip()
                last = lead_fields.get("last_name", "").strip()
                full_name = f"{first} {last}".strip() if (first or last) else ""
            
            parsed_lead["full_name"] = full_name

            logger.debug(f"Parsed lead: {parsed_lead.get('meta_lead_id')} - {parsed_lead.get('full_name')}")
            return parsed_lead

        except Exception as e:
            logger.error(f"Error parsing lead data: {str(e)}")
            return {}
