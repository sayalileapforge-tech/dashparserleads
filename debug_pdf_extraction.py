"""Debug PDF extraction - see what text is actually in the PDFs"""

import os
from PyPDF2 import PdfReader

# Find PDFs in uploads folder
uploads_path = os.path.join(os.getcwd(), 'uploads')

if os.path.exists(uploads_path):
    pdf_files = [f for f in os.listdir(uploads_path) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF files in uploads folder")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(uploads_path, pdf_file)
        print(f"\n{'='*80}")
        print(f"PDF: {pdf_file}")
        print(f"{'='*80}")
        
        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                print(f"Total pages: {len(reader.pages)}")
                
                # Extract text from first 2 pages
                for page_num in range(min(2, len(reader.pages))):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    print(f"\n--- Page {page_num + 1} ---")
                    print(text[:1000])  # First 1000 chars
                    print("\n[...content truncated...]")
        except Exception as e:
            print(f"Error reading {pdf_file}: {e}")
else:
    print(f"Uploads folder not found: {uploads_path}")
    print("Creating it...")
    os.makedirs(uploads_path, exist_ok=True)
    print("No PDFs available to debug")
