"""
Save Quote Endpoint - Stores all quote data to database
"""
import json
from datetime import datetime
from flask import request, jsonify
import mysql.connector
from mysql.connector import Error

def save_quote(app):
    """
    Save complete quote with all drivers, properties, and manual entries
    
    Request JSON:
    {
        "lead_name": "John Doe",
        "lead_email": "john@example.com", 
        "lead_phone": "416-555-0123",
        "signal": "green",  // or "red"
        "entry_mode": "auto",  // auto, property, or manual
        
        "manual_entry": {
            "ownership": "owned",
            "vehicle_use": "pleasure",
            "annual_km": 15000,
            "winter_tires": true,
            "anti_theft": false,
            "phone": "416-555-0123",
            "email": "john@example.com"
        },
        
        "drivers": [
            {
                "driver_number": 1,
                "relationship": "applicant",
                "dash_data": { ...full DASH object... },
                "mvr_data": { ...full MVR object... },
                "g_dates": {
                    "g_date": "2024-01-15",
                    "g1_date": "2022-01-15",
                    "g2_date": "2021-01-15",
                    "insufficient_experience": false
                }
            },
            {
                "driver_number": 2,
                "relationship": "spouse",
                "dash_data": { ...full DASH object... },
                "mvr_data": { ...full MVR object... },
                "g_dates": { ...g dates... }
            }
        ],
        
        "properties": [
            {
                "property_number": 1,
                "property_address": "123 Main St",
                "property_city": "Toronto",
                "property_postal": "M5H 2N2",
                "property_type": "Primary Home",
                ...all other property fields...
            }
        ]
    }
    """
    
    @app.route('/api/save-quote', methods=['POST'])
    def handle_save_quote():
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('lead_name'):
                return jsonify({'success': False, 'error': 'Lead name required'}), 400
            
            # Get database connection
            conn = app.config.get('db_connection')
            if not conn or not conn.is_connected():
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor(dictionary=True)
            
            try:
                # 1. INSERT Quote
                signal = data.get('signal', 'red')
                entry_mode = data.get('entry_mode', 'auto')
                
                manual_entry = data.get('manual_entry', {})
                
                query_quote = """
                    INSERT INTO quotes 
                    (lead_name, lead_email, lead_phone, meta_id, meta_source, potential_status, 
                     premium, renewal_date, signal, status, entry_mode,
                     ownership, vehicle_use, annual_km, winter_tires, anti_theft)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                quote_values = (
                    data.get('lead_name'),
                    data.get('lead_email'),
                    data.get('lead_phone'),
                    data.get('meta_id'),
                    data.get('meta_source'),
                    data.get('potential_status'),
                    data.get('premium'),
                    data.get('renewal_date'),
                    signal,
                    'submitted',
                    entry_mode,
                    manual_entry.get('ownership'),
                    manual_entry.get('vehicle_use'),
                    manual_entry.get('annual_km'),
                    manual_entry.get('winter_tires'),
                    manual_entry.get('anti_theft')
                )
                
                cursor.execute(query_quote, quote_values)
                quote_id = cursor.lastrowid
                
                print(f"[SAVE] Created quote {quote_id} for {data.get('lead_name')}")
                
                # 2. INSERT Drivers
                drivers = data.get('drivers', [])
                driver_count = 0
                
                for driver in drivers:
                    driver_number = driver.get('driver_number', 1)
                    relationship = driver.get('relationship', 'applicant')
                    
                    dash_data = driver.get('dash_data', {})
                    mvr_data = driver.get('mvr_data', {})
                    g_dates = driver.get('g_dates', {})
                    
                    query_driver = """
                        INSERT INTO quote_drivers
                        (quote_id, driver_number, relationship,
                         dash_name, dash_dln, dash_dob, dash_gender, dash_marital_status,
                         dash_address, dash_years_licensed, dash_years_continuous_insurance,
                         dash_years_claims_free, dash_nonpay_3y, dash_claims_6y,
                         dash_first_party_6y, dash_dcpd_6y, dash_current_company,
                         dash_current_policy_expiry, dash_current_vehicles_count,
                         dash_current_operators_count, dash_first_insurance_date,
                         mvr_birth_date, mvr_licence_expiry_date, mvr_convictions_count,
                         mvr_issue_date, g_date, g1_date, g2_date, insufficient_experience,
                         dash_json, mvr_json)
                        VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    driver_values = (
                        quote_id,
                        driver_number,
                        relationship,
                        # DASH fields
                        dash_data.get('name'),
                        dash_data.get('dln'),
                        dash_data.get('dob') if dash_data.get('dob') and dash_data.get('dob') != '-' else None,
                        dash_data.get('gender'),
                        dash_data.get('marital_status'),
                        dash_data.get('address'),
                        dash_data.get('years_licensed'),
                        dash_data.get('years_continuous_insurance'),
                        dash_data.get('years_claims_free'),
                        dash_data.get('history_nonpay_3y'),
                        dash_data.get('claims_6y'),
                        dash_data.get('first_party_6y'),
                        dash_data.get('dcpd_6y'),
                        dash_data.get('current_company'),
                        dash_data.get('current_policy_expiry'),
                        dash_data.get('current_vehicles_count'),
                        dash_data.get('current_operators_count'),
                        dash_data.get('firstInsuranceDate'),
                        # MVR fields
                        mvr_data.get('birth_date'),
                        mvr_data.get('licence_expiry_date'),
                        mvr_data.get('convictions_count'),
                        mvr_data.get('issue_date'),
                        # G dates
                        g_dates.get('g_date'),
                        g_dates.get('g1_date'),
                        g_dates.get('g2_date'),
                        g_dates.get('insufficient_experience', False),
                        # JSON backups
                        json.dumps(dash_data),
                        json.dumps(mvr_data)
                    )
                    
                    cursor.execute(query_driver, driver_values)
                    driver_count += 1
                
                print(f"[SAVE] Saved {driver_count} drivers for quote {quote_id}")
                
                # 3. INSERT Properties
                properties = data.get('properties', [])
                property_count = 0
                
                for prop in properties:
                    query_property = """
                        INSERT INTO quote_properties
                        (quote_id, property_number, property_address, property_city,
                         property_postal, property_type, year_built, storeys, units, families,
                         year_purchased, owner_occupied, inlaw_suite, basement_apartment,
                         living_area_sqft, basement_area_sqft, basement_finished_percent,
                         electrical, plumbing, roofing, heating, full_baths, half_baths,
                         burglar_alarm, fire_alarm, sprinkler_system, smoke_detectors,
                         fire_extinguishers, block_watch, walled, deadbolts, property_json)
                        VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    prop_values = (
                        quote_id,
                        prop.get('property_number', 1),
                        prop.get('property_address'),
                        prop.get('property_city'),
                        prop.get('property_postal'),
                        prop.get('property_type'),
                        prop.get('year_built'),
                        prop.get('storeys'),
                        prop.get('units'),
                        prop.get('families'),
                        prop.get('year_purchased'),
                        prop.get('owner_occupied'),
                        prop.get('inlaw_suite'),
                        prop.get('basement_apartment'),
                        prop.get('living_area_sqft'),
                        prop.get('basement_area_sqft'),
                        prop.get('basement_finished_percent'),
                        prop.get('electrical'),
                        prop.get('plumbing'),
                        prop.get('roofing'),
                        prop.get('heating'),
                        prop.get('full_baths'),
                        prop.get('half_baths'),
                        prop.get('burglar_alarm'),
                        prop.get('fire_alarm'),
                        prop.get('sprinkler_system'),
                        prop.get('smoke_detectors'),
                        prop.get('fire_extinguishers'),
                        prop.get('block_watch'),
                        prop.get('walled'),
                        prop.get('deadbolts'),
                        json.dumps(prop)
                    )
                    
                    cursor.execute(query_property, prop_values)
                    property_count += 1
                
                print(f"[SAVE] Saved {property_count} properties for quote {quote_id}")
                
                # Commit transaction
                conn.commit()
                
                return jsonify({
                    'success': True,
                    'quote_id': quote_id,
                    'message': f'Quote saved successfully with {driver_count} drivers and {property_count} properties'
                }), 201
                
            except Error as db_err:
                conn.rollback()
                print(f"[SAVE] Database error: {db_err}")
                return jsonify({'success': False, 'error': str(db_err)}), 500
            finally:
                cursor.close()
                
        except Exception as err:
            print(f"[SAVE] Error: {err}")
            return jsonify({'success': False, 'error': str(err)}), 500

    return handle_save_quote
