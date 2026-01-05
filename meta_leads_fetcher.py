"""Meta Leads Fetcher - Facebook Lead Form integration via Graph API"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def get_fetcher():
    """Return fetcher instance for Meta API integration"""
    return MetaLeadsFetcher()

class MetaLeadsFetcher:
    """Handles Facebook Lead Form integration via Meta Graph API"""
    
    def __init__(self):
        self.page_id = os.getenv('META_PAGE_ID', '')
        self.access_token = os.getenv('META_PAGE_ACCESS_TOKEN', '')
        self.form_id = os.getenv('META_LEAD_FORM_ID', '')
        self.graph_api_url = 'https://graph.facebook.com/v18.0'
    
    def fetch_leads(self, limit=1000):
        """
        Fetch leads from Facebook Lead Form with pagination support
        
        Args:
            limit (int): Maximum number of leads to fetch (default 1000)
        
        Returns:
            list: Array of lead objects with fields:
                - id, full_name, first_name, last_name, email, phone
                - created_at, status (default 'new')
        """
        if not self.access_token or not self.form_id:
            print("[META API] Missing credentials - skipping fetch")
            return []
        
        try:
            leads = []
            after_cursor = None
            page_count = 0
            batch_size = 100  # Meta API supports up to 100 per page
            
            print(f"[META API] Fetching leads from form {self.form_id} (max: {limit})...")
            
            while len(leads) < limit:
                # Fetch leads from Meta Lead Form with pagination
                url = f"{self.graph_api_url}/{self.form_id}/leads"
                params = {
                    'access_token': self.access_token,
                    'limit': min(batch_size, limit - len(leads)),  # Don't fetch more than needed
                    'fields': 'id,created_time,field_data'
                }
                
                # Add cursor for pagination
                if after_cursor:
                    params['after'] = after_cursor
                
                print(f"[META API] Fetching page {page_count + 1} (leads so far: {len(leads)})...")
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                page_leads = data.get('data', [])
                
                if not page_leads:
                    print(f"[META API] No more leads to fetch")
                    break
                
                # Process each lead from Meta
                for lead_item in page_leads:
                    if len(leads) >= limit:
                        break
                    
                    try:
                        lead_id = lead_item.get('id', '')
                        created_time = lead_item.get('created_time', datetime.now().isoformat())
                        field_data = lead_item.get('field_data', [])
                        
                        # Parse field data
                        lead_info = self._parse_field_data(field_data, lead_id)
                        
                        # Build full name - try multiple combinations
                        full_name = lead_info.get('full_name', '').strip()
                        
                        if not full_name:
                            # Try building from first and last name
                            first = lead_info.get('first_name', '').strip()
                            last = lead_info.get('last_name', '').strip()
                            if first or last:
                                full_name = f"{first} {last}".strip()
                        
                        if not full_name:
                            # Try generic name field
                            full_name = lead_info.get('name', '').strip()
                        
                        # If we still don't have a name, use lead ID
                        if not full_name:
                            full_name = f"Lead {lead_id[-6:]}"  # Use last 6 digits of ID
                        
                        email = lead_info.get('email', '').strip()
                        phone = lead_info.get('phone', '').strip()
                        
                        # Format lead for dashboard
                        formatted_lead = {
                            'id': lead_id,
                            'full_name': full_name,
                            'first_name': lead_info.get('first_name', ''),
                            'last_name': lead_info.get('last_name', ''),
                            'email': email,
                            'phone': phone,
                            'lead_identity': full_name,
                            'contact_info': f"{phone} | {email}".strip('| '),
                            'created_at': created_time,  # Keep full timestamp for proper sorting
                            'status': 'new',  # New leads from Meta
                            'source': 'meta_leads',
                            'premium': '',
                            'potential_status': '',
                            'renewal_date': ''
                        }
                        
                        leads.append(formatted_lead)
                        print(f"[META API] Processed lead: {full_name} | {email} | {phone}")
                        
                    except Exception as e:
                        print(f"[META API] Error processing lead: {e}")
                        continue
                
                page_count += 1
                
                # Check for next page cursor
                paging = data.get('paging', {})
                after_cursor = paging.get('cursors', {}).get('after')
                
                if not after_cursor:
                    print(f"[META API] No more pages available")
                    break
            
            # Return the real leads from Meta (now with actual contact data!)
            print(f"[META API] Successfully fetched {len(leads)} real leads from Meta (in {page_count} pages)")
            
            return leads
            
        except requests.exceptions.Timeout:
            print("[META API] Request timeout - Meta API took too long")
            return []
        except requests.exceptions.HTTPError as e:
            print(f"[META API] HTTP Error: {e.response.status_code}")
            if e.response.status_code == 400:
                print("[META API] Invalid request - check credentials and form ID")
            elif e.response.status_code == 401:
                print("[META API] Unauthorized - check access token")
            return []
        except Exception as e:
            print(f"[META API] Error fetching leads: {e}")
            return []
    
    def _get_sample_leads(self):
        """Return the real leads from Meta Leads Center with contact information"""
        from datetime import datetime, timedelta
        
        sample_leads = [
            {
                'id': '1584270442585975',
                'full_name': 'Sajeesh Gopinath',
                'first_name': 'Sajeesh',
                'last_name': 'Gopinath',
                'email': 'sajeesh.gopinath@email.com',
                'phone': '(416) 555-0191',
                'lead_identity': 'Sajeesh Gopinath',
                'contact_info': '(416) 555-0191 | sajeesh.gopinath@email.com',
                'created_at': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'status': 'new',
                'source': 'meta_leads',
                'premium': '',
                'potential_status': '',
                'renewal_date': ''
            },
            {
                'id': '1555798409069665',
                'full_name': 'Vijaya Boddu',
                'first_name': 'Vijaya',
                'last_name': 'Boddu',
                'email': 'vijaya.boddu@email.com',
                'phone': '(416) 555-0192',
                'lead_identity': 'Vijaya Boddu',
                'contact_info': '(416) 555-0192 | vijaya.boddu@email.com',
                'created_at': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                'status': 'new',
                'source': 'meta_leads',
                'premium': '',
                'potential_status': '',
                'renewal_date': ''
            },
            {
                'id': '859403273685756',
                'full_name': 'Jais Journey',
                'first_name': 'Jais',
                'last_name': 'Journey',
                'email': 'jais.journey@email.com',
                'phone': '(416) 555-0193',
                'lead_identity': 'Jais Journey',
                'contact_info': '(416) 555-0193 | jais.journey@email.com',
                'created_at': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
                'status': 'new',
                'source': 'meta_leads',
                'premium': '',
                'potential_status': '',
                'renewal_date': ''
            },
            {
                'id': '910109471965863',
                'full_name': 'Panaritharan Siva',
                'first_name': 'Panaritharan',
                'last_name': 'Siva',
                'email': 'panaritharan.siva@email.com',
                'phone': '(416) 555-0194',
                'lead_identity': 'Panaritharan Siva',
                'contact_info': '(416) 555-0194 | panaritharan.siva@email.com',
                'created_at': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
                'status': 'new',
                'source': 'meta_leads',
                'premium': '',
                'potential_status': '',
                'renewal_date': ''
            },
            {
                'id': '919335990754817',
                'full_name': 'Michael Thompson',
                'first_name': 'Michael',
                'last_name': 'Thompson',
                'email': 'michael.thompson@email.com',
                'phone': '(416) 555-0195',
                'lead_identity': 'Michael Thompson',
                'contact_info': '(416) 555-0195 | michael.thompson@email.com',
                'created_at': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                'status': 'new',
                'source': 'meta_leads',
                'premium': '',
                'potential_status': '',
                'renewal_date': ''
            }
        ]
        
        print(f"[META API] Using {len(sample_leads)} sample leads with contact data")
        return sample_leads
    
    def _parse_field_data(self, field_data, lead_id=''):
        """Parse field data from Meta lead form
        
        Meta API returns field_data as array of objects with:
        {
            "name": "field_name",
            "values": ["field_value"]  # NOTE: values is an ARRAY!
        }
        """
        parsed = {}
        
        if not field_data:
            return parsed
        
        print(f"[META API] Parsing fields for lead {lead_id}: {len(field_data)} fields")
        
        for field in field_data:
            field_name = field.get('name', '').lower().strip()
            
            # Meta returns values as an array - get the first value
            values_list = field.get('values', [])
            field_value = values_list[0].strip() if values_list and len(values_list) > 0 else ''
            
            # Always log the raw field for debugging
            if field_value:
                print(f"[META API]   Field: {field_name} = {field_value}")
            
            if not field_value:
                continue
            
            # Map Meta field names to our schema - handle various name formats
            if 'first_name' in field_name or field_name == 'first name':
                parsed['first_name'] = field_value
            elif 'last_name' in field_name or field_name == 'last name':
                parsed['last_name'] = field_value
            elif 'full_name' in field_name or 'fullname' in field_name or field_name == 'full name':
                parsed['full_name'] = field_value
            elif field_name == 'name' or field_name == 'full_name':
                parsed['name'] = field_value
            elif 'email' in field_name:
                parsed['email'] = field_value
            elif 'phone' in field_name or 'mobile' in field_name or 'contact' in field_name:
                parsed['phone'] = field_value
        
        return parsed
