"""Deep PDF debugging - extract and analyze actual PDF content"""

import os
from PyPDF2 import PdfReader
import re

uploads_path = r"c:\Users\sayal\Desktop\dashboard ui\uploads"

# Get first DASH PDF
pdf_files = [f for f in os.listdir(uploads_path) if f.endswith('.pdf') and 'DASH' in f]

if pdf_files:
    pdf_path = os.path.join(uploads_path, pdf_files[0])
    print(f"Analyzing: {pdf_files[0]}\n")
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            
            # Get all text
            full_text = ""
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                full_text += text + "\n\n--- PAGE BREAK ---\n\n"
            
            # Print first 2000 chars
            print("="*80)
            print("FULL PDF TEXT (first 2000 chars):")
            print("="*80)
            print(full_text[:2000])
            
            # Now test our regex patterns
            print("\n" + "="*80)
            print("REGEX PATTERN TESTS:")
            print("="*80)
            
            patterns = {
                'name': [
                    r"(?:INSURED|NAME)[:\s]+([A-Za-z\s,'.]+?)(?:\n|$)",
                    r"^([A-Za-z][A-Za-z\s,'.]+)\n"
                ],
                'dob': [
                    r"DATE\s+OF\s+BIRTH[:\s]+(\d{1,2}/\d{1,2}/\d{4})",
                    r"DOB[:\s]+(\d{1,2}/\d{1,2}/\d{4})",
                ],
                'dln': [
                    r"DRIVER\s+LICENSE\s+NUMBER[:\s]+([A-Z0-9\-]+)",
                ],
                'firstInsuranceDate': [
                    r"End of (?:the )?Latest Term\s*:?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})",
                ],
                'current_company': [
                    r"(?:CURRENT\s+)?INSUR(?:ANCE\s+)?(?:COMPANY|CARRIER)[:\s]+([A-Za-z\s&'.]+?)(?:\n|$)",
                ]
            }
            
            for field_name, pattern_list in patterns.items():
                print(f"\n{field_name}:")
                for pattern in pattern_list:
                    match = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        value = match.group(1).strip() if match.lastindex else match.group(0).strip()
                        print(f"  [MATCHED] {value}")
                        print(f"    Pattern: {pattern}")
                        break
                else:
                    print(f"  [NO MATCH] for any pattern")
                    # Show nearby text
                    print(f"  Looking for sample keywords in text...")
                    if 'INSURED' in full_text or 'NAME' in full_text:
                        idx = full_text.find('INSURED') if 'INSURED' in full_text else full_text.find('NAME')
                        if idx > 0:
                            print(f"    Found near: ...{full_text[max(0, idx-20):idx+100]}...")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No DASH PDFs found in uploads")
