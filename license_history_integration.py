"""License History Integration - G/G1/G2 Date Calculator"""

from datetime import datetime, timedelta


class DriverLicenseHistory:
    """Calculate G, G1, G2 dates from driver license and insurance history"""
    
    def __init__(self):
        self.driver_data = {}
    
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
                # Try multiple formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        issue_date = datetime.strptime(issue_date, fmt)
                        break
                    except:
                        continue
            
            if isinstance(first_insurance_date, str):
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        first_insurance_date = datetime.strptime(first_insurance_date, fmt)
                        break
                    except:
                        continue
            
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
            driver_data: Data from DASH report (contains firstInsuranceDate)
            mvr_data: Data from MVR report (contains issue_date, birth_date, licence_expiry_date)
            
        Returns:
            Dictionary with G/G1/G2 dates or experience warning message
        """
        try:
            first_insurance_date_str = driver_data.get('firstInsuranceDate', '')
            issue_date_str = mvr_data.get('issue_date', '')
            birth_date_str = mvr_data.get('birth_date', '')
            expiry_date_str = mvr_data.get('licence_expiry_date', '')
            
            if not first_insurance_date_str or not issue_date_str:
                return {
                    'success': False,
                    'error': 'Missing required dates from PDF'
                }
            
            # Parse dates
            first_insurance_date = None
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    first_insurance_date = datetime.strptime(first_insurance_date_str, fmt)
                    break
                except:
                    continue
            
            issue_date = None
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    issue_date = datetime.strptime(issue_date_str, fmt)
                    break
                except:
                    continue
            
            if not first_insurance_date or not issue_date:
                return {
                    'success': False,
                    'error': 'Could not parse dates'
                }
            
            # Check experience: If birth_date month/day != expiry_date month/day, customer has < 5 years experience
            if birth_date_str and expiry_date_str:
                try:
                    birth_date = None
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                        try:
                            birth_date = datetime.strptime(birth_date_str, fmt)
                            break
                        except:
                            continue
                    
                    expiry_date = None
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                        try:
                            expiry_date = datetime.strptime(expiry_date_str, fmt)
                            break
                        except:
                            continue
                    
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
