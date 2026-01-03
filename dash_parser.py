"""DASH PDF Parser - Extracts insurance data from DASH reports"""

import re
from PyPDF2 import PdfReader

def parse_dash_report(file_path):
    """Parse DASH insurance report PDF
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Dictionary with parsed DASH data or error status
    """
    try:
        # Read PDF
        with open(file_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        if not text:
            return {
                'success': False,
                'document_type': 'DASH',
                'data': {},
                'errors': ['Could not extract text from PDF']
            }
        
        # Parse data from text
        data = extract_dash_data(text)
        
        return {
            'success': True,
            'document_type': 'DASH',
            'data': data,
            'errors': []
        }
        
    except Exception as e:
        return {
            'success': False,
            'document_type': 'DASH',
            'data': {},
            'errors': [str(e)]
        }


def extract_dash_data(text):
    """Extract structured data from DASH PDF text"""
    data = {}
    
    # Helper function to search for patterns
    def find_value(patterns, default='Not available in document'):
        """Search for value using multiple regex patterns"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip() if match.lastindex else match.group(0).strip()
                if value and value.lower() != 'not available':
                    return value
        return default
    
    # Extract driver name - appears at top of report after "DRIVER REPORT"
    name_match = re.search(r'DRIVER REPORT\s+([A-Z\s,]+?)\s+(?:DLN|Licence)', text, re.MULTILINE | re.IGNORECASE)
    if name_match:
        data['name'] = name_match.group(1).strip()
    else:
        # Try alternative pattern
        name_match = re.search(r'(?:Name|DRIVER):\s+([A-Z\s,]+?)(?:\n|DLN|Licence)', text, re.MULTILINE | re.IGNORECASE)
        if name_match:
            data['name'] = name_match.group(1).strip()
        else:
            data['name'] = 'Not available in document'
    
    # Extract DLN (Driver License Number)
    data['dln'] = find_value([
        r'DLN:\s+([A-Z0-9\-]+)\s+Ontario'
    ])
    
    # Extract Date of Birth
    data['dob'] = find_value([
        r'Date of Birth:\s+(\d{4}-\d{2}-\d{2})'
    ])
    
    # Extract Gender
    data['gender'] = find_value([
        r'Gender:\s+(Male|Female)'
    ])
    
    # Extract Address - from "Address:" line
    # Format: "Address: 201-1480 Eglinton Ave W ,Toronto,ON M6E2G5 Number of Claims..."
    # The address ends before "Number of" or at end of line
    address_match = re.search(
        r'Address:\s+([^\n]+?)(?:\s+Number of|\n)',
        text,
        re.MULTILINE
    )
    if address_match:
        address_text = address_match.group(1).strip()
        # Remove trailing "Number of Claims..." if it's there
        address_text = re.sub(r'\s+Number of.*$', '', address_text, flags=re.IGNORECASE).strip()
        data['address'] = address_text
    else:
        data['address'] = 'Not available in document'
    
    # Extract Marital Status
    data['marital_status'] = find_value([
        r'Marital Status:\s+(\w+)'
    ])
    
    # Extract Years Licensed
    data['years_licensed'] = find_value([
        r'Years Licensed:\s+(\d+)'
    ])
    
    # Extract Years of Continuous Insurance
    data['years_continuous_insurance'] = find_value([
        r'Years of Continuous Insurance:\s+(\d+)'
    ])
    
    # Extract Years Claims Free
    data['years_claims_free'] = find_value([
        r'Years Claims Free:\s+(\d+)'
    ])
    
    # Extract claims counts from the summary section at top
    data['claims_6y'] = find_value([
        r'Number of Claims in Last 6 Years:\s+(\d+)'
    ])
    
    data['first_party_6y'] = find_value([
        r'Number of At-Fault Claims in Last 6 Years:\s+(\d+)'
    ])
    
    data['comprehensive_6y'] = find_value([
        r'Number of Comprehensive Losses in Last 6 Years:\s+(\d+)'
    ])
    
    data['dcpd_6y'] = find_value([
        r'Number of DCPD Claims in Last 6 Years:\s+(\d+)'
    ])
    
    # Extract current policy info - from "Policy #1" line at top
    # Format: "#1 2022-1 1-21 to 2025-1 1-21 Certas Home..." or "#1 2025-08-08 to 2026-08-08 Definity..."
    policy_match = re.search(
        r'#1\s+(\d{4}[-/]\d{1,2}\s*[-/]?\d{1,2}[-/]?\d{2,4})\s+to\s+(\d{4}[-/]\d{1,2}\s*[-/]?\d{1,2}[-/]?\d{2,4})\s+(.+?)\s+(?:Active|Cancelled)',
        text,
        re.MULTILINE | re.IGNORECASE
    )
    if policy_match:
        # Company name
        company_text = policy_match.group(3).strip()
        # Clean up company name - remove extra spaces
        data['current_company'] = re.sub(r'\s+', ' ', company_text)
        # Expiry date - clean up spaces in date
        data['current_policy_expiry'] = policy_match.group(2).replace(' ', '')
    else:
        data['current_company'] = 'Not available in document'
        data['current_policy_expiry'] = 'Not available in document'
    
    # Extract vehicle count - from policy section
    vehicles_match = re.search(
        r'Vehicles\s*:\s*(\d+)',
        text
    )
    if vehicles_match:
        data['current_vehicles_count'] = vehicles_match.group(1)
    else:
        # Try alternative pattern
        vehicles_match = re.search(
            r'Number of Private Passe?n?ger Vehicles\s*:\s+(\d+)',
            text
        )
        if vehicles_match:
            data['current_vehicles_count'] = vehicles_match.group(1)
        else:
            data['current_vehicles_count'] = 'Not available in document'
    
    # Extract operators count - from policy section
    operators_match = re.search(
        r'Number of Reported Operators\s*:\s*(\d+)',
        text
    )
    if operators_match:
        data['current_operators_count'] = operators_match.group(1)
    else:
        data['current_operators_count'] = 'Not available in document'
    
    # Extract first insurance date (for G/G1/G2 calculation)
    # Should be the END OF LATEST TERM from the LAST (most recent) policy for the main driver (Relationship: Self)
    
    first_insurance_date = None
    
    # Find all policy sections
    policy_pattern = r'Policy\s*#\d+.*?(?=Policy\s*#\d+|$)'
    policies = list(re.finditer(policy_pattern, text, re.DOTALL | re.IGNORECASE))
    
    last_policy_end_term = None
    
    # Process policies in order - the last one found is the final policy
    for policy_match in policies:
        policy_text = policy_match.group(0)
        
        # Check if this policy has main driver (Relationship to Policyholder: Self)
        if re.search(r'Relationship to Policyholder:\s*Self', policy_text, re.IGNORECASE):
            # Extract End of Latest Term for this policy
            # Handle both date formats: YYYY-MM DD-DD (with space) or YYYY-MM-DD (with dash)
            end_term_match = re.search(
                r'End of (?:the )?Latest Term:\s+(\d{4}[-/]\d{1,2}\s*[-/]?\d{1,2}[-/]?\d{2,4})',
                policy_text
            )
            
            if end_term_match:
                end_term_date = end_term_match.group(1).replace(' ', '')
                # Always take the latest one found (overwrite each time)
                last_policy_end_term = end_term_date
    
    if last_policy_end_term:
        data['firstInsuranceDate'] = last_policy_end_term
    else:
        data['firstInsuranceDate'] = 'Not available in document'
    
    return data
