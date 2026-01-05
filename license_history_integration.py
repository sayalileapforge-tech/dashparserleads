"""License History Integration - G/G1/G2 Date Calculator"""

import re
from datetime import datetime, timedelta


class DriverLicenseHistory:
    """Calculate G, G1, G2 dates from driver license and insurance history"""
    
    def __init__(self):
        self.driver_data = {}

    def _parse_date(self, date_str):
        """Helper to parse dates in various formats"""
        if not date_str or not isinstance(date_str, str) or 'not available' in date_str.lower():
            return None
            
        # Clean up the string
        date_str = date_str.strip()
        
        # Try common formats
        formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', 
            '%Y/%m/%d', '%d-%m-%Y', '%m-%d-%Y',
            '%Y%m%d'
        ]
        
        # Handle DASH artifact: YYYY-MMDD (e.g., 2022-1121)
        if re.match(r'^\d{4}-\d{4}$', date_str):
            try:
                year = int(date_str[:4])
                month = int(date_str[5:7])
                day = int(date_str[7:9])
                return datetime(year, month, day)
            except:
                pass

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        # Last resort: try to extract digits and guess
        digits = re.sub(r'\D', '', date_str)
        if len(digits) == 8:
            # Try YYYYMMDD
            try:
                return datetime.strptime(digits, '%Y%m%d')
            except:
                pass
            # Try MMDDYYYY
            try:
                return datetime.strptime(digits, '%m%d%Y')
            except:
                pass
            # Try DDMMYYYY
            try:
                return datetime.strptime(digits, '%d%m%Y')
            except:
                pass
                
        return None
    
    def process_manual_entry(self, issue_date, first_insurance_date, **kwargs):
        """Process manual entry with dates
        
        Args:
            issue_date: License issue date (string or datetime)
            first_insurance_date: First insurance date (string or datetime)
            
        Returns:
            Dictionary with G, G1, G2 dates
        """
        try:
            # Parse dates if strings
            if isinstance(issue_date, str):
                issue_date = self._parse_date(issue_date)
            
            if isinstance(first_insurance_date, str):
                first_insurance_date = self._parse_date(first_insurance_date)
            
            if not issue_date or not first_insurance_date:
                return {
                    'success': False,
                    'error': 'Invalid date format in manual entry'
                }
            
            # Calculate G/G1/G2 dates using correct formulas:
            # G = First Insurance Date - 1 year
            # G2 = First Insurance Date - 3 years
            # G1 = First Insurance Date - 5 years
            
            g_date = first_insurance_date.replace(year=first_insurance_date.year - 1)
            g2_date = first_insurance_date.replace(year=first_insurance_date.year - 3)
            g1_date = first_insurance_date.replace(year=first_insurance_date.year - 5)
            
            return {
                'success': True,
                'g_date': g_date.strftime('%m/%d/%Y'),
                'g1_date': g1_date.strftime('%m/%d/%Y'),
                'g2_date': g2_date.strftime('%m/%d/%Y'),
                'issue_date': issue_date.strftime('%m/%d/%Y'),
                'first_insurance_date': first_insurance_date.strftime('%m/%d/%Y'),
                'calculation_performed': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_pdf_data(self, driver_data, mvr_data):
        """Process data from PDF extraction
        
        Args:
            driver_data: Data from DASH report (contains firstInsuranceDate or startOfEarliestTerm)
            mvr_data: Data from MVR report (contains issue_date, birth_date, licence_expiry_date)
            
        Returns:
            Dictionary with G/G1/G2 dates or experience warning message
        """
        try:
            first_insurance_date_str = driver_data.get('firstInsuranceDate', '')
            # Fallback to startOfEarliestTerm if firstInsuranceDate is missing
            if not first_insurance_date_str or first_insurance_date_str == 'Not available in document':
                first_insurance_date_str = driver_data.get('startOfEarliestTerm', '')
                
            issue_date_str = mvr_data.get('issue_date', '')
            birth_date_str = mvr_data.get('birth_date', '')
            expiry_date_str = mvr_data.get('licence_expiry_date', '')
            
            if not first_insurance_date_str or not issue_date_str or first_insurance_date_str == 'Not available in document' or issue_date_str == 'Not available in document':
                return {
                    'success': False,
                    'error': f"Missing required dates from PDF (First Insurance: {first_insurance_date_str}, Issue Date: {issue_date_str})"
                }
            
            # Parse dates using robust helper
            first_insurance_date = self._parse_date(first_insurance_date_str)
            issue_date = self._parse_date(issue_date_str)
            
            if not first_insurance_date or not issue_date:
                # Provide more detailed error if possible
                error_msg = 'Could not parse dates'
                if not first_insurance_date and not issue_date:
                    error_msg = f"Could not parse both First Insurance Date ({first_insurance_date_str}) and Issue Date ({issue_date_str})"
                elif not first_insurance_date:
                    error_msg = f"Could not parse First Insurance Date: {first_insurance_date_str}"
                else:
                    error_msg = f"Could not parse Issue Date: {issue_date_str}"
                    
                return {
                    'success': False,
                    'error': error_msg
                }
            
            # Check experience: If birth_date month/day != expiry_date month/day, customer has < 5 years experience
            if birth_date_str and expiry_date_str:
                try:
                    birth_date = self._parse_date(birth_date_str)
                    expiry_date = self._parse_date(expiry_date_str)
                    
                    # Check if birth month/day matches expiry month/day
                    if birth_date and expiry_date:
                        if (birth_date.month != expiry_date.month or 
                            birth_date.day != expiry_date.day):
                            # Customer has less than 5 years of experience
                            return {
                                'success': False,
                                'error': 'Customer has less than 5 years of driving experience',
                                'calculation_performed': False
                            }
                except:
                    pass
            
            # Calculate dates using correct formulas:
            # G = First Insurance Date - 1 year
            # G2 = First Insurance Date - 3 years
            # G1 = First Insurance Date - 5 years
            
            g_date = first_insurance_date.replace(year=first_insurance_date.year - 1)
            g2_date = first_insurance_date.replace(year=first_insurance_date.year - 3)
            g1_date = first_insurance_date.replace(year=first_insurance_date.year - 5)
            
            return {
                'success': True,
                'g_date': g_date.strftime('%m/%d/%Y'),
                'g2_date': g2_date.strftime('%m/%d/%Y'),
                'g1_date': g1_date.strftime('%m/%d/%Y'),
                'issue_date': issue_date.strftime('%m/%d/%Y'),
                'first_insurance_date': first_insurance_date.strftime('%m/%d/%Y'),
                'calculation_performed': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'calculation_performed': False
            }
    
    def process_pdf_extraction(self, pdf_data):
        """Process full PDF extraction data (both DASH and MVR)
        
        Args:
            pdf_data: Dictionary with 'driver' and 'mvr_data' keys
            
        Returns:
            Dictionary with G/G1/G2 dates
        """
        try:
            driver_data = pdf_data.get('driver', {})
            mvr_data = pdf_data.get('mvr_data', {})
            
            return self.process_pdf_data(driver_data, mvr_data)
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def process_manual_entry(issue_date, first_insurance_date, **kwargs):
    """Process manual entry - standalone function"""
    processor = DriverLicenseHistory()
    return processor.process_manual_entry(issue_date, first_insurance_date, **kwargs)


def process_pdf_data(driver_data, mvr_data):
    """Process PDF extracted data - standalone function"""
    processor = DriverLicenseHistory()
    return processor.process_pdf_data(driver_data, mvr_data)
