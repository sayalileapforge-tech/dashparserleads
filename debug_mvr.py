"""Debug MVR PDF extraction"""

import os
from PyPDF2 import PdfReader

uploads_path = r"c:\Users\sayal\Desktop\dashboard ui\uploads"

# Get first MVR PDF
pdf_files = [f for f in os.listdir(uploads_path) if f.endswith('.pdf') and 'MVR' in f]

if pdf_files:
    pdf_path = os.path.join(uploads_path, pdf_files[0])
    print(f"Analyzing MVR: {pdf_files[0]}\n")
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            
            # Get all text
            full_text = ""
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                full_text += text + "\n\n--- PAGE BREAK ---\n\n"
            
            # Print first 3000 chars
            print("="*80)
            print("MVR PDF TEXT (first 3000 chars):")
            print("="*80)
            print(full_text[:3000])
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No MVR PDFs found")
