#!/usr/bin/env python3
"""
Database Export Script - Exports leads data to JSON/CSV format
Useful for showing clients what's stored in the database
Run: python export_database.py
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from app.core.database import engine, Base
from app.models.lead import Lead

def export_to_json():
    """Export all leads to JSON file"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        leads = session.query(Lead).all()
        
        leads_data = []
        for lead in leads:
            lead_dict = {
                'id': lead.id,
                'meta_lead_id': lead.meta_lead_id,
                'first_name': lead.first_name,
                'last_name': lead.last_name,
                'full_name': lead.full_name,
                'email': lead.email,
                'phone': lead.phone,
                'company_name': lead.company_name,
                'job_title': lead.job_title,
                'city': lead.city,
                'state': lead.state,
                'country': lead.country,
                'zip_code': lead.zip_code,
                'status': lead.status,
                'signal': lead.signal,
                'auto_premium': lead.auto_premium,
                'home_premium': lead.home_premium,
                'tenant_premium': lead.tenant_premium,
                'notes': lead.notes,
                'synced_at': lead.synced_at.isoformat() if lead.synced_at else None,
                'created_at': lead.created_at.isoformat() if lead.created_at else None,
                'updated_at': lead.updated_at.isoformat() if lead.updated_at else None,
            }
            leads_data.append(lead_dict)
        
        # Create exports directory
        exports_dir = Path(__file__).parent / 'exports'
        exports_dir.mkdir(exist_ok=True)
        
        # Save JSON
        json_file = exports_dir / f'leads_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(json_file, 'w') as f:
            json.dump({
                'exported_at': datetime.now().isoformat(),
                'total_records': len(leads_data),
                'database': 'insurance_leads',
                'table': 'leads',
                'leads': leads_data
            }, f, indent=2)
        
        print(f"✅ JSON exported to: {json_file}")
        print(f"   Total records: {len(leads_data)}")
        
        return json_file
        
    finally:
        session.close()

def export_to_csv():
    """Export all leads to CSV file"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        leads = session.query(Lead).all()
        
        # Create exports directory
        exports_dir = Path(__file__).parent / 'exports'
        exports_dir.mkdir(exist_ok=True)
        
        # Save CSV
        csv_file = exports_dir / f'leads_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'ID', 'Meta Lead ID', 'First Name', 'Last Name', 'Full Name',
                'Email', 'Phone', 'Company', 'Job Title', 'City', 'State',
                'Country', 'ZIP', 'Status', 'Signal', 'Auto Premium', 'Home Premium',
                'Tenant Premium', 'Notes', 'Synced At', 'Created At', 'Updated At'
            ])
            
            # Data
            for lead in leads:
                writer.writerow([
                    lead.id,
                    lead.meta_lead_id,
                    lead.first_name or '',
                    lead.last_name or '',
                    lead.full_name or '',
                    lead.email or '',
                    lead.phone or '',
                    lead.company_name or '',
                    lead.job_title or '',
                    lead.city or '',
                    lead.state or '',
                    lead.country or '',
                    lead.zip_code or '',
                    lead.status or '',
                    lead.signal or '',
                    lead.auto_premium or '',
                    lead.home_premium or '',
                    lead.tenant_premium or '',
                    lead.notes or '',
                    lead.synced_at or '',
                    lead.created_at or '',
                    lead.updated_at or '',
                ])
        
        print(f"✅ CSV exported to: {csv_file}")
        print(f"   Total records: {len(leads)}")
        
        return csv_file
        
    finally:
        session.close()

def get_database_stats():
    """Get database statistics"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        total_leads = session.query(Lead).count()
        green_signals = session.query(Lead).filter(Lead.signal == 'green').count()
        red_signals = session.query(Lead).filter(Lead.signal == 'red').count()
        
        status_counts = session.query(
            Lead.status,
            (__import__('sqlalchemy').func.count(Lead.id)).label('count')
        ).group_by(Lead.status).all()
        
        stats = {
            'total_leads': total_leads,
            'green_signals': green_signals,
            'red_signals': red_signals,
            'by_status': {str(status[0]): status[1] for status in status_counts},
            'exported_at': datetime.now().isoformat()
        }
        
        print("\n📊 DATABASE STATISTICS:")
        print(f"   Total Leads: {total_leads}")
        print(f"   Green Signal (Qualified): {green_signals}")
        print(f"   Red Signal (Not Qualified): {red_signals}")
        print("\n   By Status:")
        for status, count in stats['by_status'].items():
            print(f"      {status}: {count}")
        
        return stats
        
    finally:
        session.close()

if __name__ == '__main__':
    print("🗄️  DATABASE EXPORT TOOL")
    print("=" * 50)
    
    # Get statistics
    get_database_stats()
    
    print("\n" + "=" * 50)
    print("📤 EXPORTING DATA...\n")
    
    # Export to JSON
    json_file = export_to_json()
    
    # Export to CSV
    csv_file = export_to_csv()
    
    print("\n" + "=" * 50)
    print("✅ EXPORT COMPLETE!")
    print(f"\n📁 Files saved in: backend/exports/")
    print(f"\nYour client can download and view:")
    print(f"  • JSON format (structured): {json_file.name}")
    print(f"  • CSV format (spreadsheet): {csv_file.name}")
