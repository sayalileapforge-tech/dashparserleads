"""Test the updated MVR parser"""

import os
from mvr_parser_strict import StrictMVRParserV1

uploads_path = r"c:\Users\sayal\Desktop\dashboard ui\uploads"

# Get first MVR PDF
pdf_files = [f for f in os.listdir(uploads_path) if f.endswith('.pdf') and 'MVR' in f]

if pdf_files:
    pdf_path = os.path.join(uploads_path, pdf_files[0])
    print(f"Testing MVR Parser: {pdf_files[0]}\n")
    
    parser = StrictMVRParserV1()
    result = parser.parse_pdf(pdf_path)
    
    print(f"Success: {result['success']}")
    print(f"Document Type: {result['document_type']}")
    print(f"Errors: {result['errors']}")
    print(f"\nExtracted Data:")
    print("="*60)
    
    for key, value in result['mvr_data'].items():
        status = "[OK]" if value != "Not available in document" else "[MISSING]"
        print(f"{status} {key:25} = {value}")
else:
    print("No MVR PDFs found")
