"""
Driver License History Integration Module
Integrates G/G1/G2 calculation for both manual entry and PDF parsing

LOGIC FLOW:
1. Manual Entry: User enters Issue Date + First Insurance Date → Calculate G/G1/G2
2. PDF Parsing: Extract dates from MVR/DASH → If both dates present → Calculate G/G1/G2

RULES:
- Manual and PDF logic use IDENTICAL calculation
- Never infer missing dates
- Only calculate if BOTH Issue Date AND First Insurance Date present
- If only Issue Date or only Expiry Date → Do NOT calculate
"""

from datetime import datetime
from typing import Dict, Optional
from g1g2_calculator import G1G2Calculator, calculate_g_g1_g2


class DriverLicenseHistory:
    """
    Manage driver license history calculations for both manual entry and PDF parsing.
    """
    
    def __init__(self):
        self.calculator = G1G2Calculator()
    
    def process_manual_entry(
        self,
        issue_date: str,  # mm/dd/yyyy
        first_insurance_date: str,  # mm/dd/yyyy
        driver_name: Optional[str] = None,
        birth_date: Optional[str] = None,  # mm/dd/yyyy (for experience validation)
        expiry_date: Optional[str] = None   # mm/dd/yyyy (for experience validation)
    ) -> Dict:
        """
        Process manual form entry for Issue Date and First Insurance Date.
        
        FLOW:
        1. Validate both dates are present
        2. Parse and normalize dates to YYYY-MM-DD
        3. Call calculator
        4. Return structured result
        
        Args:
            issue_date: mm/dd/yyyy format
            first_insurance_date: mm/dd/yyyy format
            driver_name: Optional driver name for logging
            
        Returns:
            {
                'success': bool,
                'driver_name': str or None,
                'issue_date': 'YYYY-MM-DD',
                'first_insurance_date': 'YYYY-MM-DD',
                'g_date': 'YYYY-MM-DD' or None,
                'g2_date': 'YYYY-MM-DD' or None,
                'g1_date': 'YYYY-MM-DD' or None,
                'total_months': int,
                'strategy': str,
                'gaps': {'g': months, 'g2': months, 'g1': months},
                'error': str or None
            }
        """
        result = {
            'success': False,
            'driver_name': driver_name,
            'issue_date': None,
            'first_insurance_date': None,
            'g_date': None,
            'g2_date': None,
            'g1_date': None,
            'total_months': None,
            'strategy': None,
            'calculation_performed': False,  # Flag to indicate if calculation was done
            'gaps': {'g': None, 'g2': None, 'g1': None},
            'error': None
        }
        
        # Validate inputs
        if not issue_date or not first_insurance_date:
            result['error'] = "Both Issue Date and First Insurance Date are required"
            return result
        
        # Normalize dates to YYYY-MM-DD format
        try:
            issue_parsed = datetime.strptime(issue_date, "%m/%d/%Y")
            first_ins_parsed = datetime.strptime(first_insurance_date, "%m/%d/%Y")
            
            issue_iso = issue_parsed.strftime("%Y-%m-%d")
            first_ins_iso = first_ins_parsed.strftime("%Y-%m-%d")
            
            result['issue_date'] = issue_iso
            result['first_insurance_date'] = first_ins_iso
            
            # Also normalize birth_date and expiry_date if provided
            birth_iso = None
            expiry_iso = None
            
            if birth_date:
                try:
                    birth_parsed = datetime.strptime(birth_date, "%m/%d/%Y")
                    birth_iso = birth_parsed.strftime("%Y-%m-%d")
                except:
                    pass
            
            if expiry_date:
                try:
                    expiry_parsed = datetime.strptime(expiry_date, "%m/%d/%Y")
                    expiry_iso = expiry_parsed.strftime("%Y-%m-%d")
                except:
                    pass
            
        except ValueError as e:
            result['error'] = f"Invalid date format: {str(e)}"
            return result
        
        # Calculate G/G1/G2 with birth date for experience validation
        calc_result = calculate_g_g1_g2(issue_iso, first_ins_iso, birth_iso, expiry_iso)
        
        if not calc_result['success']:
            result['error'] = calc_result['error']
            return result
        
        # Extract results
        result['success'] = True
        result['calculation_performed'] = True  # Mark that calculation was performed
        result['g_date'] = calc_result['g_date']
        result['g2_date'] = calc_result['g2_date']
        result['g1_date'] = calc_result['g1_date']
        result['total_months'] = calc_result['total_months']
        result['strategy'] = calc_result['strategy']
        
        # Include experience warning if present
        if calc_result.get('experience_warning'):
            result['experience_warning'] = calc_result['experience_warning']
        
        # Calculate gaps between dates
        if all([issue_iso, result['g1_date'], result['g2_date'], result['g_date'], first_ins_iso]):
            try:
                issue_dt = datetime.strptime(issue_iso, "%Y-%m-%d")
                g1_dt = datetime.strptime(result['g1_date'], "%Y-%m-%d")
                g2_dt = datetime.strptime(result['g2_date'], "%Y-%m-%d")
                g_dt = datetime.strptime(result['g_date'], "%Y-%m-%d")
                first_dt = datetime.strptime(first_ins_iso, "%Y-%m-%d")
                
                result['gaps']['g1'] = self.calculator._months_between(issue_dt, g1_dt)
                result['gaps']['g2'] = self.calculator._months_between(g1_dt, g2_dt)
                result['gaps']['g'] = self.calculator._months_between(g2_dt, g_dt)
            except:
                pass
        
        return result
    
    def process_pdf_extraction(
        self,
        pdf_data: Dict,
        driver_num: int = 1
    ) -> Dict:
        """
        Process extracted data from PDF (MVR or DASH).
        
        RULES:
        - Extract ONLY dates explicitly in PDF
        - Do NOT infer missing dates
        - Only calculate G/G1/G2 if BOTH Issue Date AND First Insurance Date present
        
        Args:
            pdf_data: Dictionary with extracted PDF data
            driver_num: Driver number for logging
            
        Returns:
            {
                'success': bool,
                'dates_found': {
                    'issue_date': bool,
                    'first_insurance_date': bool,
                    'expiry_date': bool
                },
                'issue_date': 'YYYY-MM-DD' or None,
                'first_insurance_date': 'YYYY-MM-DD' or None,
                'expiry_date': 'YYYY-MM-DD' or None,
                'g_date': 'YYYY-MM-DD' or None,
                'g2_date': 'YYYY-MM-DD' or None,
                'g1_date': 'YYYY-MM-DD' or None,
                'total_months': int or None,
                'strategy': str or None,
                'calculation_performed': bool,
                'error': str or None,
                'note': str or None
            }
        """
        result = {
            'success': True,
            'dates_found': {
                'issue_date': False,
                'first_insurance_date': False,
                'expiry_date': False
            },
            'issue_date': None,
            'first_insurance_date': None,
            'expiry_date': None,
            'birth_date': None,
            'g_date': None,
            'g2_date': None,
            'g1_date': None,
            'total_months': None,
            'strategy': None,
            'calculation_performed': False,
            'error': None,
            'note': None
        }
        
        # SPECIFICATION REQUIREMENTS - STRICT DATE SOURCING:
        # issue_date: ONLY from MVR (Licence Issue Date)
        # first_insurance_date: ONLY from DASH (End of Latest Term)
        # expiry_date (licence_expiry_date): ONLY from MVR (Licence Expiry Date)
        # birth_date: ONLY from MVR (for experience validation)
        
        issue_date = None
        first_insurance_date = None
        expiry_date = None
        birth_date = None
        
        # Extract from MVR ONLY for these fields
        if 'mvr_data' in pdf_data and isinstance(pdf_data['mvr_data'], dict):
            mvr = pdf_data['mvr_data']
            # Issue Date: ONLY from MVR
            if mvr.get('issue_date') and mvr.get('issue_date') != '-':
                issue_date = mvr['issue_date']
                result['dates_found']['issue_date'] = True
            # Licence Expiry Date: ONLY from MVR
            if mvr.get('licence_expiry_date') and mvr.get('licence_expiry_date') != '-':
                expiry_date = mvr['licence_expiry_date']
                result['dates_found']['expiry_date'] = True
            # Birth Date: ONLY from MVR (for experience validation)
            if mvr.get('birth_date') and mvr.get('birth_date') != '-':
                birth_date = mvr['birth_date']
        
        # Extract from DASH ONLY for this field
        if 'driver' in pdf_data and isinstance(pdf_data['driver'], dict):
            driver = pdf_data['driver']
            # First Insurance Date: ONLY from DASH (End of Latest Term)
            if driver.get('firstInsuranceDate') and driver.get('firstInsuranceDate') != '-':
                first_insurance_date = driver['firstInsuranceDate']
                result['dates_found']['first_insurance_date'] = True
                print(f"[PDF EXTRACTION] firstInsuranceDate found: {first_insurance_date}")
            else:
                print(f"[PDF EXTRACTION] firstInsuranceDate NOT found or is '-': {driver.get('firstInsuranceDate')}")
        
        # Store found dates
        result['issue_date'] = issue_date
        result['first_insurance_date'] = first_insurance_date
        result['expiry_date'] = expiry_date
        result['birth_date'] = birth_date
        
        print(f"[PDF EXTRACTION] Extracted: issue_date={issue_date}, first_insurance_date={first_insurance_date}")
        
        # Only calculate if BOTH Issue Date AND First Insurance Date are present
        if issue_date and first_insurance_date:
            # Run calculation with birth_date and expiry_date for experience validation
            calc_result = calculate_g_g1_g2(issue_date, first_insurance_date, birth_date, expiry_date)
            
            if calc_result['success']:
                result['success'] = True
                result['g_date'] = calc_result['g_date']
                result['g2_date'] = calc_result['g2_date']
                result['g1_date'] = calc_result['g1_date']
                result['total_months'] = calc_result['total_months']
                result['strategy'] = calc_result['strategy']
                result['calculation_performed'] = True
                result['note'] = "G/G1/G2 dates calculated from MVR Issue Date and DASH First Insurance Date"
                # Include experience warning if present
                if calc_result.get('experience_warning'):
                    result['experience_warning'] = calc_result['experience_warning']
            else:
                result['success'] = False
                result['error'] = calc_result['error']
                result['note'] = "Calculation attempted but failed"
        else:
            # Not enough data to calculate
            if not issue_date:
                result['note'] = "Issue Date not found in MVR document"
            elif not first_insurance_date:
                result['note'] = "First Insurance Date not found in DASH document"
            else:
                result['note'] = "Both Issue Date (from MVR) and First Insurance Date (from DASH) required for calculation"
        
        return result
    
    def format_for_ui(
        self,
        calculation_result: Dict,
        format_style: str = "iso"  # or "display"
    ) -> Dict:
        """
        Format calculation result for UI display.
        
        Args:
            calculation_result: Output from process_manual_entry or process_pdf_extraction
            format_style: "iso" (YYYY-MM-DD) or "display" (MM/DD/YYYY)
            
        Returns:
            UI-ready dictionary with formatted dates
        """
        ui_data = {
            'issue_date': calculation_result.get('issue_date'),
            'first_insurance_date': calculation_result.get('first_insurance_date'),
            'g_date': calculation_result.get('g_date'),
            'g2_date': calculation_result.get('g2_date'),
            'g1_date': calculation_result.get('g1_date'),
            'total_months': calculation_result.get('total_months'),
            'strategy': calculation_result.get('strategy'),
            'calculation_performed': calculation_result.get('calculation_performed', False),
            'error': calculation_result.get('error'),
            'note': calculation_result.get('note')
        }
        
        # Format dates if requested
        if format_style == "display":
            for key in ['issue_date', 'first_insurance_date', 'g_date', 'g2_date', 'g1_date']:
                if ui_data[key]:
                    try:
                        dt = datetime.strptime(ui_data[key], "%Y-%m-%d")
                        ui_data[key] = dt.strftime("%m/%d/%Y")
                    except:
                        pass
        
        return ui_data


# Helper functions for direct use

def process_manual_entry(
    issue_date: str,
    first_insurance_date: str,
    driver_name: Optional[str] = None
) -> Dict:
    """
    Process manual form entry.
    
    Args:
        issue_date: mm/dd/yyyy
        first_insurance_date: mm/dd/yyyy
        driver_name: Optional name for logging
        
    Returns:
        Calculation result with G/G1/G2 dates
    """
    processor = DriverLicenseHistory()
    return processor.process_manual_entry(
        issue_date,
        first_insurance_date,
        driver_name
    )


def process_pdf_data(pdf_data: Dict) -> Dict:
    """
    Process extracted PDF data.
    
    Args:
        pdf_data: Dictionary with parsed PDF content
        
    Returns:
        Calculation result with G/G1/G2 dates (if applicable)
    """
    processor = DriverLicenseHistory()
    return processor.process_pdf_extraction(pdf_data)
