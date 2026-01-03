#!/usr/bin/env python
"""Debug script to fetch ALL available data from Meta leads"""

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

form_id = os.getenv('META_LEAD_FORM_ID', '')
access_token = os.getenv('META_PAGE_ACCESS_TOKEN', '')

if form_id and access_token:
    # Try multiple field configurations to get real data
    url = f"https://graph.facebook.com/v18.0/{form_id}/leads"
    
    # Try with just basic fields first
    print("=== ATTEMPT 1: Basic fields ===")
    params = {
        'access_token': access_token,
        'limit': 5,
        'fields': 'id,created_time,field_data'
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if data.get('data'):
        for idx, lead in enumerate(data['data'][:3], 1):
            print(f"\nLead {idx}:")
            print(f"  ID: {lead.get('id')}")
            print(f"  Created: {lead.get('created_time')}")
            print(f"  Field Data ({len(lead.get('field_data', []))} fields):")
            for field in lead.get('field_data', []):
                field_name = field.get('name', 'UNNAMED')
                field_value = field.get('value', '')
                print(f"    {field_name}: '{field_value}'")
    
    print("\n" + "="*60)
    print("=== RAW JSON for first lead ===")
    if data.get('data'):
        print(json.dumps(data['data'][0], indent=2))
else:
    print("Missing credentials - check .env file")
