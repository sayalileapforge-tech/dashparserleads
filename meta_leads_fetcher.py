"""
Meta Lead Ads API fetcher.
Fetches real leads from Facebook Meta API using credentials from .env
"""
import os
import requests
from typing import List, Dict, Any
from datetime import datetime
from dotenv import dotenv_values

# Load credentials directly from .env file
env_paths = [
    'dashboard/backend/.env',
    '.env',
]

env_vars = {}
for path in env_paths:
    if os.path.exists(path):
        env_vars = dotenv_values(path)
        print(f"[LOADED] Credentials from: {path}")
        break

# Also load into os.environ for fallback
try:
    from dotenv import load_dotenv
    for path in env_paths:
        if os.path.exists(path):
            load_dotenv(path)
            break
except:
    pass

class MetaLeadsFetcher:
    """Fetch leads from Meta Lead Ads API."""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self):
        """Initialize with Meta credentials from environment."""
        # Try to get from env_vars dict first (from dotenv_values), then fallback to os.environ
        self.page_id = env_vars.get('META_PAGE_ID') or os.getenv('META_PAGE_ID')
        self.access_token = env_vars.get('META_PAGE_ACCESS_TOKEN') or os.getenv('META_PAGE_ACCESS_TOKEN')
        self.form_id = env_vars.get('META_LEAD_FORM_ID') or os.getenv('META_LEAD_FORM_ID')
        self.app_secret = env_vars.get('META_APP_SECRET') or os.getenv('META_APP_SECRET')
        
        # Debug: Show if credentials are loaded
        if self.form_id and self.access_token:
            print(f"[OK] Meta credentials loaded: Form ID={self.form_id}, Token={self.access_token[:30]}...")
        else:
            print(f"[WARN] Meta credentials missing - Form ID: {self.form_id}, Token: {bool(self.access_token)}")
    
    def fetch_leads(self, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Fetch real leads from Meta Lead Ads API.
        
        Args:
            limit: Maximum number of leads to fetch
            
        Returns:
            List of lead dictionaries from Facebook
        """
        if not self.form_id or not self.access_token:
            print("Meta credentials missing - cannot fetch leads from Facebook")
            return []
        
        try:
            # Call Meta Graph API to fetch leads
            url = f"{self.BASE_URL}/{self.form_id}/leads"
            params = {
                'access_token': self.access_token,
                'limit': limit,
                'fields': 'id,created_time,field_data'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            leads = data.get('data', [])
            
            print(f"Fetched {len(leads)} leads from Meta API")
            
            # Transform Meta leads to dashboard format
            return self._transform_leads(leads)
        
        except Exception as e:
            print(f"Error fetching Meta leads: {e}")
            return []
    
    def _transform_leads(self, meta_leads: List[Dict]) -> List[Dict[str, Any]]:
        """Transform Meta API response to dashboard format."""
        transformed = []
        
        for i, lead in enumerate(meta_leads, 1):
            # Extract field data
            field_data = lead.get('field_data', [])
            fields_dict = {}
            for field in field_data:
                fields_dict[field.get('name')] = field.get('values', [None])[0]
            
            # Extract email, phone, full_name from field_data
            email = fields_dict.get('email', '')
            phone = fields_dict.get('phone', '')
            full_name = fields_dict.get('full_name', 'Unknown Lead')
            
            # Try to get lead ID
            try:
                lead_id = int(lead.get('id', i))
            except (ValueError, TypeError):
                lead_id = i
            
            # Get created time from Meta
            created_at = lead.get('created_time', datetime.now().isoformat())
            
            transformed.append({
                'id': lead_id,
                # Dashboard expected fields
                'full_name': full_name,
                'first_name': full_name.split()[0] if full_name else 'Unknown',
                'last_name': full_name.split()[-1] if full_name and len(full_name.split()) > 1 else '',
                'email': email or '',
                'phone': phone or '',
                'created_at': created_at,
                'status': 'new',
                'signal': 'red',
                'auto_premium': '',
                'home_premium': '',
                'tenant_premium': '',
                'renewal_date': datetime.now().strftime('%Y-%m-%d'),
                # Also keep our custom fields for reference
                'lead_identity': full_name,
                'contact_info': f"{phone} | {email}",
                'premium_potential': 'High',
                'meta_signal': 'Active',
                'action': 'View'
            })
        
        return transformed
    
    def _get_sample_leads(self) -> List[Dict[str, Any]]:
        """Return sample leads for demo."""
        return [
            {
                'id': 1,
                'lead_identity': 'John Smith',
                'contact_info': '(416) 555-0123 | john.smith@email.com',
                'status': 'new',
                'premium_potential': 'High',
                'renewal_date': '2025-02-15',
                'meta_signal': '✓ Active',
                'action': 'View'
            },
            {
                'id': 2,
                'lead_identity': 'Sarah Johnson',
                'contact_info': '(647) 555-0456 | sarah.j@email.com',
                'status': 'contacted',
                'premium_potential': 'Medium',
                'renewal_date': '2025-03-20',
                'meta_signal': '✓ Engaged',
                'action': 'View'
            },
            {
                'id': 3,
                'lead_identity': 'Michael Chen',
                'contact_info': '(905) 555-0789 | m.chen@email.com',
                'status': 'qualified',
                'premium_potential': 'High',
                'renewal_date': '2025-01-10',
                'meta_signal': '✓ Ready',
                'action': 'View'
            },
            {
                'id': 4,
                'lead_identity': 'Emma Wilson',
                'contact_info': '(289) 555-0101 | emma.w@email.com',
                'status': 'new',
                'premium_potential': 'Low',
                'renewal_date': '2025-04-05',
                'meta_signal': '○ Pending',
                'action': 'View'
            },
            {
                'id': 5,
                'lead_identity': 'David Brown',
                'contact_info': '(416) 555-0202 | dbrown@email.com',
                'status': 'contacted',
                'premium_potential': 'Medium',
                'renewal_date': '2025-02-28',
                'meta_signal': '✓ Active',
                'action': 'View'
            }
        ]


# Singleton instance
_fetcher = None

def get_fetcher() -> MetaLeadsFetcher:
    """Get or create the Meta leads fetcher."""
    global _fetcher
    if _fetcher is None:
        _fetcher = MetaLeadsFetcher()
    return _fetcher
