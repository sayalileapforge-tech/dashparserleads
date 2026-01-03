"""
DASH PDF Parser - Dynamic extraction from DASH insurance reports
Extracts driver information dynamically (no hardcoding)
"""

import re
from PyPDF2 import PdfReader
from datetime import datetime


def extract_text_from_pdf(pdf_path):
    """Extract all text from PDF"""
    try:
        pdf = PdfReader(pdf_path)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""


def parse_dash_report(pdf_path):
    """
    Parse DASH report and extract driver information
    Returns dict with extracted fields or "-" for missing data
    """
    result = {
        'success': False,
        'data': {},
        'errors': []
    }
    
    try:
        text = extract_text_from_pdf(pdf_path)
        if not text:
            result['errors'].append("Could not extract text from PDF")
            return result
        
        # DEBUG: Save extracted text for inspection
        try:
            debug_file = pdf_path.replace('.pdf', '_extracted_text.txt')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            pass
        
        # Initialize data dict with all possible fields
        data = {
            'name': '-',
            'dob': '-',
            'dln': '-',
            'address': '-',
            'gender': '-',
            'marital_status': '-',
            'years_licensed': '-',
            'years_continuous_insurance': '-',
            'years_claims_free': '-',
            'claims_6y': '-',
            'first_party_6y': '-',
            'comprehensive_6y': '-',
            'dcpd_6y': '-',
            'history_nonpay_3y': '-',
            'current_company': '-',
            'current_policy_expiry': '-',
            'current_vehicles_count': '-',
            'current_operators_count': '-',
            'firstInsuranceDate': '-',  # First insurance date ONLY (from DASH: End of Latest Term)
        }
        
        # ===== BASIC INFO =====
        
        # Extract full name (appears after "DRIVER REPORT" or at top)
        name_match = re.search(r'(?:DRIVER REPORT\s+)?([A-Z][A-Z\s]{2,})\s+(?:DLN|Ontario)', text, re.IGNORECASE)
        if not name_match:
            # Try alternative pattern
            name_match = re.search(r'^([A-Z][A-Z\s]+)$', text, re.MULTILINE)
        
        if name_match:
            full_name = name_match.group(1).strip()
            # Clean up - remove unwanted parts
            full_name = re.sub(r'\s+', ' ', full_name)
            # Only take first reasonable length as name
            if len(full_name) < 60:  # Sanity check
                data['name'] = full_name
        
        # Extract DLN (Driver License Number)
        dln_match = re.search(r'DLN[:\s]+([A-Z0-9\-]+)', text, re.IGNORECASE)
        if dln_match:
            data['dln'] = dln_match.group(1).strip()
        
        # Extract Date of Birth
        dob_match = re.search(r'(?:Date of Birth|DOB)[:\s]*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
        if dob_match:
            dob_str = dob_match.group(1).strip()
            # Convert YYYY-MM-DD to MM/DD/YYYY if needed
            if '-' in dob_str:
                parts = dob_str.split('-')
                dob_str = f"{parts[1]}/{parts[2]}/{parts[0]}"
            data['dob'] = dob_str
        
        # Extract Address
        address_match = re.search(r'Address[:\s]+([A-Z0-9\s\-,]+?)(?:\n|Number of)', text, re.IGNORECASE)
        if address_match:
            addr = address_match.group(1).strip()
            # Clean up extra whitespace
            addr = re.sub(r'\s+', ' ', addr)
            if addr and len(addr) > 5:
                data['address'] = addr
        
        # Extract Gender
        gender_match = re.search(r'Gender[:\s]+(M|F|Male|Female)', text, re.IGNORECASE)
        if gender_match:
            gender = gender_match.group(1).strip().upper()
            data['gender'] = gender[0] if gender else '-'  # M or F
        
        # Extract Marital Status
        marital_match = re.search(r'Marital Status[:\s]*([A-Za-z\s\-]+?)(?:\n|Number of|Years|Gender|Driver)', text, re.IGNORECASE)
        if marital_match:
            status = marital_match.group(1).strip()
            # Clean up status - remove extra spaces and check for "not available"
            status = re.sub(r'\s+', ' ', status)
            data['marital_status'] = status if status and status.lower() != 'not available' else '-'
        
        # ===== INSURANCE HISTORY =====
        
        # Extract Years Licensed
        years_lic_match = re.search(r'Years Licensed[:\s]+(\d+)', text, re.IGNORECASE)
        if years_lic_match:
            data['years_licensed'] = years_lic_match.group(1).strip()
        
        # Extract Years of Continuous Insurance
        cont_ins_match = re.search(r'Years of Continuous Insurance[:\s]+(\d+)', text, re.IGNORECASE)
        if cont_ins_match:
            data['years_continuous_insurance'] = cont_ins_match.group(1).strip()
        
        # Extract Years Claims Free
        claims_free_match = re.search(r'Years Claims Free[:\s]+(\d+)', text, re.IGNORECASE)
        if claims_free_match:
            data['years_claims_free'] = claims_free_match.group(1).strip()
        
        # ===== CLAIMS IN LAST 6 YEARS =====
        
        # Number of Claims
        claims_match = re.search(r'Number of Claims in Last 6 Years[:\s]*(\d+)', text, re.IGNORECASE)
        if claims_match:
            data['claims_6y'] = claims_match.group(1).strip()
        
        # At-Fault Claims
        at_fault_match = re.search(r'Number of At-Fault Claims in Last 6 Years[:\s]*(\d+)', text, re.IGNORECASE)
        if at_fault_match:
            data['first_party_6y'] = at_fault_match.group(1).strip()
        
        # Comprehensive Losses
        comp_match = re.search(r'Number of Comprehensive Losses in Last 6 Years[:\s]*(\d+)', text, re.IGNORECASE)
        if comp_match:
            data['comprehensive_6y'] = comp_match.group(1).strip()
        
        # DCPD Claims
        dcpd_match = re.search(r'Number of DCPD Claims in Last 6 Years[:\s]*(\d+)', text, re.IGNORECASE)
        if dcpd_match:
            data['dcpd_6y'] = dcpd_match.group(1).strip()
        
        # ===== CURRENT POLICY =====
        
        # Extract current policy info - look for ACTIVE policy
        # Pattern: Date range, Company, Status (ACTIVE)
        # Handles dates with spaces like "2022-1 1-21"
        active_policy_match = re.search(
            r'#1\s+([0-9\-\s]+)\s+to\s+([0-9\-\s]+)\s+(.+?)\s+(Active)',
            text,
            re.IGNORECASE
        )
        
        if active_policy_match:
            expiry_date_str = active_policy_match.group(2).strip()  # End date
            company = active_policy_match.group(3).strip()
            
            # Normalize date format - remove spaces and convert to MM/DD/YYYY
            expiry_date_normalized = expiry_date_str.replace(' ', '')
            
            if '-' in expiry_date_normalized:
                # YYYY-MM-DD format
                parts = expiry_date_normalized.split('-')
                if len(parts) == 3:
                    data['current_policy_expiry'] = f"{parts[1]}/{parts[2]}/{parts[0]}"
                    data['current_company'] = company
                    print(f"[DASH PARSER] Found Active Policy - Company: {company}, Expiry: {data['current_policy_expiry']}")
            elif '/' in expiry_date_normalized:
                # Already in MM/DD/YYYY format
                data['current_policy_expiry'] = expiry_date_normalized
                data['current_company'] = company
                print(f"[DASH PARSER] Found Active Policy - Company: {company}, Expiry: {data['current_policy_expiry']}")
        
        # Extract vehicles and operators count from Policy #1 section
        # Look for "Number of Reported Operators:" and "Number of Private Passenger Vehicles:"
        vehicles_match = re.search(
            r'(?:Policy #1.*?)?Number of Private.*?Vehicles?\s*:\s*(\d+)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        if vehicles_match:
            data['current_vehicles_count'] = vehicles_match.group(1).strip()
        
        operators_match = re.search(
            r'(?:Policy #1.*?)?Number of Reported Operators?\s*:\s*(\d+)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        if operators_match:
            data['current_operators_count'] = operators_match.group(1).strip()
        
        # ===== EXTRACT FIRST INSURANCE DATE (End of Latest Term from matched operator) =====
        # SPECIFICATION:
        # - First Insurance Date (DASH only) = End of the Latest Term
        # - Issue Date comes ONLY from MVR (not calculated here from DASH)
        
        driver_name = data['name'].lower().strip() if data['name'] != '-' else None
        # Extract the FIRST INSURANCE DATE = "End of Latest Term" from the OLDEST policy
        # Find ALL "End of Latest Term" dates for the driver and use the earliest date
        all_end_dates = []
        
        if driver_name:
            # Split text by policy sections (each policy starts with "Policy #")
            policy_blocks = re.split(r'(?=Policy\s+#)', text, flags=re.IGNORECASE)
            
            for policy_block in policy_blocks:
                if not policy_block.strip():
                    continue
                
                # Extract all operators in this policy block
                operator_matches = re.finditer(
                    r'(?:Operator|Driver)\s*:?\s*([A-Z][A-Z\s\-]{2,}?)(?:\n|;|\(|,)',
                    policy_block,
                    re.IGNORECASE
                )
                
                operators_in_policy = []
                for match in operator_matches:
                    op_name = match.group(1).strip()
                    op_normalized = re.sub(r'\s+', ' ', op_name.lower()).replace(',', '')
                    operators_in_policy.append(op_normalized)
                
                # Normalize driver name
                driver_normalized = re.sub(r'\s+', ' ', driver_name).replace(',', '')
                
                # Check if driver is in this policy
                operator_matched = False
                for op_normalized in operators_in_policy:
                    if op_normalized == driver_normalized:
                        operator_matched = True
                        break
                
                # If matched, extract "End of the Latest Term" from this policy
                if operator_matched:
                    # Pattern handles: YYYY-MM-DD, MM/DD/YYYY, YYYY-M M-DD (with spaces)
                    eolt_match = re.search(
                        r'End of (?:the )?Latest Term\s*:?\s*([0-9\-/ ]+?)(?:\n|$)',
                        policy_block,
                        re.IGNORECASE
                    )
                    
                    if eolt_match:
                        eolt_date = eolt_match.group(1).strip()
                        # Normalize date format to YYYY-MM-DD
                        if '/' in eolt_date:
                            # MM/DD/YYYY format
                            parts = eolt_date.split('/')
                            if len(parts) == 3:
                                eolt_date = f"{parts[2]}-{parts[0]}-{parts[1]}"
                        else:
                            # YYYY-M M-DD or YYYY-MM-DD format (may have spaces)
                            eolt_date = eolt_date.replace(' ', '')  # Remove spaces
                        all_end_dates.append(eolt_date)
            
            # Find the OLDEST (earliest) date - that's the first insurance date
            if all_end_dates:
                all_end_dates.sort()  # Sort ascending - first one is oldest
                data['firstInsuranceDate'] = all_end_dates[0]
                print(f"[DASH PARSER] Found {len(all_end_dates)} policies for {driver_name}")
                print(f"[DASH PARSER] All end dates: {all_end_dates}")
                print(f"[DASH PARSER] Using earliest: {all_end_dates[0]}")
        
        # Fallback: find all "End of the Latest Term" in entire document and use earliest
        if data['firstInsuranceDate'] == '-':
            all_end_matches = re.finditer(
                r'End of (?:the )?Latest Term\s*:?\s*([0-9\-/ ]+?)(?:\n|$)',
                text,
                re.IGNORECASE
            )
            
            end_dates = []
            for match in all_end_matches:
                end_date = match.group(1).strip()
                # Normalize date format to YYYY-MM-DD
                if '/' in end_date:
                    # MM/DD/YYYY format
                    parts = end_date.split('/')
                    if len(parts) == 3:
                        end_date = f"{parts[2]}-{parts[0]}-{parts[1]}"
                else:
                    # YYYY-M M-DD or YYYY-MM-DD format (may have spaces)
                    end_date = end_date.replace(' ', '')  # Remove spaces
                end_dates.append(end_date)
            
            if end_dates:
                end_dates.sort()  # Ascending - oldest first
                data['firstInsuranceDate'] = end_dates[0]
                print(f"[DASH PARSER] Fallback: Found {len(end_dates)} 'End of Latest Term' dates")
                print(f"[DASH PARSER] Using earliest: {end_dates[0]}")
        
        # === HISTORY: NON-PAY (3 YEARS) ===
        # Try to extract non-pay incidents from last 3 years
        # Pattern: "Non-Payment Incidents" or "Non-Pay" with a number
        nonpay_match = re.search(
            r'(?:Non[- ]?Pay(?:ment)?|Incident).*?(?:3[- ]?year|3Y|Last 3).*?(?::|\()\s*(\d+)',
            text,
            re.IGNORECASE
        )
        if nonpay_match:
            data['history_nonpay_3y'] = nonpay_match.group(1).strip()
        
        result['data'] = data
        result['success'] = True
        
    except Exception as e:
        result['errors'].append(f"Parsing error: {str(e)}")
        print(f"Error in parse_dash_report: {e}")
    
    return result


if __name__ == "__main__":
    # Test with provided PDF
    import json
    import sys
    
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else 'DASH Report - MOTILAL DANNILLIAN - 2025-11-19 20-58-55-EST - En.pdf'
    
    result = parse_dash_report(pdf_path)
    print(json.dumps(result, indent=2))
