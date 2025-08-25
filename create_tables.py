#!/usr/bin/env python3
"""
Database migration script to create all tables and seed data
Run this script to set up your FuelExpress database
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, Fuel, Address, Order

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    
    # Create all tables
    db.create_all()
    
    print("✅ Database tables created successfully!")

def seed_fuel_data():
    """Seed the database with fuel types"""
    print("Seeding fuel data...")
    
    # Check if fuel data already exists
    if Fuel.query.count() > 0:
        print("⚠️ Fuel data already exists. Skipping seed.")
        return
    
    # Create fuel types
    fuels = [
        Fuel(
            name="Petrol",
            description="Premium unleaded petrol for cars and motorcycles",
            price_per_liter=102.50,
            is_available=True
        ),
        Fuel(
            name="Diesel",
            description="High-speed diesel for cars, trucks and heavy vehicles",
            price_per_liter=89.75,
            is_available=True
        ),
        Fuel(
            name="CNG",
            description="Compressed Natural Gas - eco-friendly fuel option",
            price_per_liter=75.20,
            is_available=True
        )
    ]
    
    # Add fuels to database
    for fuel in fuels:
        db.session.add(fuel)
    
    db.session.commit()
    print("✅ Fuel data seeded successfully!")

def seed_test_users():
    """Create test users for development"""
    print("Creating test users...")
    
    # Check if users already exist
    if User.query.count() > 0:
        print("⚠️ Users already exist. Skipping test user creation.")
        return
    
    # Create test users
    users = [
        User(
            name="John Doe",
            email="john@example.com",
            phone="+91-9876543210",
            password="password123"
        ),
        User(
            name="Jane Smith",
            email="jane@example.com", 
            phone="+91-9876543211",
            password="password123"
        )
    ]
    
    # Add users to database
    for user in users:
        db.session.add(user)
    
    db.session.commit()
    print("✅ Test users created successfully!")
    print("📧 Login credentials:")
    print("   Email: john@example.com | Password: password123")
    print("   Email: jane@example.com | Password: password123")

def seed_test_addresses():
    """Create test addresses for test users"""
    print("Creating test addresses...")
    
    # Get test users
    john = User.query.filter_by(email="john@example.com").first()
    jane = User.query.filter_by(email="jane@example.com").first()
    
    if not john or not jane:
        print("⚠️ Test users not found. Skipping address creation.")
        return
    
    # Check if addresses already exist
    if Address.query.count() > 0:
        print("⚠️ Addresses already exist. Skipping test address creation.")
        return
    
    # Create test addresses
    addresses = [
        # John's addresses
        Address(
            user_id=john.id,
            name="Home",
            address_line1="123 Main Street",
            address_line2="Apartment 4B",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            phone="+91-9876543210",
            is_default=True
        ),
        Address(
            user_id=john.id,
            name="Office",
            address_line1="456 Business Park",
            address_line2="Floor 5, Wing A",
            city="Pune",
            state="Maharashtra",
            pincode="411014",
            phone="+91-9876543210",
            is_default=False
        ),
        # Jane's addresses
        Address(
            user_id=jane.id,
            name="Home",
            address_line1="789 Garden Lane",
            city="Pune",
            state="Maharashtra", 
            pincode="411038",
            phone="+91-9876543211",
            is_default=True
        )
    ]
    
    # Add addresses to database
    for address in addresses:
        db.session.add(address)
    
    db.session.commit()
    print("✅ Test addresses created successfully!")

def main():
    """Main function to run all migrations"""
    print("🚀 Starting FuelExpress Database Migration...")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Step 1: Create tables
            create_tables()
            
            # Step 2: Seed fuel data
            seed_fuel_data()
            
            # Step 3: Create test users
            seed_test_users()
            
            # Step 4: Create test addresses
            seed_test_addresses()
            
            print("\n" + "=" * 50)
            print("🎉 Database migration completed successfully!")
            print("=" * 50)
            print("\n📊 Database Summary:")
            print(f"   • Users: {User.query.count()}")
            print(f"   • Fuel Types: {Fuel.query.count()}")
            print(f"   • Addresses: {Address.query.count()}")
            print(f"   • Orders: {Order.query.count()}")
            
            print("\n🌐 You can now start your Flask application:")
            print("   python run.py")
            
            print("\n🔐 Test Login Credentials:")
            print("   Email: john@example.com")
            print("   Password: password123")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())