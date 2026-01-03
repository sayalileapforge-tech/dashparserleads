"""
Minimal Flask server for testing customer search autocomplete
"""
import os
import sys
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from pathlib import Path

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)
CORS(app)

# Sample leads data
SAMPLE_LEADS = [
    {"full_name": "Anchit Parveen Gupta", "first_name": "Anchit", "last_name": "Gupta", "phone": "(416) 555-0101", "email": "anchit@example.com"},
    {"full_name": "zahra", "first_name": "zahra", "last_name": "zahra", "phone": "(416) 555-0202", "email": "zahra@example.com"},
    {"full_name": "nallely prado castro", "first_name": "nallely", "last_name": "prado castro", "phone": "(416) 555-0303", "email": "nallely@example.com"},
    {"full_name": "John Smith", "first_name": "John", "last_name": "Smith", "phone": "(416) 555-0404", "email": "john@example.com"},
    {"full_name": "Sarah Johnson", "first_name": "Sarah", "last_name": "Johnson", "phone": "(416) 555-0505", "email": "sarah@example.com"},
]

@app.route('/')
def index():
    """Serve the PDF parser page"""
    html_file = Path('Untitled-2.html')
    if html_file.exists():
        return send_file(str(html_file), mimetype='text/html')
    return jsonify({"error": "HTML file not found"}), 404

@app.route('/pdf-parser')
def pdf_parser():
    """Serve the PDF parser page"""
    html_file = Path('Untitled-2.html')
    if html_file.exists():
        return send_file(str(html_file), mimetype='text/html')
    return jsonify({"error": "HTML file not found"}), 404

@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Search and return leads"""
    print("[API] GET /api/leads called")
    search_query = request.args.get('search', '').lower()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    print(f"[SEARCH] Query: '{search_query}'")
    
    # Filter leads
    if search_query:
        filtered = [
            lead for lead in SAMPLE_LEADS
            if search_query in lead['full_name'].lower()
            or search_query in lead['first_name'].lower()
            or search_query in lead['last_name'].lower()
            or search_query in lead['phone'].lower()
            or search_query in lead['email'].lower()
        ]
        print(f"[SEARCH] Filtered {len(filtered)} leads from {len(SAMPLE_LEADS)}")
    else:
        filtered = SAMPLE_LEADS
    
    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]
    
    result = {
        "total": len(filtered),
        "page": page,
        "page_size": page_size,
        "leads": paginated
    }
    
    print(f"[OK] Returning {len(paginated)} leads")
    return jsonify(result)

@app.route('/api/upload-mvr', methods=['POST'])
def upload_mvr():
    """Handle PDF upload (placeholder)"""
    print("[API] POST /api/upload-mvr called")
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Just echo back success for now
    return jsonify({
        "success": True,
        "filename": file.filename,
        "message": "File received (parsing not yet implemented)"
    })

if __name__ == '__main__':
    print("=" * 60)
    print("SIMPLE SEARCH SERVER - Starting on http://127.0.0.1:3001")
    print("=" * 60)
    app.run(host='127.0.0.1', port=3001, debug=False)
