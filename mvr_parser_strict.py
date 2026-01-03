"""
STRICT MVR (Motor Vehicle Record) Parser - v1
Extracts ONLY explicit data from MVR documents
No inference, no guessing, no DASH data reuse
"""

from PyPDF2 import PdfReader
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field as dataclass_field
from datetime import datetime


@dataclass
class ConvictionInfo:
    date: str = "Not available in document"
    description: str = "Not available in document"
    code: str = "Not available in document"
    points: str = "Not available in document"


@dataclass
class MVRData:
    document_type: str = "MVR"
    total_pages: int = 0
    
    # MVR INFO FIELDS (ONLY these should be populated)
    full_name: str = "Not available in document"
    birth_date: str = "Not available in document"
    licence_number: str = "Not available in document"
    licence_expiry_date: str = "Not available in document"
    issue_date: str = "Not available in document"  # For G/G1/G2 calculation
    first_insurance_date: str = "Not available in document"  # For G/G1/G2 calculation
    
    # Demographics & Address
    address: str = "Not available in document"
    gender: str = "Not available in document"
    marital_status: str = "Not available in document"
    years_licensed: str = "Not available in document"
    years_claims_free: str = "Not available in document"
    
    # History (Insurance Claims)
    nonpay_3y: str = "Not available in document"
    claims_6y: str = "Not available in document"
    first_party_6y: str = "Not available in document"
    gaps_6y: str = "Not available in document"
    years_continuous_insurance: str = "Not available in document"
    
    # Current Policy
    current_company: str = "Not available in document"
    current_policy_expiry: str = "Not available in document"
    current_vehicles_count: str = "Not available in document"
    current_operators_count: str = "Not available in document"
    
    # Convictions
    convictions_count: str = "Not available in document"
    convictions: List[ConvictionInfo] = dataclass_field(default_factory=list)
    
    # G/G1/G2 License Class Dates (calculated if both dates present)
    g_date: str = "Not available in document"
    g2_date: str = "Not available in document"
    g1_date: str = "Not available in document"
    
    # Metadata
    verification: Dict = dataclass_field(default_factory=dict)


class StrictMVRParserV1:
    """
    Strict MVR parser that extracts ONLY explicit data from the document.
    
    RULES:
    - Extract only data explicitly mentioned in MVR
    - Never infer or guess
    - Never use DASH data
    - Show "—" for missing values
    """
    
    def __init__(self):
        self.data = MVRData()
        self.verification = {
            'birth_date_found': False,
            'licence_expiry_found': False,
            'convictions_found': False,
            'document_recognized': False,
        }
    
    def parse_pdf(self, pdf_path: str) -> dict:
        """Parse PDF (either MVR or DASH) and extract data"""
        try:
            reader = PdfReader(pdf_path)
            self.data.total_pages = len(reader.pages)
            
            # Extract text and check document type
            full_text = self._extract_all_text(reader)
            
            # CHECK DASH FIRST (more specific) before MVR
            # Otherwise DASH PDFs might match MVR patterns
            if self._is_dash_document(full_text):
                self.data.document_type = "DASH"
                self.verification['document_recognized'] = True
                
                # Extract DASH-specific fields (insurance/policy info)
                self._extract_driver_info(full_text)
                self._extract_demographics(full_text)
                self._extract_address(full_text)
                self._extract_current_policy(full_text)
                
                return self._format_output(success=True)
            
            # Check if MVR document
            elif self._is_mvr_document(full_text):
                self.data.document_type = "MVR"
                self.verification['document_recognized'] = True
                
                # Extract MVR-specific fields
                self._extract_driver_info(full_text)
                self._extract_licence_info(full_text)
                self._extract_demographics(full_text)
                self._extract_address(full_text)
                self._extract_history(full_text)
                self._extract_current_policy(full_text)
                self._extract_convictions(full_text)
                
                # Calculate G/G1/G2 dates if both issue and expiry dates present
                self._calculate_g_dates()
                
                return self._format_output(success=True)
            
            else:
                return self._format_output(
                    success=False,
                    message="Document is neither an MVR nor DASH report"
                )
            
        except Exception as e:
            return self._format_output(
                success=False,
                message=f"Error parsing PDF: {str(e)}"
            )
    
    def _extract_all_text(self, reader: PdfReader) -> str:
        """Extract text from all pages"""
        full_text = ""
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text:
                    full_text += f"\n--- PAGE {page_num + 1} ---\n{text}"
            except:
                pass
        return full_text
    
    def _is_mvr_document(self, text: str) -> bool:
        """Check if document is an MVR report"""
        mvr_indicators = [
            r'motor\s*vehicle\s*record',
            r'\bMVR\b',
            r'driving\s*record',
            r'licence\s*history',
            r'motor\s*vehicle\s*history',
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) 
                  for pattern in mvr_indicators)
    
    def _is_dash_document(self, text: str) -> bool:
        """Check if document is a DASH report (insurance/policy document)"""
        dash_indicators = [
            r'DASH\s+Report',
            r'DRIVER REPORT',
            r'Insurance\s+Certificate',
            r'Policy\s+Certificate',
            r'Insurance\s+Summary',
            r'Certificate\s+of\s+Insurance',
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) 
                  for pattern in dash_indicators)
    
    def _extract_driver_info(self, text: str):
        """Extract driver name and birth date from MVR"""
        
        # Extract Name (usually at the top)
        name_patterns = [
            # MVR format: "Name: GARNICA,IVAN,TRABANCA Birth Date: ..."
            r'Name:\s*([A-Z][A-Z\-\',\.\s,]+?)(?:\s+Birth Date)',
            # DASH format: "Name: MOTILAL  DANNILLIAN" or name followed by newline
            r'Name:\s*([A-Z][A-Za-z\s\-\',\.]+?)(?:\n|Birth Date|Gender)',
            r'Name:\s*([A-Z][A-Za-z\s\-\',\.]+?)(?:\n|$)',
            r'Driver Name:\s*([A-Z][A-Za-z\s\-\',\.]+?)(?:\n|$)',
            r'Name\s+([A-Z][A-Za-z\s\-\',\.]+?)\s+Birth Date',
            # DASH format: Name appears on its own line after "DRIVER REPORT"
            r'(?:DRIVER REPORT|DASH\s+REPORT)\s*\n\s*([A-Z][A-Za-z\s\-\',\.]+?)\n',
            # Or just capture line with names (two capitals)
            r'^([A-Z][A-Za-z]+\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)\s*$',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up name - remove "Date" if it got included
                name = re.sub(r'\s*(?:Date of Birth|Birth Date|Gender|Height).*$', '', name).strip()
                # Remove any trailing punctuation
                name = name.rstrip(',:')
                # Convert commas in MVR names (GARNICA,IVAN,TRABANCA) to spaces
                name = name.replace(',', ' ')
                # Remove extra spaces (DASH has double spaces)
                name = re.sub(r'\s+', ' ', name)
                if name and name != "Not available in document" and len(name) > 2 and not re.match(r'^(DRIVER|REPORT|DASH|Report)', name):
                    self.data.full_name = name
                    break
        
        # Extract Birth Date - improved patterns that match actual format
        date_patterns = [
            r'Birth Date:\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'Date of Birth:\s*(\d{4}-\d{2}-\d{2})',
            r'Date of Birth:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'DOB:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'\bD\.O\.B\.?:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'(?:Born|B\.)\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dob = match.group(1).strip()
                if dob:
                    self.data.birth_date = self._normalize_date(dob)
                    self.verification['birth_date_found'] = True
                    break
    
    def _extract_licence_info(self, text: str):
        """Extract licence number and expiry date"""
        
        # Extract Licence Number
        licence_patterns = [
            r'Licence Number[\s:]*([A-Z0-9\-\s]+?)(?:\n|Expiry|Gender|Height)',
            r'Licence Number:\s*([G0-9\-\s]+?)(?:\n|$)',
            r'License Number[\s:]*([A-Z0-9\-\s]+?)(?:\n|$)',
            r'DL[\s:]?#?[\s]*([A-Z0-9\-\s]+?)(?:\n|$)',
            r'(?:Ontario|ON)\s+(?:Licence|License)[\s:]*([A-Z0-9\-\s]+?)(?:\n|$)',
            # DASH format: "DLN: M6771-15409-66215 Ontario"
            r'DLN:\s*([A-Z0-9\-\s]+?)(?:\s+Ontario|$)',
        ]
        
        for pattern in licence_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                licence = match.group(1).strip()
                if licence and licence != "Not available in document":
                    self.data.licence_number = licence
                    break
        
        # Extract Licence Expiry Date - match actual format "Expiry Date: 05/02/2027"
        expiry_patterns = [
            r'Expiry Date:\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'Licence Expiry:\s*(\d{4}-\d{2}-\d{2})',
            r'Licence Expiry:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'Expiry:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'Expires?:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'License Expiry:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'Valid Until:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'Renewal Date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        ]
        
        for pattern in expiry_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                expiry = match.group(1).strip()
                if expiry:
                    self.data.licence_expiry_date = self._normalize_date(expiry)
                    self.verification['licence_expiry_found'] = True
                    break
        
        # Extract Issue Date - needed for G/G1/G2 calculation
        issue_patterns = [
            r'Issue Date:\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'Issued:\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'Licence Issued:\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'Issue Date[\s:]*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        ]
        
        for pattern in issue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                issue = match.group(1).strip()
                if issue:
                    self.data.issue_date = self._normalize_date(issue)
                    break
        
        # Extract First Insurance Date - needed for G/G1/G2 calculation
        # Look for earliest insurance policy date or explicit "First Insurance Date"
        first_ins_patterns = [
            r'First Insurance Date[\s:]*(\d{4}-\d{2}-\d{2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'First Insured[\s:]*(\d{4}-\d{2}-\d{2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'Since[\s:]*(\d{4}-\d{2}-\d{2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        ]
        
        for pattern in first_ins_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                first_ins = match.group(1).strip()
                if first_ins:
                    self.data.first_insurance_date = self._normalize_date(first_ins)
                    break
    
    def _calculate_g_dates(self):
        """
        MVR Parser does NOT calculate G/G1/G2 dates.
        
        IMPORTANT: G/G1/G2 dates require firstInsuranceDate from DASH report.
        The combination endpoint will calculate G/G1/G2 using both DASH and MVR data.
        
        MVR parser only extracts: issue_date, licence_expiry_date, birth_date
        """
        # G/G1/G2 calculation is handled by combination endpoint
        # which has access to both DASH (firstInsuranceDate) and MVR data
        pass
    
    def _extract_convictions(self, text: str):
        """Extract convictions count and details"""
        
        # Look for convictions count - match "***Number of Convictions: 0 ***" pattern
        count_patterns = [
            r'\*+\s*Number of Convictions:\s*(\d+)',
            r'Total Convictions[\s:]*(\d+)',
            r'Number of Convictions[\s:]*(\d+)',
            r'Convictions[\s:]*(\d+)',
            r'(?:Current\s+)?Convictions on Record[\s:]*(\d+)',
        ]
        
        conviction_count = None
        for pattern in count_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                conviction_count = match.group(1).strip()
                self.data.convictions_count = conviction_count
                self.verification['convictions_found'] = True
                break
        
        # If no count found but document might have convictions section
        if not conviction_count:
            # Look for convictions section headers
            if re.search(r'(?:Convictions?|Violations?|Infractions?)\s*(?:Section|Record|History)', 
                        text, re.IGNORECASE):
                self.verification['convictions_found'] = True
        
        # Extract individual conviction details
        self._parse_conviction_records(text)
    
    def _parse_conviction_records(self, text: str):
        """Parse individual conviction records from MVR"""
        
        # Look for all lines with dates in YYYY-MM-DD or DD/MM/YYYY format
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line contains a date
            date_match = re.match(r'(\d{4}-\d{2}-\d{2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})', line)
            
            if date_match:
                # This line starts with a date, might be a conviction record
                date_str = date_match.group(1)
                
                # Get description from same line or next line
                description = line[date_match.end():].strip()
                
                # If description is on the same line
                if description and not description.lower() in ['', 'none', 'no convictions']:
                    conviction = ConvictionInfo()
                    conviction.date = self._normalize_date(date_str)
                    conviction.description = description
                    self.data.convictions.append(conviction)
                # Check if description is on the next line
                elif i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not re.match(r'\d{4}-\d{2}-\d{2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}', next_line):
                        conviction = ConvictionInfo()
                        conviction.date = self._normalize_date(date_str)
                        conviction.description = next_line
                        self.data.convictions.append(conviction)
                        i += 1  # Skip next line since we processed it
            
            i += 1
    
    def _parse_conviction_line(self, line: str) -> ConvictionInfo:
        """Parse a single conviction line"""
        conviction = ConvictionInfo()
        
        # Extract date
        date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})', line)
        if date_match:
            conviction.date = self._normalize_date(date_match.group(1))
        
        # Extract description (rest of the line)
        # Remove date from line to get description
        desc = re.sub(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}[\s\-]*', '', line).strip()
        if desc:
            conviction.description = desc
        
        return conviction
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to YYYY-MM-DD format
        
        Canadian MVR documents typically use DD/MM/YYYY format.
        """
        if not date_str or date_str == "Not available in document":
            return "Not available in document"
        
        # Remove extra spaces
        date_str = date_str.strip()
        
        # Try common formats - prioritize DD/MM/YYYY for Canadian documents
        # Then try MM/DD/YYYY, etc.
        formats = [
            ('%d/%m/%Y', 'DD/MM/YYYY'),  # Canadian format - TRY FIRST
            ('%d-%m-%Y', 'DD-MM-YYYY'),  # Canadian format variant
            ('%m/%d/%Y', 'MM/DD/YYYY'),  # US format
            ('%m-%d-%Y', 'MM-DD-YYYY'),  # US format variant
            ('%Y-%m-%d', 'YYYY-MM-DD'),
            ('%m/%d/%y', 'MM/DD/YY'),
            ('%d/%m/%y', 'DD/MM/YY'),
        ]
        
        for fmt, _ in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If parsing fails, return as-is if it looks like a date
        if re.match(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}', date_str):
            return date_str
        
        return "Not available in document"
    
    def _extract_demographics(self, text: str):
        """Extract demographics information"""
        # Gender
        gender_match = re.search(r'Gender:\s*(\w+)', text)
        if gender_match:
            self.data.gender = gender_match.group(1).strip()
        
        # Marital Status - use boundary "Number of" to avoid capturing following content
        marital_match = re.search(r'Marital Status:\s*([A-Za-z\s]+?)(?:\s+Number of|$)', text)
        if marital_match:
            self.data.marital_status = marital_match.group(1).strip()
        
        # Years Licensed
        years_lic_match = re.search(r'Years Licensed:\s*(\d+)', text)
        if years_lic_match:
            self.data.years_licensed = years_lic_match.group(1).strip()
        
        # Years Claims Free
        years_free_match = re.search(r'Years Claims Free:\s*(\d+)', text)
        if years_free_match:
            self.data.years_claims_free = years_free_match.group(1).strip()
    
    def _extract_address(self, text: str):
        """Extract address information"""
        # Address pattern: "Address: 61 GRAPEVINE CIRCLE SCARBOROUGH ON M1X1X6"
        address_match = re.search(r'Address:\s*([A-Z0-9\s\-,]+?)(?:\s+(?:Number of|Gender|Marital|Years)|\n|$)', text)
        if address_match:
            addr = address_match.group(1).strip()
            # Clean up - remove extra spaces and trailing commas
            addr = re.sub(r'\s+', ' ', addr).rstrip(',')
            if addr and len(addr) > 3:
                self.data.address = addr
    
    def _extract_history(self, text: str):
        """Extract insurance history and claim information"""
        # Number of Non-Pay Claims in Last 3 Years
        nonpay_match = re.search(r'Number of Non-?Pay(?:ments?)? in Last 3 Years?:\s*(\d+)', text, re.IGNORECASE)
        if nonpay_match:
            self.data.nonpay_3y = nonpay_match.group(1).strip()
        
        # Number of Claims in Last 6 Years
        claims_match = re.search(r'Number of Claims in Last [36] Years?:\s*(\d+)', text)
        if claims_match:
            self.data.claims_6y = claims_match.group(1).strip()
        
        # Number of At-Fault Claims (1st Party) in Last 6 Years
        first_party_match = re.search(r'Number of At-Fault Claims in Last 6 Years?:\s*(\d+)', text)
        if first_party_match:
            self.data.first_party_6y = first_party_match.group(1).strip()
        
        # Number of Comprehensive Losses (Gaps)
        gaps_match = re.search(r'Number of Comprehensive Losses in Last 6 Years?:\s*(\d+)', text)
        if gaps_match:
            self.data.gaps_6y = gaps_match.group(1).strip()
        
        # Years of Continuous Insurance
        continuous_match = re.search(r'Years of Continuous Insurance:\s*(\d+)', text)
        if continuous_match:
            self.data.years_continuous_insurance = continuous_match.group(1).strip()
    
    def _extract_current_policy(self, text: str):
        """Extract current policy information"""
        # Look for the first active policy
        # Pattern: "Policy #1 2022-12-04 to 2024-12-04 Aviva Insurance Company of Canada Active"
        active_policy_match = re.search(
            r'#\d+\s+[\d\-]+\s+to\s+([\d\-]+)\s+([A-Za-z\s&\.]+?)\s+Active',
            text
        )
        
        if active_policy_match:
            # Extract expiry date
            self.data.current_policy_expiry = active_policy_match.group(1).strip()
            # Extract company name
            company = active_policy_match.group(2).strip()
            company = re.sub(r'\s+', ' ', company).rstrip(' -')
            self.data.current_company = company
        
        # Count vehicles and operators in the policy
        # Look for "Number of Private Passenger Vehicles : X" (handles spaces in text)
        vehicles_match = re.search(r'Number of\s+Private\s+Passe\s*nger\s+Vehicles?\s*:?\s*(\d+)', text)
        if vehicles_match:
            self.data.current_vehicles_count = vehicles_match.group(1).strip()
        
        # Look for "Number of Reported Operators: X"
        operators_match = re.search(r'Number of Reported Operators:\s*(\d+)', text)
        if operators_match:
            self.data.current_operators_count = operators_match.group(1).strip()
    
    def _format_output(self, success: bool, message: str = None) -> dict:
        """Format output for API response"""
        return {
            'success': success,
            'message': message,
            'document_type': self.data.document_type,
            'total_pages': self.data.total_pages,
            'mvr_data': {
                'full_name': self.data.full_name,
                'birth_date': self.data.birth_date,
                'licence_number': self.data.licence_number,
                'licence_expiry_date': self.data.licence_expiry_date,
                'issue_date': self.data.issue_date,
                'address': self.data.address,
                'gender': self.data.gender,
                'marital_status': self.data.marital_status,
                'years_licensed': self.data.years_licensed,
                'years_claims_free': self.data.years_claims_free,
                'nonpay_3y': self.data.nonpay_3y,
                'claims_6y': self.data.claims_6y,
                'first_party_6y': self.data.first_party_6y,
                'gaps_6y': self.data.gaps_6y,
                'years_continuous_insurance': self.data.years_continuous_insurance,
                'current_company': self.data.current_company,
                'current_policy_expiry': self.data.current_policy_expiry,
                'current_vehicles_count': self.data.current_vehicles_count,
                'current_operators_count': self.data.current_operators_count,
                'convictions_count': self.data.convictions_count,
                'convictions': [asdict(c) for c in self.data.convictions],
                'g_dates': {
                    'g_date': self.data.g_date,
                    'g2_date': self.data.g2_date,
                    'g1_date': self.data.g1_date,
                }
            },
            'verification': self.verification,
        }


def parse_mvr_report_strict(pdf_path: str) -> dict:
    """
    Parse MVR report with strict rules.
    
    Returns:
    {
        'success': bool,
        'document_type': 'MVR',
        'total_pages': int,
        'mvr_data': {
            'full_name': str,
            'birth_date': str,
            'licence_number': str,
            'licence_expiry_date': str,
            'convictions_count': str,
            'convictions': [
                {'date': str, 'description': str, 'code': str, 'points': str}
            ]
        },
        'verification': dict
    }
    """
    parser = StrictMVRParserV1()
    return parser.parse_pdf(pdf_path)
