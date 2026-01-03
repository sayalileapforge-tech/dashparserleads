"""
G/G1/G2 License Class Date Calculation Module
Simple calendar year subtraction from First Insurance Date

LOGIC:
- G = First Insurance Date - 1 year
- G2 = First Insurance Date - 3 years
- G1 = First Insurance Date - 5 years

DATE SOURCES:
- First Insurance Date: From DASH (End of Latest Term of matching driver policy)
- Issue Date, Expiry Date, Birth Date: From MVR

EXPERIENCE VALIDATION:
- Compare birthDate (day+month) with expiryDate (day+month)
- If mismatch: "Customer has less than 5 years of experience"
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, Optional


class G1G2Calculator:
    """Calculate G/G1/G2 dates using simple calendar year subtraction."""
    
    def calculate_from_dates(
        self,
        issue_date: str,
        first_insurance_date: str
    ) -> Dict:
        """
        Calculate G/G1/G2 dates by subtracting years from First Insurance Date.
        
        LOGIC:
        - G = First Insurance Date - 1 year
        - G2 = First Insurance Date - 3 years
        - G1 = First Insurance Date - 5 years
        
        Args:
            issue_date: YYYY-MM-DD format (from MVR)
            first_insurance_date: YYYY-MM-DD format (from DASH End of Latest Term)
            
        Returns:
            {
                'success': bool,
                'g_date': 'YYYY-MM-DD' or None,
                'g2_date': 'YYYY-MM-DD' or None,
                'g1_date': 'YYYY-MM-DD' or None,
                'strategy': str or None,
                'error': str or None,
                'total_days': int (for calculating total_months)
            }
        """
        result = {
            'success': False,
            'g_date': None,
            'g2_date': None,
            'g1_date': None,
            'strategy': 'CALENDAR_YEAR',
            'error': None,
            'total_days': 0
        }
        
        try:
            # Parse dates
            issue_dt = datetime.strptime(issue_date, '%Y-%m-%d')
            first_ins_dt = datetime.strptime(first_insurance_date, '%Y-%m-%d')
            
            # Calculate by subtracting years from first insurance date
            g_date = first_ins_dt - relativedelta(years=1)
            g2_date = first_ins_dt - relativedelta(years=3)
            g1_date = first_ins_dt - relativedelta(years=5)
            
            # No validation needed - firstInsuranceDate (DASH) and IssueDate (MVR) are from different documents
            # and represent different things
            
            result['success'] = True
            result['g_date'] = g_date.strftime('%Y-%m-%d')
            result['g2_date'] = g2_date.strftime('%Y-%m-%d')
            result['g1_date'] = g1_date.strftime('%Y-%m-%d')
            result['total_days'] = (first_ins_dt - issue_dt).days
            
            return result
            
        except Exception as e:
            result['error'] = f"Date calculation failed: {str(e)}"
            return result


def calculate_g_g1_g2(
    issue_date: str,
    first_insurance_date: str,
    birth_date: str = None,
    expiry_date: str = None
) -> Dict:
    """
    Public function to calculate G/G1/G2 dates using calendar year subtraction.
    
    LOGIC:
    1. Check experience validation (birthDate DAY & MONTH vs expiryDate DAY & MONTH)
    2. Calculate G/G1/G2 using simple calendar year subtraction:
       - G = First Insurance Date - 1 year
       - G2 = First Insurance Date - 3 years
       - G1 = First Insurance Date - 5 years
    3. Return both calculation results AND any experience warning
    
    Args:
        issue_date: YYYY-MM-DD (from MVR)
        first_insurance_date: YYYY-MM-DD (from DASH End of Latest Term)
        birth_date: YYYY-MM-DD (optional, from MVR)
        expiry_date: YYYY-MM-DD (optional, from MVR - called licence_expiry_date)
        
    Returns:
        {
            'success': bool,
            'g_date': 'YYYY-MM-DD' or None,
            'g2_date': 'YYYY-MM-DD' or None,
            'g1_date': 'YYYY-MM-DD' or None,
            'strategy': str or None,
            'error': str or None,
            'experience_warning': str or None,
            'total_months': int or None
        }
    """
    result = {
        'success': False,
        'g_date': None,
        'g2_date': None,
        'g1_date': None,
        'strategy': None,
        'error': None,
        'experience_warning': None,
        'total_months': None
    }
    
    # Step 1: Check experience validation
    # Compare birthDate DAY & MONTH with expiryDate DAY & MONTH
    experience_warning = None
    if birth_date and expiry_date:
        try:
            birth_dt = datetime.strptime(birth_date, "%Y-%m-%d")
            expiry_dt = datetime.strptime(expiry_date, "%Y-%m-%d")
            
            # Compare DAY & MONTH (ignore year)
            if (birth_dt.day != expiry_dt.day or 
                birth_dt.month != expiry_dt.month):
                experience_warning = "Customer has less than 5 years of experience"
                # Note: We still continue with calculation, just show this warning
        except:
            pass
    
    # Step 2: Calculate G/G1/G2 using calendar year subtraction
    calculator = G1G2Calculator()
    calc_result = calculator.calculate_from_dates(issue_date, first_insurance_date)
    
    if calc_result['success']:
        result['success'] = True
        result['g_date'] = calc_result['g_date']
        result['g2_date'] = calc_result['g2_date']
        result['g1_date'] = calc_result['g1_date']
        result['strategy'] = calc_result['strategy']
        result['experience_warning'] = experience_warning
        
        # Calculate total_months for reference
        result['total_months'] = int(calc_result.get('total_days', 0) / 30.44)
    else:
        result['error'] = calc_result['error']
        result['experience_warning'] = experience_warning
    
    return result
