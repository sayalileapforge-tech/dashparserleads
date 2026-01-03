"""MVR (Motor Vehicle Record) PDF Parser - Strict extraction"""

import re
from PyPDF2 import PdfReader


class StrictMVRParserV1:
    """Parses MVR PDFs with strict field extraction"""
    
    def parse_pdf(self, file_path):
        """Parse MVR PDF and extract driver information"""
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
                    'document_type': self.detect_document_type(text),
                    'mvr_data': {},
                    'errors': ['Could not extract text from PDF']
                }
            
            # Detect document type
            doc_type = self.detect_document_type(text)
            
            # Parse data
            data = self.extract_mvr_data(text)
            
            return {
                'success': True,
                'document_type': doc_type,
                'mvr_data': data,
                'errors': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'document_type': None,
                'mvr_data': {},
                'errors': [str(e)]
            }
    
    def detect_document_type(self, text):
        """Detect if document is MVR or DASH"""
        text_lower = text.lower()
        
        # Check for MVR indicators
        if any(keyword in text_lower for keyword in ['motor vehicle', 'mvr', 'driving record', 'violation', 'licence number']):
            return 'MVR'
        
        # Check for DASH indicators
        if any(keyword in text_lower for keyword in ['dash report', 'insurance', 'policy']):
            return 'DASH'
        
        return 'UNKNOWN'
    
    def extract_mvr_data(self, text):
        """Extract MVR fields from PDF text"""
        data = {}
        
        # Helper function
        def find_value(patterns, default='Not available in document'):
            """Search for value using multiple regex patterns"""
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip() if match.lastindex else match.group(0).strip()
                    if value and value.lower() != 'not available':
                        return value
            return default
        
        # Extract driver information - Ontario MVR format
        data['full_name'] = find_value([
            r"^Name:\s+([A-Z,\s]+?)(?:\n|Birth Date)",
            r"^Name:\s+(.+?)(?:\n|$)",
            r"DRIVER\s+NAME[:\s]+([A-Za-z\s]+?)(?:\n|$)",
        ])
        
        # Ontario format: Birth Date: 01/02/2006
        data['birth_date'] = find_value([
            r"Birth Date:\s+(\d{2}/\d{2}/\d{4})",
            r"DATE\s+OF\s+BIRTH[:\s]+(\d{4}-\d{1,2}-\d{1,2})",
            r"DOB[:\s]+(\d{1,2}/\d{1,2}/\d{4})",
        ])
        
        # Ontario format: Licence Number: G0402-71700-60201
        data['licence_number'] = find_value([
            r"Licence Number:\s+([A-Z0-9\-]+)",
            r"LICENSE\s+NUMBER[:\s]+([A-Z0-9\-]+)",
            r"DL\s+NUMBER[:\s]+([A-Z0-9\-]+)",
        ])
        
        # Ontario format: Expiry Date: 05/02/2027
        data['licence_expiry_date'] = find_value([
            r"Expiry Date:\s+(\d{2}/\d{2}/\d{4})",
            r"LICENSE\s+EXPIRY[:\s]+(\d{4}-\d{1,2}-\d{1,2})",
            r"EXPIRES?[:\s]+(\d{2}/\d{2}/\d{4})",
        ])
        
        # Ontario format: Address: "some address"
        data['address'] = find_value([
            r"Address:\s+\"([^\"]+)\"",
            r"ADDRESS[:\s]+([^\n]+)",
        ])
        
        # Extract violation/conviction count - Ontario MVR format
        violation_count_match = re.search(
            r"\*\*\*Number of Convictions:\s*(\d+)\s*\*\*\*",
            text
        )
        if violation_count_match:
            violation_count = violation_count_match.group(1)
        else:
            violation_count = find_value([
                r"Total Violations:\s+(\d+)",
                r"(?:TOTAL\s+)?(?:VIOLATIONS?|CONVICTIONS?|OFFENSES?)[:\s]+(\d+)",
            ])
        
        # Ensure convictions_count is always a string number
        data['convictions_count'] = str(violation_count) if violation_count != 'Not available in document' else '0'
        
        # Extract convictions/violations list
        convictions = []
        
        # For Ontario MVR, if convictions count is 0, return empty list
        if data['convictions_count'] != '0':
            # Look for convictions under "DATE CONVICTIONS, DISCHARGES AND OTHER ACTIONS" section
            # Format: DD/MM/YYYY VIOLATION_TYPE DETAILS
            
            convictions_section_start = text.find('DATE CONVICTIONS')
            if convictions_section_start > -1:
                # Find end of convictions section
                convictions_section_end = text.find('SEARCH SUCCESSFUL', convictions_section_start)
                if convictions_section_end == -1:
                    convictions_section_end = text.find('*** END OF REPORT', convictions_section_start)
                
                if convictions_section_end > convictions_section_start:
                    convictions_text = text[convictions_section_start:convictions_section_end]
                    
                    # Extract all conviction entries - split by date pattern
                    # Pattern: DD/MM/YYYY at start of line followed by violation details
                    lines = convictions_text.split('\n')
                    
                    i = 0
                    while i < len(lines):
                        line = lines[i].strip()
                        
                        # Check if line starts with date pattern (DD/MM/YYYY)
                        if len(line) >= 10 and line[0:2].isdigit() and line[2] == '/' and line[3:5].isdigit() and line[5] == '/':
                            # Extract date and violation text
                            date_part = line[0:10]
                            violation_part = line[10:].strip()
                            
                            # Continue reading lines that are part of this violation (indented or continuation)
                            i += 1
                            while i < len(lines):
                                next_line = lines[i].strip()
                                
                                # Stop if we hit another date or marker
                                if len(next_line) >= 10 and next_line[0:2].isdigit() and next_line[2] == '/' and next_line[3:5].isdigit():
                                    break
                                if next_line.startswith('OFFENCE DATE') or next_line.startswith('SEARCH'):
                                    break
                                
                                # Add continuation lines
                                if next_line and not next_line.startswith('OFFENCE'):
                                    violation_part += ' ' + next_line
                                elif next_line.startswith('OFFENCE DATE'):
                                    break
                                
                                i += 1
                            
                            # Clean up violation text
                            violation_part = re.sub(r'\s+', ' ', violation_part).strip()
                            violation_part = violation_part.replace('OFFENCE DATE', '').strip()
                            
                            if violation_part and len(violation_part) > 3:
                                formatted_conviction = f"{date_part} {violation_part}"
                                if formatted_conviction not in convictions:
                                    convictions.append(formatted_conviction)
                            continue
                        
                        i += 1
        
        # Return empty list if no convictions found
        data['convictions'] = convictions if convictions else []
        
        # Return empty list if no convictions found
        data['convictions'] = convictions if convictions else []
        
        # Extract issue date if available
        data['issue_date'] = find_value([
            r"Issue Date:\s+(\d{2}/\d{2}/\d{4})",
            r"ISSUE\s+DATE[:\s]+(\d{2}/\d{2}/\d{4})",
        ])
        
        # Extract demerit points
        data['demerit_points'] = find_value([
            r"Current Demerit Points:\s+(\d+)",
            r"DEMERIT\s+POINTS[:\s]+(\d+)",
        ])
        
        return data
