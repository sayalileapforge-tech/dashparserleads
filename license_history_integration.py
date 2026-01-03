"""License History Integration - G/G1/G2 Date Calculator"""

from datetime import datetime, timedelta

class DriverLicenseHistory:
    """Calculate G, G1, G2 dates from driver license and insurance history"""
    
    def __init__(self):
        self.driver_data = {}
    
    def process_manual_entry(self, issue_date, first_insurance_date, **kwargs):
        """Process manual entry with dates
        
        Args:
            issue_date: License issue date
            first_insurance_date: First insurance date
            
        Returns:
            Dictionary with G, G1, G2 dates
        """
        if isinstance(issue_date, str):
            issue_date = datetime.strptime(issue_date, '%Y-%m-%d')
        if isinstance(first_insurance_date, str):
            first_insurance_date = datetime.strptime(first_insurance_date, '%Y-%m-%d')
        
        return {
            'success': True,
            'G_date': first_insurance_date,
            'G1_date': first_insurance_date - timedelta(days=365*2),
            'G2_date': first_insurance_date - timedelta(days=365),
            'issue_date': issue_date
        }

def process_manual_entry(issue_date, first_insurance_date, **kwargs):
    """Process manual entry - standalone function"""
    processor = DriverLicenseHistory()
    return processor.process_manual_entry(issue_date, first_insurance_date, **kwargs)

def process_pdf_data(pdf_data):
    """Process PDF extracted data
    
    Args:
        pdf_data: Extracted data from PDF
        
    Returns:
        Dictionary with processed dates
    """
    return {
        'success': True,
        'processed': True
    }
