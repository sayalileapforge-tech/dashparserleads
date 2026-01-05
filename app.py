"""
Insurance Dashboard Backend - Python Flask
Handles PDF parsing, data extraction, and database persistence.

STRICT RULES APPLIED:
- No guessing, no assumptions, no auto-fill
- "Not available in document" for missing data
- Extract data EXACTLY as written in PDF
- Analyze FULL PDF (all pages)
- Current policy identified by status/date logic
- Driver deletion shown independently from policy status
"""

import os
import sys
import json
import uuid
import re
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

try:
    import pg8000
    PG8000_AVAILABLE = True
except ImportError:
    PG8000_AVAILABLE = False

try:
    import psycopg
    from psycopg import OperationalError, Error as PostgresError
    PSYCOPG_AVAILABLE = True
except ImportError as e:
    PSYCOPG_AVAILABLE = False
    try:
        import psycopg2
        import psycopg2.extras
        from psycopg2 import OperationalError
        psycopg = None
        PSYCOPG2_AVAILABLE = True
    except ImportError:
        psycopg = None
        psycopg2 = None
        OperationalError = Exception
        PostgresError = Exception
        PSYCOPG2_AVAILABLE = False

from meta_leads_fetcher import get_fetcher  # Meta API integration
from dash_parser import parse_dash_report  # DASH PDF parser
from license_history_integration import (  # G/G1/G2 date calculation
    DriverLicenseHistory,
    process_manual_entry,
    process_pdf_data
)

# Quote persistence endpoint (optional - may use mysql)
try:
    from save_quote_endpoint import save_quote
except:
    save_quote = None  # Optional if mysql not available

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
app = Flask(__name__)
CORS(app)

# In-memory database for temporary storage (when PostgreSQL not available)
mock_leads_db = {}

# Database connection
def get_db_connection():
    """Get PostgreSQL database connection with environment variables"""
    global PSYCOPG_AVAILABLE, PSYCOPG2_AVAILABLE
    
    if not (PG8000_AVAILABLE or PSYCOPG_AVAILABLE or PSYCOPG2_AVAILABLE):
        print("[DB] PostgreSQL drivers not available - using in-memory storage")
        return None
    try:
        # Parse DATABASE_URL or build from environment variables
        db_url = os.getenv('DATABASE_URL')
        
        # Try pg8000 first (pure Python, no system dependencies)
        if PG8000_AVAILABLE:
            try:
                if db_url:
                    # Handle postgres:// or postgresql://
                    # Format: postgresql://user:password@host:port/dbname
                    url_clean = db_url.replace('postgres://', 'postgresql://')
                    import re
                    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', url_clean)
                    if match:
                        user, password, host, port, db = match.groups()
                        port = int(port)
                    else:
                        # Try format without port: postgresql://user:password@host/dbname
                        match = re.match(r'postgresql://([^:]+):([^@]+)@([^/]+)/(.+)', url_clean)
                        if match:
                            user, password, host, db = match.groups()
                            port = 5432
                        else:
                            # Fallback to env vars
                            user = os.getenv('PG_USER', 'insurance_details_user')
                            password = os.getenv('PG_PASSWORD', 'yJB4ToerfMWn0xu0NV7hUdn56ed0RjcR')
                            host = os.getenv('PG_HOST', 'dpg-d5daccmr433s73ad8e70-a')
                            port = int(os.getenv('PG_PORT', 5432))
                            db = os.getenv('PG_DB', 'insurance_details')
                else:
                    user = os.getenv('PG_USER', 'insurance_details_user')
                    password = os.getenv('PG_PASSWORD', 'yJB4ToerfMWn0xu0NV7hUdn56ed0RjcR')
                    host = os.getenv('PG_HOST', 'dpg-d5daccmr433s73ad8e70-a')
                    port = int(os.getenv('PG_PORT', 5432))
                    db = os.getenv('PG_DB', 'insurance_details')
                
                print(f"[DB] Attempting pg8000 connection to {host}:{port}/{db}")
                conn = pg8000.connect(
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    database=db,
                    timeout=10
                )
                print("[DB] ✓ Connected to PostgreSQL using pg8000")
                return conn
            except Exception as e:
                print(f"[DB] pg8000 connection failed: {e}")
                # Don't return, try next driver
        
        # Try psycopg3 (if libpq available)
        if PSYCOPG_AVAILABLE and psycopg is not None:
            try:
                conn = psycopg.connect(db_url)
                print("[DB] ✓ Connected to PostgreSQL using psycopg3")
                return conn
            except ImportError as e:
                print(f"[DB] psycopg3 import error: {e}")
                PSYCOPG_AVAILABLE = False
        
        # Fall back to psycopg2
        if PSYCOPG2_AVAILABLE and psycopg2 is not None:
            try:
                # psycopg2 requires postgresql:// instead of postgres://
                psycopg2_url = db_url.replace('postgres://', 'postgresql://') if db_url else None
                conn = psycopg2.connect(psycopg2_url, cursor_factory=psycopg2.extras.RealDictCursor)
                print("[DB] ✓ Connected to PostgreSQL using psycopg2")
                return conn
            except Exception as e2:
                print(f"[DB] psycopg2 connection failed: {e2}")
        
        print("[DB] Unable to connect to PostgreSQL with any available driver")
        return None
    except Exception as e:
        print(f"[DB] Database connection error: {e}")
        return None

# Helper function to execute UPDATE queries with different drivers
def execute_db_update(conn, query, params):
    """Execute an UPDATE query using the appropriate driver API"""
    try:
        if PG8000_AVAILABLE:
            # pg8000 API - connection object has cursor() method and execute()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            cursor.close()
            return True
        elif PSYCOPG_AVAILABLE and hasattr(conn, 'cursor'):
            # psycopg3 API
            with conn.cursor() as cursor:
                cursor.execute(query, params)
            conn.commit()
            return True
        elif PSYCOPG2_AVAILABLE and hasattr(conn, 'cursor'):
            # psycopg2 API
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            cursor.close()
            return True
        return False
    except Exception as e:
        print(f"[DB] Error executing query: {e}")
        try:
            conn.rollback()
        except:
            pass
        raise

# Store connection in app config (optional - not required to start)
try:
    db_conn = get_db_connection()
    if db_conn:
        app.config['db_connection'] = db_conn
        print("[DB] Database connection established")
    else:
        print("[DB] Database not available - using in-memory storage for updates")
        app.config['db_connection'] = None
except Exception as e:
    print(f"[DB] Database optional - running with in-memory storage")
    print(f"[DB] Error details: {e}")
    app.config['db_connection'] = None

# Register quote save endpoint (optional)
try:
    if app.config['db_connection'] and save_quote:
        save_quote(app)
        print("[API] Quote save endpoint registered")
    else:
        print("[API] Database not connected or save_quote not available - quote saving disabled")
except Exception as e:
    print(f"[API] Warning: Could not register quote endpoint - {e}")

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'insurance_dashboard'),
    'port': int(os.getenv('DB_PORT', 3306))
}


class DatabaseManager:
    """Handle database operations for PostgreSQL."""
    @staticmethod
    def get_connection():
        try:
            return get_db_connection()
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            raise
    @staticmethod
    def save_auto_quote(data: dict) -> dict:
        """
        Save auto insurance quote to database.
        
        Args:
            data: Quote data from form
            
        Returns:
            Result with quote_id
        """
        conn = None
        cursor = None
        
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()
            
            # Extract data
            customer_name = data.get('name', '')
            phone = data.get('phone', '')
            email = data.get('email', '')
            
            # Insert or update meta_leads
            lead_query = """
                INSERT INTO meta_leads (full_name, phone, email)
                VALUES (%s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET phone=EXCLUDED.phone, full_name=EXCLUDED.full_name
            """
            cursor.execute(lead_query, (customer_name, phone, email))
            conn.commit()
            cursor.execute("SELECT id FROM meta_leads WHERE email=%s", (email,))
            lead_id = cursor.fetchone()["id"]

            # Insert into complete_quotes
            quote_query = """
                INSERT INTO complete_quotes (lead_id, quote_type, quote_status)
                VALUES (%s, 'auto', 'draft')
                ON CONFLICT (lead_id) DO UPDATE SET quote_type='auto'
            """
            cursor.execute(quote_query, (lead_id,))
            conn.commit()
            cursor.execute("SELECT id FROM complete_quotes WHERE lead_id=%s", (lead_id,))
            quote_id = cursor.fetchone()["id"]

            # Insert vehicles
            vehicles = data.get('vehicles', [])
            for idx, vehicle in enumerate(vehicles, 1):
                vehicle_query = """
                    INSERT INTO vehicle_details (lead_id, vehicle_sequence, year, make, model, body_type, vin, license_plate, annual_km, vehicle_use, ownership_type, winter_tires, anti_theft_device)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (lead_id, vehicle_sequence) DO UPDATE SET year=EXCLUDED.year, make=EXCLUDED.make, model=EXCLUDED.model
                """
                cursor.execute(vehicle_query, (
                    lead_id,
                    idx,
                    vehicle.get('year'),
                    vehicle.get('make'),
                    vehicle.get('model'),
                    vehicle.get('body_type'),
                    vehicle.get('vin'),
                    vehicle.get('plateNumber'),
                    vehicle.get('annual_km'),
                    vehicle.get('vehicle_use'),
                    vehicle.get('ownership_type'),
                    vehicle.get('winter_tires'),
                    vehicle.get('anti_theft_device')
                ))

            # Insert drivers as manual_entry_data
            drivers = data.get('drivers', [])
            for driver in drivers:
                manual_query = """
                    INSERT INTO manual_entry_data (lead_id, full_name, date_of_birth, gender, marital_status, address, license_number, license_class, license_issue_date, license_expiry_date, first_insurance_date, years_continuous_insurance, years_claims_free, total_claims_6y, at_fault_claims_6y, first_party_claims_6y, comprehensive_claims_6y, dcpd_claims_6y, current_company, current_policy_number, current_policy_expiry, current_operators_count, current_vehicles_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(manual_query, (
                    lead_id,
                    driver.get('name'),
                    driver.get('dob'),
                    driver.get('gender'),
                    driver.get('marital_status'),
                    driver.get('address'),
                    driver.get('dln'),
                    driver.get('licenseClass'),
                    driver.get('issueDate'),
                    driver.get('expiryDate'),
                    driver.get('first_insurance_date'),
                    driver.get('years_continuous_insurance'),
                    driver.get('years_claims_free'),
                    driver.get('total_claims_6y'),
                    driver.get('at_fault_claims_6y'),
                    driver.get('first_party_claims_6y'),
                    driver.get('comprehensive_claims_6y'),
                    driver.get('dcpd_claims_6y'),
                    driver.get('current_company'),
                    driver.get('current_policy_number'),
                    driver.get('current_policy_expiry'),
                    driver.get('current_operators_count'),
                    driver.get('current_vehicles_count')
                ))

            # Insert parsed PDF data if present
            if data.get('parsed_pdf_data'):
                pdf = data['parsed_pdf_data']
                pdf_query = """
                    INSERT INTO parsed_pdf_data (lead_id, document_type, raw_extracted_data)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(pdf_query, (
                    lead_id,
                    pdf.get('document_type'),
                    json.dumps(pdf)
                ))

            # Insert claims history if present
            if data.get('claims_history'):
                for claim in data['claims_history']:
                    claim_query = """
                        INSERT INTO claims_history (lead_id, source_table, claim_date, claim_type, amount, description, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(claim_query, (
                        lead_id,
                        claim.get('source_table'),
                        claim.get('claim_date'),
                        claim.get('claim_type'),
                        claim.get('amount'),
                        claim.get('description'),
                        claim.get('status')
                    ))

            conn.commit()
            print(f"✅ Quote {quote_id} saved successfully (enhanced schema)")
            return {
                'success': True,
                'quote_id': quote_id,
                'lead_id': lead_id
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Database error: {str(e)}")
            return {'success': False, 'error': str(e)}
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def map_extracted_to_ui_fields(parsed_data: dict) -> dict:
    """
    Map extracted PDF data to UI input fields.
    
    Applies STRICT rules:
    - All values from parsed_data are used as-is
    - Driver deletion shown with warning label
    - Relationship preserved exactly
    - Source inconsistencies displayed without correction
    """
    
    driver = parsed_data.get('analyzed_driver', {})
    current_policy = parsed_data.get('current_policy')
    all_policies = parsed_data.get('all_policies', [])
    
    ui_fields = {
        # ▶ DRIVER INFORMATION
        'driver_information': {
            'fullName': driver.get('fullName', 'Not available in document'),
            'dln': driver.get('dln', 'Not available in document'),
            'dob': driver.get('dob', 'Not available in document'),
            'gender': driver.get('gender', 'Not available in document'),
            'maritalStatus': driver.get('maritalStatus', 'Not available in document'),
            'address': driver.get('address', 'Not available in document'),
            'yearsLicensed': driver.get('yearsLicensed', 'Not available in document'),
            'yearsContinuousInsurance': driver.get('yearsContinuousInsurance', 'Not available in document'),
            'yearsContinuousInsurance_note': 'Value provided by source system',  # Source attribution
            'yearsClaimsFree': driver.get('yearsClaimsFree', 'Not available in document'),
            'driverTraining': driver.get('driverTraining', 'Not available in document'),
            'claims_last_6_years': driver.get('claims_last_6_years', 'Not available in document'),
            'at_fault_claims_last_6_years': driver.get('at_fault_claims_last_6_years', 'Not available in document'),
            'comprehensive_losses_last_6_years': driver.get('comprehensive_losses_last_6_years', 'Not available in document'),
            'dcpd_claims_last_6_years': driver.get('dcpd_claims_last_6_years', 'Not available in document'),
        },
        
        # ▶ CURRENT POLICY INSURANCE DETAILS
        'current_policy_details': {},
        
        # ▶ PAST POLICIES
        'past_policies': [],
        
        # ▶ VEHICLE INFORMATION
        'vehicles': [],
        
        # ▶ CLAIMS HISTORY
        'claims_history': {
            'total_claims': parsed_data.get('verification', {}).get('claims_found', 0),
            'claims': parsed_data.get('claims', [])
        },
        
        # ▶ PREVIOUS INQUIRIES
        'inquiries': parsed_data.get('inquiries', []),
        
        # Metadata
        'metadata': {
            'document_type': parsed_data.get('document_type', 'Not available in document'),
            'total_pages_analyzed': parsed_data.get('total_pages', 0),
            'verification': parsed_data.get('verification', {}),
        }
    }
    
    # MAP CURRENT POLICY
    if current_policy:
        policy_fields = {
            'company': current_policy.get('company', 'Not available in document'),
            'policyNumber': current_policy.get('policy_number', 'Not available in document'),
            'status': current_policy.get('status', 'Not available in document'),
            'effectiveDate': current_policy.get('effective_date', 'Not available in document'),
            'expiryDate': current_policy.get('expiry_date', 'Not available in document'),
            'cancellationDate': current_policy.get('cancellation_date', 'N/A'),
            'policyholder': current_policy.get('policyholder', 'Not available in document'),
            'policyholderAddress': current_policy.get('policyholder_address', 'Not available in document'),
            'numOperators': current_policy.get('num_operators', 'Not available in document'),
            'numVehicles': current_policy.get('num_vehicles', 'Not available in document'),
        }
        
        # CRITICAL: Add driver status warning if deleted/excluded
        driver_status = current_policy.get('driver_status', 'Not in this policy')
        if driver_status in ['Deleted', 'Excluded']:
            driver_coverage = current_policy.get('driver_coverage_period', {})
            removal_date = driver_coverage.get('end_date', 'Unknown')
            
            policy_fields['driver_status_warning'] = {
                'icon': '⚠️',
                'type': 'DRIVER_REMOVED',
                'message': f'Driver removed from policy as of {removal_date}',
                'severity': 'warning'
            }
            policy_fields['driver_status'] = driver_status
            policy_fields['driver_role'] = current_policy.get('driver_role', 'Not available in document')
        else:
            policy_fields['driver_status'] = driver_status
            policy_fields['driver_role'] = current_policy.get('driver_role', 'Not available in document')
        
        # Add operators list to policy fields
        operators = current_policy.get('operators', [])
        policy_fields['operators'] = operators
        
        # Find driver relationship
        for op in operators:
            if op.get('name') == driver.get('fullName'):
                policy_fields['driver_relationship'] = op.get('relationship', 'Not available in document')
                break
        
        ui_fields['current_policy_details'] = policy_fields
        
        # MAP VEHICLES IN CURRENT POLICY - also add to policy_fields
        vehicles = current_policy.get('vehicles', [])
        policy_fields['vehicles'] = vehicles
        for vehicle in vehicles:
            vehicle_fields = {
                'year': vehicle.get('year', 'Not available in document'),
                'make': vehicle.get('make', 'Not available in document'),
                'model': vehicle.get('model', 'Not available in document'),
                'vin': vehicle.get('vin', 'Not available in document'),
                'vehicleCode': vehicle.get('vehicle_code', 'Not available in document'),
                'usage': vehicle.get('usage', 'Not available in document'),
                'commutingDistanceOneWay': vehicle.get('commuting_distance_oneway', 'Not available in document'),
                'commutingDistanceAnnual': vehicle.get('commuting_distance_annual', 'Not available in document'),
                'businessUse': vehicle.get('business_use', 'Not available in document'),
                'coverage': vehicle.get('coverage', 'Not available in document'),
                'vehicleLocation': vehicle.get('vehicle_location', 'Not available in document'),
                'vehicleClass': vehicle.get('vehicle_class', 'Not available in document'),
                'drivingRecord': vehicle.get('driving_record', 'Not available in document'),
                'grossVehicleWeight': vehicle.get('gross_vehicle_weight', 'Not available in document'),
                'branding': vehicle.get('branding', 'Not available in document'),
            }
            ui_fields['vehicles'].append(vehicle_fields)
    
    # MAP PAST POLICIES
    for policy in all_policies:
        if policy.get('policy_number') != current_policy.get('policy_number') if current_policy else True:
            past_policy = {
                'company': policy.get('company', 'Not available in document'),
                'policyNumber': policy.get('policy_number', 'Not available in document'),
                'status': policy.get('status', 'Not available in document'),
                'effectiveDate': policy.get('effective_date', 'Not available in document'),
                'expiryDate': policy.get('expiry_date', 'Not available in document'),
                'cancellationDate': policy.get('cancellation_date', 'N/A'),
                'policyholder': policy.get('policyholder', 'Not available in document'),
                'policyholderAddress': policy.get('policyholder_address', 'Not available in document'),
                'numOperators': policy.get('num_operators', 'Not available in document'),
                'numVehicles': policy.get('num_vehicles', 'Not available in document'),
                'driverRole': policy.get('driver_role', 'Not available in document'),
                'driverCoveragePeriod': policy.get('driver_coverage_period', {}),
            }
            ui_fields['past_policies'].append(past_policy)
    
    return ui_fields





# ===== STATIC ROUTES =====

@app.route('/', methods=['GET'])
def index():
    """Serve the Insurance Dashboard API homepage."""
    try:
        # Try multiple paths for deployed and local environments
        possible_paths = [
            'index.html',
            '/opt/render/project/src/index.html',
            './index.html',
            os.path.join(os.path.dirname(__file__), 'index.html')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return Response(content, mimetype='text/html')
        
        # Fallback: return JSON API status
        return jsonify({
            'status': 'Insurance Dashboard API Running',
            'version': '1.0',
            'mode': 'Temporary Demo (No Database)',
            'platform': 'Render.com',
            'endpoints': {
                'health': '/api/health',
                'parse_dash': '/api/parse-dash',
                'parse_mvr': '/api/parse-mvr',
                'g_dates': '/api/calculate-g-dates',
                'incoming_leads': '/api/incoming-leads',
                'webhook': '/api/meta-webhook'
            }
        }), 200
    except Exception as e:
        print(f"[ERROR] Failed to serve homepage: {e}")
        return jsonify({
            'status': 'Insurance Dashboard API Running',
            'version': '1.0',
            'error': str(e)
        }), 200

@app.route('/pdf-parser', methods=['GET'])
def pdf_parser():
    """Serve the PDF Parser UI (DASH & MVR parsing)."""
    try:
        with open('pdf-parser.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content, mimetype='text/html')
    except Exception as e:
        print(f"[ERROR] Failed to serve PDF Parser: {e}")
        return jsonify({'error': 'PDF Parser not found'}), 404

@app.route('/dashboard/<path:filename>', methods=['GET'])
def dashboard(filename):
    """Serve dashboard HTML files from the dashboard folder."""
    try:
        filepath = os.path.join('dashboard', secure_filename(filename))
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return Response(content, mimetype='text/html')
        else:
            return jsonify({'error': f'File {filename} not found'}), 404
    except Exception as e:
        print(f"[ERROR] Failed to serve dashboard: {e}")
        return jsonify({'error': str(e)}), 500

# ===== API ENDPOINTS =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'Insurance Dashboard Backend',
        'version': '2.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get leads from Meta API or return sample data."""
    try:
        page = request.args.get('page', 1, type=int)
        status = request.args.get('status', None)
        search = request.args.get('search', None)
        page_size = request.args.get('page_size', 25, type=int)
        
        print(f"[API] /api/leads - search: {search}, page: {page}, status: {status}")
        
        # 1. Always fetch latest leads from Meta API first
        fetcher = get_fetcher()
        all_leads = fetcher.fetch_leads(limit=1000)
        
        if not all_leads:
            print(f"[API] Meta API returned no leads - using sample data")
            all_leads = [
                {
                    'id': 1,
                    'full_name': 'Anchit Parveen Gupta',
                    'first_name': 'Anchit',
                    'last_name': 'Gupta',
                    'email': 'gupta.anchit407@gmail.com',
                    'phone': '(416) 555-0101',
                    'lead_identity': 'Anchit Parveen Gupta',
                    'contact_info': '(416) 555-0101 | gupta.anchit407@gmail.com',
                    'created_at': '2025-12-29',
                    'status': 'new',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                },
                {
                    'id': 2,
                    'full_name': 'zahra',
                    'first_name': 'zahra',
                    'last_name': '',
                    'email': 'zebraabuzar788@gmail.com',
                    'phone': '(647) 555-0202',
                    'lead_identity': 'zahra',
                    'contact_info': '(647) 555-0202 | zebraabuzar788@gmail.com',
                    'created_at': '2025-12-29',
                    'status': 'new',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                },
                {
                    'id': 3,
                    'full_name': 'nallely prado castro',
                    'first_name': 'nallely',
                    'last_name': 'castro',
                    'email': 'nallely@email.com',
                    'phone': '(905) 555-0303',
                    'lead_identity': 'nallely prado castro',
                    'contact_info': '(905) 555-0303 | nallely@email.com',
                    'created_at': '2025-12-29',
                    'status': 'new',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                },
                {
                    'id': 4,
                    'full_name': 'John Michael Smith',
                    'first_name': 'John',
                    'last_name': 'Smith',
                    'email': 'jsmith@email.com',
                    'phone': '(416) 555-0404',
                    'lead_identity': 'John Michael Smith',
                    'contact_info': '(416) 555-0404 | jsmith@email.com',
                    'created_at': '2025-12-29',
                    'status': 'new',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                },
                {
                    'id': 5,
                    'full_name': 'Sarah Jessica Williams',
                    'first_name': 'Sarah',
                    'last_name': 'Williams',
                    'email': 'sarah.w@email.com',
                    'phone': '(647) 555-0505',
                    'lead_identity': 'Sarah Jessica Williams',
                    'contact_info': '(647) 555-0505 | sarah.w@email.com',
                    'created_at': '2025-12-29',
                    'status': 'contacted',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                },
                {
                    'id': 6,
                    'full_name': 'David Kumar',
                    'first_name': 'David',
                    'last_name': 'Kumar',
                    'email': 'david.kumar@email.com',
                    'phone': '(905) 555-0606',
                    'lead_identity': 'David Kumar',
                    'contact_info': '(905) 555-0606 | david.kumar@email.com',
                    'created_at': '2025-12-29',
                    'status': 'quote_sent',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                },
                {
                    'id': 7,
                    'full_name': 'Maria Garcia Rodriguez',
                    'first_name': 'Maria',
                    'last_name': 'Rodriguez',
                    'email': 'maria.g.r@email.com',
                    'phone': '(416) 555-0707',
                    'lead_identity': 'Maria Garcia Rodriguez',
                    'contact_info': '(416) 555-0707 | maria.g.r@email.com',
                    'created_at': '2025-12-28',
                    'status': 'new',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                },
                {
                    'id': 8,
                    'full_name': 'James Robert Brown',
                    'first_name': 'James',
                    'last_name': 'Brown',
                    'email': 'james.brown@email.com',
                    'phone': '(647) 555-0808',
                    'lead_identity': 'James Robert Brown',
                    'contact_info': '(647) 555-0808 | james.brown@email.com',
                    'created_at': '2025-12-28',
                    'status': 'new',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                },
                {
                    'id': 9,
                    'full_name': 'Lisa Chen',
                    'first_name': 'Lisa',
                    'last_name': 'Chen',
                    'email': 'lisa.chen@email.com',
                    'phone': '(905) 555-0909',
                    'lead_identity': 'Lisa Chen',
                    'contact_info': '(905) 555-0909 | lisa.chen@email.com',
                    'created_at': '2025-12-28',
                    'status': 'contacted',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                },
                {
                    'id': 10,
                    'full_name': 'Michael Ahmed Hassan',
                    'first_name': 'Michael',
                    'last_name': 'Hassan',
                    'email': 'michael.hassan@email.com',
                    'phone': '(416) 555-1010',
                    'lead_identity': 'Michael Ahmed Hassan',
                    'contact_info': '(416) 555-1010 | michael.hassan@email.com',
                    'created_at': '2025-12-28',
                    'status': 'closed_won',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                }
            ]

        # 2. Fetch local updates from PostgreSQL and merge
        try:
            conn = get_db_connection()
            if conn:
                local_data = {}
                if PG8000_AVAILABLE:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM leads")
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    for row in rows:
                        d = dict(zip(columns, row))
                        local_data[str(d.get('meta_lead_id'))] = d
                elif PSYCOPG2_AVAILABLE:
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    cursor.execute("SELECT * FROM leads")
                    rows = cursor.fetchall()
                    for row in rows:
                        local_data[str(row.get('meta_lead_id'))] = row
                cursor.close()
                conn.close()
                
                if local_data:
                    print(f"[API] Merging {len(local_data)} local updates from PostgreSQL")
                    for lead in all_leads:
                        lead_id = str(lead.get('id') or lead.get('meta_lead_id') or '')
                        if lead_id in local_data:
                            # Merge selectively - DON'T overwrite created_at (use Meta's date)
                            updates = local_data[lead_id]
                            for key, value in updates.items():
                                # Skip merging these fields from database (keep Meta's values)
                                if key in ['created_at', 'id', 'meta_lead_id']:
                                    continue
                                if value is not None and value != '':
                                    # Don't overwrite name with generic 'Lead'
                                    if key == 'full_name' and lead.get('full_name') and value == 'Lead':
                                        continue
                                    lead[key] = value
        except Exception as db_e:
            print(f"[API] PostgreSQL merge failed: {db_e}")

        # 3. Merge with in-memory storage (mock_leads_db) as final fallback
        for lead in all_leads:
            lead_id = str(lead.get('id') or lead.get('meta_lead_id') or '')
            if lead_id and lead_id in mock_leads_db:
                stored_data = mock_leads_db[lead_id]
                for key, value in stored_data.items():
                    if key == 'full_name' and lead.get('full_name') and value == 'Lead':
                        continue
                    lead[key] = value
                print(f"[API] Merged in-memory data for lead {lead_id}")
        
        # Filter by search - search across all name and contact fields
        if search:
            search_lower = search.lower()
            print(f"[API] Searching for: '{search_lower}'")
            filtered = []
            for l in all_leads:
                # Search in multiple fields
                searchable_text = ' '.join([
                    str(l.get('full_name', '')),
                    str(l.get('first_name', '')),
                    str(l.get('last_name', '')),
                    str(l.get('phone', '')),
                    str(l.get('email', '')),
                    str(l.get('lead_identity', '')),
                    str(l.get('contact_info', ''))
                ]).lower()
                
                if search_lower in searchable_text:
                    filtered.append(l)
            
            all_leads = filtered
            print(f"[API] Search returned {len(all_leads)} results")
        
        # Filter by status
        if status:
            all_leads = [l for l in all_leads if l.get('status') == status]
        
        # Sort by created_at descending (newest first)
        # Parse dates properly for correct sorting
        def parse_created_date(lead):
            created = lead.get('created_at', '')
            if not created:
                return '0000-00-00'  # Fallback for empty dates
            
            # Convert to string if needed
            created_str = str(created)
            
            # Handle ISO format with timestamp: 2026-01-02T18:59:52+0000 → 2026-01-02T18:59:52
            if 'T' in created_str:
                # Remove timezone info and keep full ISO datetime for proper sorting
                created_str = created_str.split('+')[0].split('Z')[0]
                return created_str  # Keep as YYYY-MM-DDTHH:MM:SS for chronological sorting
            
            # Handle simple date format: 2025-12-29
            return created_str
        
        try:
            # Sort by date descending (newest first) - ISO format sorts correctly as string
            all_leads.sort(key=lambda x: parse_created_date(x), reverse=True)
            print(f"[API] Sorted {len(all_leads)} leads by created_at (newest first)")
            
            # Log top 5 leads for verification
            print(f"[API] Top 5 leads after sorting:")
            for i, lead in enumerate(all_leads[:5]):
                print(f"[API]   #{i+1}: {lead.get('full_name')} | created_at: {lead.get('created_at')} | parsed: {parse_created_date(lead)}")
        except Exception as e:
            print(f"[API] Warning: Could not sort leads: {e}")
            # Debug: Show first 3 leads after sorting
            for i, lead in enumerate(all_leads[:3]):
                print(f"[API] Top {i+1}: {lead.get('full_name')} - {parse_created_date(lead)}")
        except Exception as e:
            print(f"[API] Warning: Could not sort leads: {e}")
        
        # Pagination
        total = len(all_leads)
        pages = (total + page_size - 1) // page_size if total > 0 else 0
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_leads = all_leads[start_idx:end_idx]
        
        print(f"[API] Returning {len(paginated_leads)} paginated results")
        
        return jsonify({
            'success': True,
            'leads': paginated_leads,
            'total': total,
            'page': page,
            'pages': pages
        })
    except Exception as e:
        print(f"[ERROR] /api/leads failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'leads': [],
            'total': 0
        }), 500




@app.route('/api/quotes/auto', methods=['POST'])
def save_auto_quote():
    """
    Save auto insurance quote.
    
    Expected JSON:
    {
        "name": "John Doe",
        "phone": "(416) 555-0123",
        "email": "john@example.com",
        "ownership": "owned",
        "use": "pleasure",
        "annualKm": 15000,
        "winterTires": "yes",
        "antiTheft": "no",
        "drivers": [...],
        "vehicles": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        # Save to database
        result = DatabaseManager.save_auto_quote(data)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'quote_id': result['quote_id'],
                'message': 'Quote saved successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 500
        
    except Exception as e:
        return jsonify({
            'error': f'Save error: {str(e)}'
        }), 500


@app.route('/api/quotes/property', methods=['POST'])
def save_property_quote():
    """
    Save property insurance quote.
    
    Expected JSON:
    {
        "name": "John Doe",
        "phone": "(416) 555-0123",
        "email": "john@example.com",
        "properties": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        # Save property quote to MySQL
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                # Insert into meta_leads if not exists
                lead_query = """
                    INSERT INTO meta_leads (full_name, phone, email)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE phone=VALUES(phone), email=VALUES(email)
                """
                cursor.execute(lead_query, (data.get('name'), data.get('phone'), data.get('email')))
                conn.commit()
                # Get lead_id
                cursor.execute("SELECT id FROM meta_leads WHERE email=%s", (data.get('email'),))
                lead_id = cursor.fetchone()[0]
                # Insert property details
                for prop in data.get('properties', []):
                    prop_query = """
                        INSERT INTO property_details (lead_id, property_type, address, city, postal_code, province, year_built, square_footage, number_of_storeys, number_of_units, owner_occupied, purchased_date, first_insured_year, has_mortgage, lender_name, full_bathrooms, half_bathrooms, bedrooms, has_burglar_alarm, has_fire_alarm, has_sprinkler_system, has_deadbolts, electrical_status, plumbing_status, roofing_status, heating_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(prop_query, (
                        lead_id,
                        prop.get('property_type'),
                        prop.get('address'),
                        prop.get('city'),
                        prop.get('postal_code'),
                        prop.get('province'),
                        prop.get('year_built'),
                        prop.get('square_footage'),
                        prop.get('number_of_storeys'),
                        prop.get('number_of_units'),
                        prop.get('owner_occupied'),
                        prop.get('purchased_date'),
                        prop.get('first_insured_year'),
                        prop.get('has_mortgage'),
                        prop.get('lender_name'),
                        prop.get('full_bathrooms'),
                        prop.get('half_bathrooms'),
                        prop.get('bedrooms'),
                        prop.get('has_burglar_alarm'),
                        prop.get('has_fire_alarm'),
                        prop.get('has_sprinkler_system'),
                        prop.get('has_deadbolts'),
                        prop.get('electrical_status'),
                        prop.get('plumbing_status'),
                        prop.get('roofing_status'),
                        prop.get('heating_status')
                    ))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({
                    'success': True,
                    'message': 'Property quote saved successfully',
                    'lead_id': lead_id
                }), 201
            else:
                return jsonify({'error': 'Database not available'}), 500
        except Exception as db_e:
            return jsonify({'error': f'Database error: {db_e}'}), 500
        
    except Exception as e:
        return jsonify({
            'error': f'Save error: {str(e)}'
        }), 500



@app.route('/api/parse-mvr', methods=['POST'])
def parse_mvr_pdf():
    """
    Parse MVR PDF and extract driver information (strict mode - only MVR fields).
    
    Expected: multipart/form-data with 'file' field containing PDF
    Returns: {
        'success': bool,
        'document_type': 'MVR' | 'DASH',
        'mvr_data': {
            'full_name': str,
            'birth_date': str (YYYY-MM-DD),
            'licence_number': str,
            'licence_expiry_date': str (YYYY-MM-DD),
            'convictions_count': str,
            'convictions': list
        },
        'errors': list
    }
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'document_type': None,
                'mvr_data': {},
                'errors': ['No file provided']
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'document_type': None,
                'mvr_data': {},
                'errors': ['No file selected']
            }), 400
        
        # Validate file extension
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'document_type': None,
                'mvr_data': {},
                'errors': ['File must be a PDF']
            }), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        temp_filename = f"{file_id}_{filename}"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        file.save(temp_path)
        
        try:
            # Parse the MVR PDF using strict parser
            from mvr_parser_strict import StrictMVRParserV1
            
            parser = StrictMVRParserV1()
            result = parser.parse_pdf(temp_path)
            
            # Log the parsing result
            print(f"[MVR PARSER] Parsed {temp_filename}")
            print(f"[MVR PARSER] Document type: {result.get('document_type')}")
            print(f"[MVR PARSER] Success: {result['success']}")
            if result.get('errors'):
                print(f"[MVR PARSER] Errors: {result['errors']}")
            
            # SPECIFICATION: G/G1/G2 calculation REQUIRES BOTH MVR AND DASH data
            # - issue_date: from MVR
            # - first_insurance_date: from DASH (End of Latest Term)
            # DO NOT calculate from MVR data alone - it's incomplete without DASH data
            # MVR parsing alone cannot provide firstInsuranceDate (that comes from DASH)
            
            # Store MVR birth_date and licence_expiry_date for later use when DASH data is available
            if result.get('success') and result.get('mvr_data'):
                mvr_data = result['mvr_data']
                birth_date = mvr_data.get('birth_date')
                licence_expiry_date = mvr_data.get('licence_expiry_date')
                
                # Mark that these dates are available from MVR for experience validation
                result['mvr_data']['has_birth_date'] = birth_date and birth_date != 'Not available in document'
                result['mvr_data']['has_expiry_date'] = licence_expiry_date and licence_expiry_date != 'Not available in document'
            
            return jsonify(result), 200
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    except Exception as e:
        print(f"[ERROR] /api/parse-mvr failed: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'document_type': None,
            'mvr_data': {},
            'errors': [f'Server error: {str(e)}']
        }), 500


@app.route('/api/parse-dash', methods=['POST'])
def parse_dash_pdf():
    """
    Parse DASH PDF and extract driver information.
    
    Expected: multipart/form-data with 'file' field containing PDF
    Returns: {
        'success': bool,
        'data': {
            'name': str,
            'dob': str (MM/DD/YYYY),
            'dln': str,
            'address': str,
            'gender': str (M/F),
            'marital_status': str,
            'years_licensed': str,
            'years_continuous_insurance': str,
            'years_claims_free': str,
            'claims_6y': str,
            'first_party_6y': str,
            'comprehensive_6y': str,
            'dcpd_6y': str,
            'current_company': str,
            'current_policy_expiry': str (MM/DD/YYYY),
            'current_vehicles_count': str,
            'current_operators_count': str
        },
        'errors': list
    }
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'data': {},
                'errors': ['No file provided']
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'data': {},
                'errors': ['No file selected']
            }), 400
        
        # Validate file extension
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'data': {},
                'errors': ['File must be a PDF']
            }), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        temp_filename = f"{file_id}_{filename}"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        file.save(temp_path)
        
        try:
            # Parse the DASH PDF
            result = parse_dash_report(temp_path)
            
            # Log the parsing result
            print(f"[DASH PARSER] Parsed {temp_filename}")
            print(f"[DASH PARSER] Success: {result['success']}")
            if result.get('errors'):
                print(f"[DASH PARSER] Errors: {result['errors']}")
            else:
                print(f"[DASH PARSER] Extracted {len(result.get('data', {}))} fields")
            
            # NOTE: G/G1/G2 calculation is NOT done here because:
            # - DASH provides: firstInsuranceDate (End of Latest Term)
            # - MVR provides: issueDate, licenseExpiryDate, birthDate
            # - G/G1/G2 requires BOTH DASH data AND MVR data
            # - Calculation happens in /api/calculate-g-dates endpoint
            # - This is called during combination (PDF + Manual entry)
            
            if result.get('success') and result.get('data'):
                result['data']['g_calculation_note'] = "G/G1/G2 calculated during combination with MVR data"
                print(f"[DASH PARSER] G/G1/G2 calculation deferred to combination endpoint")
            
            return jsonify(result), 200
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    except Exception as e:
        print(f"[ERROR] /api/parse-dash failed: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'data': {},
            'errors': [f'Server error: {str(e)}']
        }), 500


@app.route('/api/calculate-g-dates', methods=['POST'])
def calculate_g_dates():
    """
    Calculate G/G1/G2 dates from Issue Date and First Insurance Date.
    
    Accepts both manual entry and PDF data formats.
    
    MANUAL ENTRY:
    {
        'mode': 'manual',
        'issue_date': 'mm/dd/yyyy',
        'first_insurance_date': 'mm/dd/yyyy'
    }
    
    PDF DATA:
    {
        'mode': 'pdf',
        'pdf_data': {...}  # Full PDF extraction result
    }
    
    Returns:
    {
        'success': bool,
        'g_date': 'YYYY-MM-DD',
        'g2_date': 'YYYY-MM-DD',
        'g1_date': 'YYYY-MM-DD',
        'total_months': int,
        'strategy': str,
        'calculation_performed': bool,
        'error': str or None,
        'note': str or None
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        mode = data.get('mode', 'manual')
        processor = DriverLicenseHistory()
        
        if mode == 'manual':
            # Manual entry mode
            issue_date = data.get('issue_date')
            first_insurance_date = data.get('first_insurance_date')
            driver_name = data.get('driver_name')
            birth_date = data.get('birth_date')  # Optional, for experience validation
            expiry_date = data.get('expiry_date')  # Optional, for experience validation
            
            result = processor.process_manual_entry(
                issue_date,
                first_insurance_date,
                driver_name,
                birth_date,
                expiry_date
            )
            
        elif mode == 'pdf':
            # PDF data mode
            pdf_data = data.get('pdf_data', {})
            
            # DEBUG: Log what we received
            print(f"[DEBUG /api/calculate-g-dates] PDF mode - received pdf_data:")
            print(f"  pdf_data keys: {list(pdf_data.keys())}")
            if 'driver' in pdf_data:
                driver = pdf_data['driver']
                print(f"  driver type: {type(driver)}")
                print(f"  driver.firstInsuranceDate = {driver.get('firstInsuranceDate', 'MISSING')}")
                print(f"  driver keys: {list(driver.keys())[:5]}...")  # First 5 keys
            if 'mvr_data' in pdf_data:
                mvr = pdf_data['mvr_data']
                print(f"  mvr_data type: {type(mvr)}")
                print(f"  mvr_data.issue_date = {mvr.get('issue_date', 'MISSING')}")
                print(f"  mvr_data.licence_expiry_date = {mvr.get('licence_expiry_date', 'MISSING')}")
                print(f"  mvr_data keys: {list(mvr.keys())[:5]}...")  # First 5 keys
            
            result = processor.process_pdf_extraction(pdf_data)
            
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown mode: {mode}'
            }), 400
        
        # Format for UI response
        response = {
            'success': result.get('success', False),
            'g_date': result.get('g_date'),
            'g2_date': result.get('g2_date'),
            'g1_date': result.get('g1_date'),
            'total_months': result.get('total_months'),
            'strategy': result.get('strategy'),
            'calculation_performed': result.get('calculation_performed', False),
            'error': result.get('error'),
            'note': result.get('note'),
            'experience_warning': result.get('experience_warning')
        }
        
        print(f"[G/G1/G2 CALCULATOR] Mode: {mode}")
        print(f"[G/G1/G2 CALCULATOR] Success: {response['success']}")
        print(f"[G/G1/G2 CALCULATOR] Response keys: {list(response.keys())}")
        print(f"[G/G1/G2 CALCULATOR] Full response: {response}")
        if response.get('calculation_performed'):
            print(f"[G/G1/G2 CALCULATOR] G Date: {response['g_date']}")
            print(f"[G/G1/G2 CALCULATOR] G2 Date: {response['g2_date']}")
            print(f"[G/G1/G2 CALCULATOR] G1 Date: {response['g1_date']}")
        if response.get('experience_warning'):
            print(f"[G/G1/G2 CALCULATOR] Experience Warning: {response['experience_warning']}")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"[ERROR] /api/calculate-g-dates failed: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/test-db', methods=['GET'])
def test_database():
    """Test database connection."""
    try:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Database connection successful'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# FACEBOOK META WEBHOOK - Auto-sync leads
# ============================================

# Store leads in memory (temporary storage)
incoming_leads = []

@app.route('/api/meta-webhook', methods=['GET', 'POST'])
def meta_webhook():
    """Facebook Meta webhook for automatic lead sync"""
    
    if request.method == 'GET':
        # Webhook verification
        verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'insurance_dashboard_webhook')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if token == verify_token:
            print("[META WEBHOOK] Webhook verified successfully")
            return challenge
        else:
            print("[META WEBHOOK] Webhook verification failed")
            return 'Forbidden', 403
    
    if request.method == 'POST':
        # Receive leads from Facebook
        try:
            data = request.get_json()
            print(f"[META WEBHOOK] Received data: {data}")
            
            # Extract leads from Meta webhook payload
            if data.get('entry'):
                for entry in data['entry']:
                    if entry.get('changes'):
                        for change in entry['changes']:
                            if change.get('value') and change['value'].get('leadgen_id'):
                                lead_data = change['value']
                                
                                # Store lead in memory
                                incoming_leads.append({
                                    'id': lead_data.get('leadgen_id'),
                                    'form_id': lead_data.get('form_id'),
                                    'ad_id': lead_data.get('ad_id'),
                                    'created_time': lead_data.get('created_time'),
                                    'field_data': lead_data.get('field_data', []),
                                    'timestamp': datetime.now().isoformat()
                                })
                                # Also persist to MySQL meta_leads
                                try:
                                    conn = get_db_connection()
                                    if conn:
                                        cursor = conn.cursor()
                                        # Extract fields
                                        full_name = ''
                                        email = ''
                                        phone = ''
                                        for f in lead_data.get('field_data', []):
                                            if f.get('name') == 'full_name':
                                                full_name = f.get('values', [''])[0]
                                            if f.get('name') == 'email':
                                                email = f.get('values', [''])[0]
                                            if f.get('name') == 'phone_number':
                                                phone = f.get('values', [''])[0]
                                        lead_query = """
                                            INSERT INTO meta_leads (meta_lead_id, full_name, email, phone, created_at)
                                            VALUES (%s, %s, %s, %s, NOW())
                                            ON DUPLICATE KEY UPDATE full_name=VALUES(full_name), email=VALUES(email), phone=VALUES(phone)
                                        """
                                        cursor.execute(lead_query, (
                                            lead_data.get('leadgen_id'),
                                            full_name,
                                            email,
                                            phone
                                        ))
                                        conn.commit()
                                        cursor.close()
                                        conn.close()
                                except Exception as db_e:
                                    print(f"[META WEBHOOK] MySQL persist error: {db_e}")
                                print(f"[META WEBHOOK] Lead received: {lead_data.get('leadgen_id')}")
            
            # Always return 200 OK to Meta
            return jsonify({'success': True}), 200
            
        except Exception as e:
            print(f"[META WEBHOOK] Error: {e}")
            return jsonify({'error': str(e)}), 200  # Return 200 anyway so Meta doesn't retry


@app.route('/api/incoming-leads', methods=['GET'])
def get_incoming_leads():
    """Get all leads received from Meta webhook"""
    return jsonify({
        'success': True,
        'leads': incoming_leads,
        'total': len(incoming_leads)
    }), 200


@app.route('/api/incoming-leads/<lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    """Remove a lead from incoming leads"""
    global incoming_leads
    incoming_leads = [l for l in incoming_leads if l.get('id') != lead_id]
    return jsonify({'success': True}), 200


# ============================================================
# LEAD DATA PERSISTENCE ENDPOINTS - Store to MySQL
# ============================================================

@app.route('/api/leads/<lead_id>/signal', methods=['PUT'])
def update_lead_signal(lead_id):
    """Update lead's meta signal"""
    try:
        data = request.get_json()
        signal_value = data.get('signal')
        
        print(f"[DB] Updating lead {lead_id} signal to: {signal_value}", flush=True)
        
        # Try to save to PostgreSQL if available
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                query = """
                    INSERT INTO leads (meta_lead_id, full_name, signal)
                    VALUES (%s, 'Lead', %s)
                    ON CONFLICT (meta_lead_id) DO UPDATE SET signal = EXCLUDED.signal, updated_at = CURRENT_TIMESTAMP
                """
                execute_db_update(conn, query, (lead_id, signal_value))
                print(f"[DB] ✓ Lead {lead_id} signal saved to PostgreSQL", flush=True)
            else:
                # Fallback to in-memory storage
                if lead_id not in mock_leads_db:
                    mock_leads_db[lead_id] = {'meta_lead_id': lead_id, 'full_name': 'Lead'}
                mock_leads_db[lead_id]['signal'] = signal_value
                mock_leads_db[lead_id]['updated_at'] = datetime.now().isoformat()
                print(f"[DB] PostgreSQL not available - signal saved to in-memory storage", flush=True)
        except Exception as db_error:
            print(f"[DB] Error saving signal: {db_error}", flush=True)
            # Fallback to in-memory storage
            if lead_id not in mock_leads_db:
                mock_leads_db[lead_id] = {'meta_lead_id': lead_id, 'full_name': 'Lead'}
            mock_leads_db[lead_id]['signal'] = signal_value
            mock_leads_db[lead_id]['updated_at'] = datetime.now().isoformat()
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

        # Send signal to Facebook Conversions API
        import requests, time, hashlib, os
        pixel_id = os.getenv('FB_PIXEL_ID', '2251357192000496')
        access_token = os.getenv('FB_PIXEL_TOKEN', '')
        fb_url = f'https://graph.facebook.com/v18.0/{pixel_id}/events?access_token={access_token}'

        # Optionally fetch user data from DB for hashing
        user_email = ''
        user_phone = ''
        try:
            conn = get_db_connection()
            if conn:
                # Use execute_db_query helper if we had one, but for SELECT we need a cursor
                if PG8000_AVAILABLE:
                    cursor = conn.cursor()
                    cursor.execute("SELECT email, phone FROM leads WHERE meta_lead_id=%s", (lead_id,))
                    row = cursor.fetchone()
                    if row:
                        # pg8000 returns a list/tuple
                        user_email = row[0] if len(row) > 0 else ''
                        user_phone = row[1] if len(row) > 1 else ''
                elif PSYCOPG2_AVAILABLE:
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    cursor.execute("SELECT email, phone FROM leads WHERE meta_lead_id=%s", (lead_id,))
                    row = cursor.fetchone()
                    if row:
                        user_email = row.get('email', '') or ''
                        user_phone = row.get('phone', '') or ''
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"[FB] Could not fetch user data for hashing: {e}")

        def hash_data(data):
            return hashlib.sha256(data.strip().lower().encode()).hexdigest() if data else ''

        payload = {
            "data": [
                {
                    "event_name": "Signal",
                    "event_time": int(time.time()),
                    "user_data": {
                        "em": [hash_data(user_email)] if user_email else [],
                        "ph": [hash_data(user_phone)] if user_phone else []
                    },
                    "custom_data": {
                        "signal": signal_value
                    }
                }
            ]
        }
        try:
            fb_resp = requests.post(fb_url, json=payload, timeout=10)
            print(f"[FB] Signal sent to Conversions API: {fb_resp.status_code} {fb_resp.text}")
        except Exception as fb_e:
            print(f"[FB] Error sending signal to Conversions API: {fb_e}")

        return jsonify({'success': True, 'message': 'Signal updated and sent to Facebook'}), 200
    except Exception as e:
        print(f"[API] Error updating signal: {str(e)}", flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>/premium', methods=['PUT'])
def update_lead_premium(lead_id):
    """Update lead's premium potential"""
    try:
        data = request.get_json()
        auto_premium = data.get('auto_premium')
        home_premium = data.get('home_premium')
        tenant_premium = data.get('tenant_premium')
        total_premium = data.get('premium') # Total
        
        print(f"[DB] Updating lead {lead_id} premiums: Auto={auto_premium}, Home={home_premium}, Tenant={tenant_premium}, Total={total_premium}", flush=True)
        
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                try:
                    # Store total and individual premiums
                    query = """
                        INSERT INTO leads (meta_lead_id, premium, premium_auto, premium_home, premium_tenant, full_name)
                        VALUES (%s, %s, %s, %s, %s, 'Lead')
                        ON CONFLICT (meta_lead_id) DO UPDATE 
                        SET premium = EXCLUDED.premium, 
                            premium_auto = EXCLUDED.premium_auto,
                            premium_home = EXCLUDED.premium_home,
                            premium_tenant = EXCLUDED.premium_tenant,
                            updated_at = CURRENT_TIMESTAMP
                    """
                    execute_db_update(conn, query, (lead_id, total_premium, auto_premium, home_premium, tenant_premium))
                    print(f"[DB] ✓ Lead {lead_id} premiums saved to PostgreSQL", flush=True)
                    return jsonify({'success': True, 'message': 'Premium updated'}), 200
                except Exception as db_error:
                    print(f"[DB] Error saving to PostgreSQL: {db_error}", flush=True)
                    raise
            else:
                # Fallback to in-memory storage - here we CAN store individual values
                if lead_id not in mock_leads_db:
                    mock_leads_db[lead_id] = {'meta_lead_id': lead_id, 'full_name': 'Lead'}
                
                mock_leads_db[lead_id]['auto_premium'] = auto_premium
                mock_leads_db[lead_id]['home_premium'] = home_premium
                mock_leads_db[lead_id]['tenant_premium'] = tenant_premium
                mock_leads_db[lead_id]['premium'] = total_premium
                mock_leads_db[lead_id]['updated_at'] = datetime.now().isoformat()
                
                print(f"[DB] ✓ Lead {lead_id} premiums saved to in-memory storage", flush=True)
                return jsonify({'success': True, 'message': 'Premiums updated (stored locally)'}), 200
        except Exception as db_error:
            print(f"[DB] Error updating premium: {db_error}", flush=True)
            # Fallback to in-memory storage
            if lead_id not in mock_leads_db:
                mock_leads_db[lead_id] = {'meta_lead_id': lead_id, 'full_name': 'Lead'}
            mock_leads_db[lead_id]['auto_premium'] = auto_premium
            mock_leads_db[lead_id]['home_premium'] = home_premium
            mock_leads_db[lead_id]['tenant_premium'] = tenant_premium
            mock_leads_db[lead_id]['premium'] = total_premium
            mock_leads_db[lead_id]['updated_at'] = datetime.now().isoformat()
            return jsonify({'success': True, 'message': 'Premiums updated (stored locally)'}), 200
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    except Exception as e:
        print(f"[API] Error updating premium: {str(e)}", flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Update lead status (generic endpoint)"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        print(f"[DB] Updating lead {lead_id} status to: {status}", flush=True)
        
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                try:
                    query = """
                        INSERT INTO leads (meta_lead_id, status, full_name)
                        VALUES (%s, %s, 'Lead')
                        ON CONFLICT (meta_lead_id) DO UPDATE 
                        SET status = EXCLUDED.status, updated_at = CURRENT_TIMESTAMP
                    """
                    execute_db_update(conn, query, (lead_id, status))
                    print(f"[DB] ✓ Lead {lead_id} status saved to PostgreSQL", flush=True)
                    return jsonify({'success': True, 'message': 'Status updated', 'status': status}), 200
                except Exception as db_error:
                    print(f"[DB] Error saving to PostgreSQL: {db_error}", flush=True)
                    raise
            else:
                # Fallback to in-memory storage
                if lead_id not in mock_leads_db:
                    mock_leads_db[lead_id] = {'meta_lead_id': lead_id, 'full_name': 'Lead'}
                mock_leads_db[lead_id]['status'] = status
                mock_leads_db[lead_id]['updated_at'] = datetime.now().isoformat()
                print(f"[DB] ✓ Lead {lead_id} status saved to in-memory storage", flush=True)
                return jsonify({'success': True, 'message': 'Status updated (stored locally)', 'status': status}), 200
        except Exception as db_error:
            print(f"[DB] Error updating status: {db_error}", flush=True)
            # Still save to in-memory as backup
            if lead_id not in mock_leads_db:
                mock_leads_db[lead_id] = {'meta_lead_id': lead_id, 'full_name': 'Lead'}
            mock_leads_db[lead_id]['status'] = status
            mock_leads_db[lead_id]['updated_at'] = datetime.now().isoformat()
            return jsonify({'success': True, 'message': 'Status updated (stored locally)', 'status': status}), 200
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    except Exception as e:
        print(f"[API] Error updating status: {str(e)}", flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>/potential-status', methods=['PUT'])
def update_lead_potential_status(lead_id):
    """Update lead's potential status"""
    try:
        data = request.get_json()
        potential_status = data.get('potential_status')
        
        print(f"[DB] Updating lead {lead_id} potential status to: {potential_status}", flush=True)
        
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                try:
                    query = """
                        INSERT INTO leads (meta_lead_id, potential_status, full_name)
                        VALUES (%s, %s, 'Lead')
                        ON CONFLICT (meta_lead_id) DO UPDATE 
                        SET potential_status = EXCLUDED.potential_status, updated_at = CURRENT_TIMESTAMP
                    """
                    execute_db_update(conn, query, (lead_id, potential_status))
                    print(f"[DB] ✓ Lead {lead_id} potential status saved to PostgreSQL", flush=True)
                    return jsonify({'success': True, 'message': 'Potential status updated'}), 200
                except Exception as db_error:
                    print(f"[DB] Error saving to PostgreSQL: {db_error}", flush=True)
                    raise
            else:
                # Fallback to in-memory storage
                if lead_id not in mock_leads_db:
                    mock_leads_db[lead_id] = {'meta_lead_id': lead_id, 'full_name': 'Lead'}
                mock_leads_db[lead_id]['potential_status'] = potential_status
                mock_leads_db[lead_id]['updated_at'] = datetime.now().isoformat()
                print(f"[DB] ✓ Lead {lead_id} potential status saved to in-memory storage", flush=True)
                return jsonify({'success': True, 'message': 'Potential status updated (stored locally)'}), 200
        except Exception as db_error:
            print(f"[DB] Error updating potential status: {db_error}", flush=True)
            # Fallback to in-memory storage
            if lead_id not in mock_leads_db:
                mock_leads_db[lead_id] = {'meta_lead_id': lead_id, 'full_name': 'Lead'}
            mock_leads_db[lead_id]['potential_status'] = potential_status
            mock_leads_db[lead_id]['updated_at'] = datetime.now().isoformat()
            return jsonify({'success': True, 'message': 'Potential status updated (stored locally)'}), 200
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    except Exception as e:
        print(f"[API] Error updating potential status: {str(e)}", flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>/renewal-date', methods=['PUT'])
def update_lead_renewal_date(lead_id):
    """Update lead's renewal date"""
    try:
        data = request.get_json()
        renewal_date = data.get('renewal_date')
        
        print(f"[DB] Updating lead {lead_id} renewal date to: {renewal_date}", flush=True)
        
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                try:
                    query = """
                        INSERT INTO leads (meta_lead_id, renewal_date, full_name)
                        VALUES (%s, %s, 'Lead')
                        ON CONFLICT (meta_lead_id) DO UPDATE 
                        SET renewal_date = EXCLUDED.renewal_date, updated_at = CURRENT_TIMESTAMP
                    """
                    execute_db_update(conn, query, (lead_id, renewal_date))
                    print(f"[DB] ✓ Lead {lead_id} renewal date saved to PostgreSQL", flush=True)
                    return jsonify({'success': True, 'message': 'Renewal date updated'}), 200
                except Exception as db_error:
                    print(f"[DB] Error saving to PostgreSQL: {db_error}", flush=True)
                    raise
            else:
                # Fallback to in-memory storage
                if lead_id not in mock_leads_db:
                    mock_leads_db[lead_id] = {'meta_lead_id': lead_id, 'full_name': 'Lead'}
                mock_leads_db[lead_id]['renewal_date'] = renewal_date
                mock_leads_db[lead_id]['updated_at'] = datetime.now().isoformat()
                print(f"[DB] ✓ Lead {lead_id} renewal date saved to in-memory storage", flush=True)
                return jsonify({'success': True, 'message': 'Renewal date updated (stored locally)'}), 200
        except Exception as db_error:
            print(f"[DB] Error updating renewal date: {db_error}", flush=True)
            # Fallback to in-memory storage
            if lead_id not in mock_leads_db:
                mock_leads_db[lead_id] = {'meta_lead_id': lead_id, 'full_name': 'Lead'}
            mock_leads_db[lead_id]['renewal_date'] = renewal_date
            mock_leads_db[lead_id]['updated_at'] = datetime.now().isoformat()
            return jsonify({'success': True, 'message': 'Renewal date updated (stored locally)'}), 200
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    except Exception as e:
        print(f"[API] Error updating renewal date: {str(e)}", flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/quotes/save', methods=['POST'])
def save_quote_data():
    """Save quote data (DASH, MVR, Property) to MySQL"""
    try:
        data = request.get_json()
        lead_id = data.get('lead_id')
        quote_type = data.get('quote_type')  # 'auto', 'property', 'combined'
        
        print(f"[DB] Saving {quote_type} quote for lead {lead_id}", flush=True)
        
        conn = None
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                # Save parsed PDF data if present
                if data.get('dash_data'):
                    dash_query = """
                        INSERT INTO parsed_pdf_data (lead_id, document_type, raw_extracted_data, parsed_at)
                        VALUES (%s, 'DASH', %s, NOW())
                    """
                    cursor.execute(dash_query, (lead_id, json.dumps(data.get('dash_data'))))
                
                if data.get('mvr_data'):
                    mvr_query = """
                        INSERT INTO parsed_pdf_data (lead_id, document_type, raw_extracted_data, parsed_at)
                        VALUES (%s, 'MVR', %s, NOW())
                    """
                    cursor.execute(mvr_query, (lead_id, json.dumps(data.get('mvr_data'))))
                
                # Save property data if present
                if data.get('property_data'):
                    prop_query = """
                        INSERT INTO property_details (lead_id, address, city, postal_code, property_type, 
                                                     created_at)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                    """
                    prop_data = data.get('property_data')
                    cursor.execute(prop_query, (lead_id, prop_data.get('address'), prop_data.get('city'), 
                                              prop_data.get('postal'), prop_data.get('property_type')))
                
                conn.commit()
                cursor.close()
                print(f"[DB] ✓ Quote data for lead {lead_id} saved to MySQL", flush=True)
            else:
                print(f"[DB] MySQL not available - quote not persisted", flush=True)
        except Exception as db_error:
            print(f"[DB] Error saving quote: {db_error}", flush=True)
        finally:
            if conn:
                conn.close()
        
        return jsonify({'success': True, 'message': 'Quote saved'}), 200
    except Exception as e:
        print(f"[API] Error saving quote: {str(e)}", flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# LIVE DATABASE VIEW FOR CLIENT
# ============================================================

def init_db():
    """Initialize database tables if they don't exist"""
    conn = get_db_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        # Ensure all columns exist for persistence
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                meta_lead_id TEXT PRIMARY KEY,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                status TEXT DEFAULT 'new',
                renewal_date TEXT,
                signal TEXT DEFAULT 'red',
                premium TEXT,
                premium_auto TEXT,
                premium_home TEXT,
                premium_tenant TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        print("[DB] Tables initialized successfully")
    except Exception as e:
        print(f"[DB] Error initializing tables: {e}")
    finally:
        conn.close()

# Initialize DB on startup
init_db()

@app.route('/db-view')
def db_view():
    """Live view of the PostgreSQL database for the client"""
    conn = get_db_connection()
    if not conn: 
        return "<h1>Database Connection Failed</h1><p>Check Render Environment Variables.</p>", 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads ORDER BY updated_at DESC")
        
        # Handle different driver return types
        if PG8000_AVAILABLE:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        else:
            # For psycopg2 RealDictCursor or similar
            try:
                rows = cursor.fetchall()
                if rows and isinstance(rows[0], dict):
                    columns = list(rows[0].keys())
                    rows = [list(r.values()) for r in rows]
                else:
                    columns = [desc[0] for desc in cursor.description]
            except:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
        
        html = f"""
        <html><head><title>Live DB View</title>
        <style>
            table{{border-collapse:collapse;width:100%;font-family:sans-serif;font-size:12px;}}
            th,td{{border:1px solid #ddd;padding:8px;text-align:left;}}
            th{{background-color:#4f46e5;color:white;position:sticky;top:0;}}
            tr:nth-child(even){{background-color:#f9fafb;}}
            tr:hover{{background-color:#f3f4f6;}}
            .status-new{{color:#2563eb;font-weight:bold;}}
            .status-won{{color:#059669;font-weight:bold;}}
        </style></head><body>
        <div style="padding:20px;">
            <h1>PostgreSQL Live Records</h1>
            <p>Showing latest updates first. Total records: <b>{len(rows)}</b></p>
            <table><tr>"""
        
        for col in columns: html += f"<th>{col}</th>"
        html += "</tr>"
        
        for row in rows:
            html += "<tr>"
            for i, val in enumerate(row):
                cell_class = ""
                if columns[i] == 'status':
                    if val == 'new': cell_class = 'class="status-new"'
                    if val == 'closed_won': cell_class = 'class="status-won"'
                html += f"<td {cell_class}>{val if val is not None else ''}</td>"
            html += "</tr>"
            
        html += "</table></div></body></html>"
        cursor.close()
        conn.close()
        return html
    except Exception as e:
        return f"<h1>Error Fetching Data</h1><p>{str(e)}</p>", 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore')
    
    # Render uses PORT environment variable
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 3001)))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    
    print(f"[START] Flask server starting on port {port}", flush=True)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=False
    )
