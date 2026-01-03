"""Test MVR extraction to see conviction text"""

from PyPDF2 import PdfReader
import re

# Use one of the MVR files
pdf_path = r'c:\Users\sayal\Desktop\dashboard ui\uploads\f181fdd4-71ad-4b0c-ada8-188b8cb3f467_MVR_ON_G04027170060201.pdf'

with open(pdf_path, 'rb') as f:
    pdf_reader = PdfReader(f)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

print("=== FULL MVR TEXT ===")
print(text[:2000])
print("\n=== SEARCHING FOR CONVICTIONS ===")

# Look for conviction count
conviction_count_match = re.search(r"\*\*\*Number of Convictions:\s*(\d+)\s*\*\*\*", text)
if conviction_count_match:
    print(f"Conviction count found: {conviction_count_match.group(1)}")
else:
    print("Conviction count NOT found with *** pattern")

# Try to find any violations section
violations_section = re.search(r'(?:VIOLATIONS|CONVICTIONS|OFFENSES).*?(?=\n\n|\Z)', text, re.DOTALL | re.IGNORECASE)
if violations_section:
    print("\nViolations section found:")
    print(violations_section.group(0)[:500])

# Look for numbered items
print("\n=== LOOKING FOR NUMBERED ITEMS ===")
numbered = re.findall(r'^\d+\.\s+(.+?)$', text, re.MULTILINE)
if numbered:
    for i, item in enumerate(numbered[:5]):
        print(f"{i+1}. {item}")
else:
    print("No numbered items found")

# Search for lines with specific keywords
print("\n=== SEARCHING FOR KEYWORDS ===")
for line in text.split('\n'):
    if any(kw in line.lower() for kw in ['violation', 'conviction', 'offense', 'speeding', 'parking']):
        print(f"  {line.strip()}")
