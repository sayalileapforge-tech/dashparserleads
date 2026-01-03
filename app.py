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
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS

try:
    import mysql.connector
    from mysql.connector import Error
except:
    Error = Exception  # Fallback if mysql not available

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

# Database connection
def get_db_connection():
    """Get MySQL database connection with environment variables"""
    try:
        # Get from environment variables (for Render/production) or use defaults (for local)
        host = os.getenv('MYSQL_HOST', 'localhost')
        port = int(os.getenv('MYSQL_PORT', 3306))
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', 'root@123')
        database = os.getenv('MYSQL_DATABASE', 'insurance_leads')
        
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

# Store connection in app config (optional - not required to start)
try:
    db_conn = get_db_connection()
    if db_conn:
        app.config['db_connection'] = db_conn
        print("[DB] Database connection established")
    else:
        print("[DB] Database not available - running in temporary mode")
        app.config['db_connection'] = None
except Exception as e:
    print(f"[DB] Database optional - running without database")
    print(f"[DB] Error details: {e}")
    app.config['db_connection'] = None

# Register quote save endpoint (optional)
try:
    if app.config['db_connection']:
        save_quote(app)
        print("[API] Quote save endpoint registered")
    else:
        print("[API] Database not connected - quote saving disabled")
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
    """Handle database operations."""
    
    @staticmethod
    def get_connection():
        """Create database connection."""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except Error as e:
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
            
            # Insert customer
            customer_query = """
                INSERT INTO customers (name, phone, email, created_at)
                VALUES (%s, %s, %s, NOW())
            """
            cursor.execute(customer_query, (customer_name, phone, email))
            customer_id = cursor.lastrowid
            
            # Insert auto quote
            quote_query = """
                INSERT INTO auto_quotes (customer_id, ownership, vehicle_use, annual_km, 
                                        winter_tires, anti_theft, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(quote_query, (
                customer_id,
                data.get('ownership', 'owned'),
                data.get('use', 'pleasure'),
                data.get('annualKm', 0),
                data.get('winterTires', 'no'),
                data.get('antiTheft', 'no')
            ))
            quote_id = cursor.lastrowid
            
            # Insert drivers
            drivers = data.get('drivers', [])
            for driver in drivers:
                driver_query = """
                    INSERT INTO drivers (quote_id, name, dln, dob, address, 
                                        license_class, license_status, issue_date, 
                                        expiry_date, province, relationship, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """
                cursor.execute(driver_query, (
                    quote_id,
                    driver.get('name'),
                    driver.get('dln'),
                    driver.get('dob'),
                    driver.get('address'),
                    driver.get('licenseClass'),
                    driver.get('licenseStatus'),
                    driver.get('issueDate'),
                    driver.get('expiryDate'),
                    driver.get('province'),
                    driver.get('rel', 'applicant')
                ))
                driver_id = cursor.lastrowid
                
                # Insert driver documents (if parsing was done)
                if driver.get('parsed_from_dash'):
                    doc_query = """
                        INSERT INTO driver_documents (driver_id, document_type, 
                                                     file_path, extracted_data, created_at)
                        VALUES (%s, %s, %s, %s, NOW())
                    """
                    cursor.execute(doc_query, (
                        driver_id,
                        'dash',
                        driver.get('file_path', ''),
                        json.dumps(driver.get('extracted_data', {}))
                    ))
            
            # Insert vehicles
            vehicles = data.get('vehicles', [])
            for vehicle in vehicles:
                vehicle_query = """
                    INSERT INTO vehicles (quote_id, year, make, model, vin, 
                                         plate_number, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """
                cursor.execute(vehicle_query, (
                    quote_id,
                    vehicle.get('year'),
                    vehicle.get('make'),
                    vehicle.get('model'),
                    vehicle.get('vin'),
                    vehicle.get('plateNumber')
                ))
            
            conn.commit()
            
            print(f"✅ Quote {quote_id} saved successfully")
            return {
                'success': True,
                'quote_id': quote_id,
                'customer_id': customer_id
            }
            
        except Error as e:
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
        
        print(f"[API] /api/leads - search: {search}, page: {page}")
        
        # Use sample data (Meta API can hang or crash)
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
                },
                {
                    'id': 11,
                    'full_name': 'Angela Patricia Johnson',
                    'first_name': 'Angela',
                    'last_name': 'Johnson',
                    'email': 'angela.johnson@email.com',
                    'phone': '(647) 555-1111',
                    'lead_identity': 'Angela Patricia Johnson',
                    'contact_info': '(647) 555-1111 | angela.johnson@email.com',
                    'created_at': '2025-12-27',
                    'status': 'new',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                },
                {
                    'id': 12,
                    'full_name': 'Christopher Lee',
                    'first_name': 'Christopher',
                    'last_name': 'Lee',
                    'email': 'chris.lee@email.com',
                    'phone': '(905) 555-1212',
                    'lead_identity': 'Christopher Lee',
                    'contact_info': '(905) 555-1212 | chris.lee@email.com',
                    'created_at': '2025-12-27',
                    'status': 'quote_sent',
                    'premium': '',
                    'potential_status': '',
                    'renewal_date': ''
                },
                {
                    'id': 13,
                    'full_name': 'Natasha Petrov',
                    'first_name': 'Natasha',
                    'last_name': 'Petrov',
                    'email': 'natasha.p@email.com',
                    'phone': '(416) 555-1313',
                    'lead_identity': 'Natasha Petrov',
                    'contact_info': '(416) 555-1313 | natasha.p@email.com',
                    'created_at': '2025-12-27',
                    'status': 'new'
                },
                {
                    'id': 14,
                    'full_name': 'Kevin Thomas Murphy',
                    'first_name': 'Kevin',
                    'last_name': 'Murphy',
                    'email': 'kevin.murphy@email.com',
                    'phone': '(647) 555-1414',
                    'lead_identity': 'Kevin Thomas Murphy',
                    'contact_info': '(647) 555-1414 | kevin.murphy@email.com',
                    'created_at': '2025-12-27',
                    'status': 'contacted'
                },
                {
                    'id': 15,
                    'full_name': 'Jennifer Wilson',
                    'first_name': 'Jennifer',
                    'last_name': 'Wilson',
                    'email': 'jen.wilson@email.com',
                    'phone': '(905) 555-1515',
                    'lead_identity': 'Jennifer Wilson',
                    'contact_info': '(905) 555-1515 | jen.wilson@email.com',
                    'created_at': '2025-12-26',
                    'status': 'new'
                },
                {
                    'id': 16,
                    'full_name': 'Daniel Martinez',
                    'first_name': 'Daniel',
                    'last_name': 'Martinez',
                    'email': 'daniel.martinez@email.com',
                    'phone': '(416) 555-1616',
                    'lead_identity': 'Daniel Martinez',
                    'contact_info': '(416) 555-1616 | daniel.martinez@email.com',
                    'created_at': '2025-12-26',
                    'status': 'new'
                },
                {
                    'id': 17,
                    'full_name': 'Rachel Thompson',
                    'first_name': 'Rachel',
                    'last_name': 'Thompson',
                    'email': 'rachel.t@email.com',
                    'phone': '(647) 555-1717',
                    'lead_identity': 'Rachel Thompson',
                    'contact_info': '(647) 555-1717 | rachel.t@email.com',
                    'created_at': '2025-12-26',
                    'status': 'quote_sent'
                },
                {
                    'id': 18,
                    'full_name': 'Brandon Scott Davis',
                    'first_name': 'Brandon',
                    'last_name': 'Davis',
                    'email': 'brandon.davis@email.com',
                    'phone': '(905) 555-1818',
                    'lead_identity': 'Brandon Scott Davis',
                    'contact_info': '(905) 555-1818 | brandon.davis@email.com',
                    'created_at': '2025-12-26',
                    'status': 'new'
                },
                {
                    'id': 19,
                    'full_name': 'Victoria Lewis',
                    'first_name': 'Victoria',
                    'last_name': 'Lewis',
                    'email': 'victoria.lewis@email.com',
                    'phone': '(416) 555-1919',
                    'lead_identity': 'Victoria Lewis',
                    'contact_info': '(416) 555-1919 | victoria.lewis@email.com',
                    'created_at': '2025-12-25',
                    'status': 'closed_won'
                }
            ]
        
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
                    print(f"[API] Match: {l.get('full_name', 'UNKNOWN')}")
            
            all_leads = filtered
            print(f"[API] Search returned {len(all_leads)} results")
        
        # Filter by status
        if status:
            all_leads = [l for l in all_leads if l.get('status') == status]
        
        # Sort by created_at descending (newest first)
        # This ensures latest leads from Facebook appear at the top
        try:
            all_leads.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            print(f"[API] Sorted leads by created_at (newest first)")
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
        
        # TODO: Implement property quote saving
        return jsonify({
            'success': True,
            'message': 'Property quote saved successfully'
        }), 201
        
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
    
    port = int(os.getenv('FLASK_PORT', 3001))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    
    print(f"[START] Flask server starting on port {port}", flush=True)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=False
    )
