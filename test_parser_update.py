"""Test the updated DASH parser"""

import os
from dash_parser import parse_dash_report

uploads_path = r"c:\Users\sayal\Desktop\dashboard ui\uploads"

# Get first DASH PDF
pdf_files = [f for f in os.listdir(uploads_path) if f.endswith('.pdf') and 'DASH' in f]

if pdf_files:
    pdf_path = os.path.join(uploads_path, pdf_files[0])
    print(f"Testing: {pdf_files[0]}\n")
    
    result = parse_dash_report(pdf_path)
    
    print(f"Success: {result['success']}")
    print(f"Errors: {result['errors']}")
    print(f"\nExtracted Data:")
    print("="*60)
    
    for key, value in result['data'].items():
        status = "[OK]" if value != "Not available in document" else "[MISSING]"
        print(f"{status} {key:30} = {value}")
else:
    print("No DASH PDFs found")
