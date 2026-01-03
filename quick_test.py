#!/usr/bin/env python
"""Quick test of PDF upload and dashboard functionality"""

import requests
import json
import time

BASE_URL = 'http://localhost:3001'

def test_server():
    """Test if server is running"""
    try:
        r = requests.get(f'{BASE_URL}/api/leads', timeout=5)
        print(f'✓ Server responding: {r.status_code}')
        return True
    except Exception as e:
        print(f'✗ Server error: {e}')
        return False

def test_dash_pdf():
    """Test DASH PDF upload"""
    print('\n' + '='*60)
    print('TEST 1: DASH PDF Upload')
    print('='*60)
    
    pdf_file = 'DASH Report - MOTILAL DANNILLIAN - 2025-11-19 20-58-55-EST - En.pdf'
    
    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': f}
            r = requests.post(f'{BASE_URL}/api/upload-mvr', files=files, timeout=15)
        
        data = r.json()
        print(f'✓ Upload Status: {r.status_code}')
        print(f'✓ Success: {data.get("success")}')
        print(f'✓ Document Type: {data.get("document_type")}')
        
        if data.get('data'):
            print('\n✓ EXTRACTED FIELDS:')
            extracted = data['data']
            for key in ['full_name', 'address', 'gender', 'marital_status', 'current_company']:
                val = extracted.get(key, 'N/A')
                print(f'  • {key}: {val}')
        
        print('\n✓ EXPECTED BEHAVIOR:')
        print('  Dashboard should show DASH sections populated')
        print('  - Demographics (Gender, Marital Status, DOB)')
        print('  - Address')
        print('  - History (Claims, Insurance Gaps)')
        print('  - Current Policy')
        print('  - Insurance Details')
        return True
        
    except Exception as e:
        print(f'✗ Error: {e}')
        return False

def test_mvr_pdf():
    """Test MVR PDF upload"""
    print('\n' + '='*60)
    print('TEST 2: MVR PDF Upload')
    print('='*60)
    
    pdf_file = 'MVR_ON_G04027170060201.pdf'
    
    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': f}
            r = requests.post(f'{BASE_URL}/api/upload-mvr', files=files, timeout=15)
        
        data = r.json()
        print(f'✓ Upload Status: {r.status_code}')
        print(f'✓ Success: {data.get("success")}')
        print(f'✓ Document Type: {data.get("document_type")}')
        
        if data.get('data'):
            print('\n✓ EXTRACTED FIELDS:')
            extracted = data['data']
            for key in ['full_name', 'convictions_count', 'years_licensed', 'years_claims_free']:
                val = extracted.get(key, 'N/A')
                print(f'  • {key}: {val}')
        
        print('\n✓ EXPECTED BEHAVIOR (CUMULATIVE):')
        print('  - MVR Info section should UPDATE with convictions/experience')
        print('  - DASH sections should REMAIN VISIBLE (Demographics, Address, History)')
        print('  - Both datasets visible simultaneously on dashboard')
        return True
        
    except Exception as e:
        print(f'✗ Error: {e}')
        return False

if __name__ == '__main__':
    print('\n' + '='*60)
    print('DASHBOARD PDF CUMULATIVE DISPLAY TEST')
    print('='*60)
    
    if not test_server():
        print('\n✗ Server not running. Start it with: python app.py')
        exit(1)
    
    test_dash_pdf()
    time.sleep(1)
    test_mvr_pdf()
    
    print('\n' + '='*60)
    print('TEST COMPLETE')
    print('='*60)
    print('\nNEXT STEPS:')
    print('1. Open browser: http://localhost:3001/pdf-parser')
    print('2. Upload DASH PDF → Check Demographics, Address populate')
    print('3. Upload MVR PDF → Check MVR Info updates, DASH sections remain')
    print('4. Open browser console (F12) → Look for [ROUTE] and [MVR_UI] logs')
    print('='*60)
