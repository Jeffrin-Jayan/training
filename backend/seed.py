import os
import json
from werkzeug.security import generate_password_hash
from database import db, User, UserProfile, Scheme, SchemeEligibilityRule, SchemeDocument, OfficeLocation
from datetime import datetime

def seed_database(app):
    with app.app_context():
        # Check if database is already seeded
        if User.query.first() is not None:
            print("Database already seeded.")
            return
            
        print("Seeding database...")
        
        # 1. Users & Profiles
        admin_pass = generate_password_hash("admin123")
        user_pass = generate_password_hash("user123")
        
        admin = User(email="admin@govassist.in", password_hash=admin_pass, role="admin")
        user = User(email="citizen@govassist.in", password_hash=user_pass, role="user")
        
        db.session.add(admin)
        db.session.add(user)
        db.session.flush() # Get IDs
        
        profile = UserProfile(
            user_id=user.id,
            full_name="Rajesh Kumar",
            age=34,
            gender="Male",
            occupation="Farmer",
            annual_income=75000.0,
            state="Kerala",
            district="Palakkad",
            education="Secondary School",
            is_student=False,
            is_farmer=True,
            is_entrepreneur=False,
            has_disability=False,
            is_widow=False,
            is_senior_citizen=False
        )
        db.session.add(profile)
        
        # 2. Schemes & Rules & Documents
        schemes_data = [
            {
                "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
                "description": "An initiative by the government of India that provides up to Rs 6,000 per year in three equal installments to all small and marginal farmers.",
                "benefits": "Financial benefit of Rs. 6000 per annum per family payable in three equal installments of Rs. 2000 each, every four months.",
                "category": "Agriculture",
                "ministry": "Ministry of Agriculture and Farmers Welfare",
                "state": "Central",
                "application_url": "https://pmkisan.gov.in/",
                "rules": {
                    "min_age": 18,
                    "max_age": 100,
                    "max_income": 300000.0,
                    "allowed_genders": "Male,Female,Other",
                    "allowed_occupations": "Farmer",
                    "allowed_states": "Central",
                    "requires_disability": False,
                    "requires_widow": False,
                    "requires_student": False,
                    "requires_farmer": True
                },
                "documents": [
                    {"name": "Aadhaar Card", "is_mandatory": True, "description": "Identity proof"},
                    {"name": "Land Holding Documents", "is_mandatory": True, "description": "Proof of agricultural land"},
                    {"name": "Bank Account Passbook", "is_mandatory": True, "description": "For direct benefit transfer"}
                ]
            },
            {
                "name": "Post-Matric Scholarship Scheme",
                "description": "Financial assistance to students belonging to Scheduled Castes, Scheduled Tribes, and low-income families to pursue post-matric or post-secondary courses.",
                "benefits": "Full tuition fee reimbursement and a monthly maintenance allowance ranging from Rs. 300 to Rs. 1200 depending on the course group.",
                "category": "Education",
                "ministry": "Ministry of Social Justice and Empowerment",
                "state": "Central",
                "application_url": "https://scholarships.gov.in/",
                "rules": {
                    "min_age": 15,
                    "max_age": 30,
                    "max_income": 250000.0,
                    "allowed_genders": "Male,Female,Other",
                    "allowed_occupations": "Student,None",
                    "allowed_states": "Central",
                    "requires_disability": False,
                    "requires_widow": False,
                    "requires_student": True,
                    "requires_farmer": False
                },
                "documents": [
                    {"name": "Aadhaar Card", "is_mandatory": True, "description": "Identity proof"},
                    {"name": "Income Certificate", "is_mandatory": True, "description": "Annual household income verification"},
                    {"name": "Caste Certificate", "is_mandatory": False, "description": "If applying under SC/ST category"},
                    {"name": "Previous Marksheet", "is_mandatory": True, "description": "Proof of qualifying exam"}
                ]
            },
            {
                "name": "Stand-Up India Scheme",
                "description": "Promotes entrepreneurship among women and SC/ST communities by providing bank loans between Rs. 10 Lakhs and Rs. 1 Crore for starting greenfield enterprises.",
                "benefits": "Composite loan (inclusive of term loan and working capital) between Rs. 10 Lakh and Rs. 100 Lakh.",
                "category": "Business",
                "ministry": "Ministry of Finance",
                "state": "Central",
                "application_url": "https://www.standupmitra.in/",
                "rules": {
                    "min_age": 18,
                    "max_age": 70,
                    "max_income": 99999999.0,
                    "allowed_genders": "Female",
                    "allowed_occupations": "Entrepreneur,Business Owner,Unemployed",
                    "allowed_states": "Central",
                    "requires_disability": False,
                    "requires_widow": False,
                    "requires_student": False,
                    "requires_farmer": False
                },
                "documents": [
                    {"name": "Aadhaar Card", "is_mandatory": True, "description": "Identity proof"},
                    {"name": "PAN Card", "is_mandatory": True, "description": "Tax ID"},
                    {"name": "Project Report", "is_mandatory": True, "description": "Business proposal and greenfield project details"},
                    {"name": "Partnership Deed / Incorporation Certificate", "is_mandatory": False, "description": "For business entity"}
                ]
            },
            {
                "name": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
                "description": "A non-contributing pension scheme providing financial assistance to senior citizens belonging to below poverty line (BPL) households.",
                "benefits": "Monthly pension of Rs. 200 for ages 60-79, and Rs. 500 for age 80 and above, supplemented by state contributions.",
                "category": "Social Welfare",
                "ministry": "Ministry of Rural Development",
                "state": "Central",
                "application_url": "https://nsap.nic.in/",
                "rules": {
                    "min_age": 60,
                    "max_age": 120,
                    "max_income": 120000.0,
                    "allowed_genders": "Male,Female,Other",
                    "allowed_occupations": "None,Retired,Unemployed",
                    "allowed_states": "Central",
                    "requires_disability": False,
                    "requires_widow": False,
                    "requires_student": False,
                    "requires_farmer": False
                },
                "documents": [
                    {"name": "Aadhaar Card", "is_mandatory": True, "description": "Identity proof"},
                    {"name": "BPL Ration Card", "is_mandatory": True, "description": "Proof of BPL category status"},
                    {"name": "Age Proof Certificate", "is_mandatory": True, "description": "Birth certificate or school leaving certificate"},
                    {"name": "Bank Passbook Details", "is_mandatory": True, "description": "For direct pension transfers"}
                ]
            },
            {
                "name": "Pradhan Mantri Awas Yojana - Gramin (PMAY-G)",
                "description": "Social welfare program to provide clean and affordable housing for rural poor families.",
                "benefits": "Financial assistance of Rs. 1.20 Lakh in plain areas and Rs. 1.30 Lakh in hilly/difficult areas for constructing a house.",
                "category": "Social Welfare",
                "ministry": "Ministry of Rural Development",
                "state": "Central",
                "application_url": "https://pmayg.nic.in/",
                "rules": {
                    "min_age": 18,
                    "max_age": 90,
                    "max_income": 180000.0,
                    "allowed_genders": "Male,Female,Other",
                    "allowed_occupations": "Unemployed,Farmer,Laborer",
                    "allowed_states": "Central",
                    "requires_disability": False,
                    "requires_widow": False,
                    "requires_student": False,
                    "requires_farmer": False
                },
                "documents": [
                    {"name": "Aadhaar Card", "is_mandatory": True, "description": "Identity proof"},
                    {"name": "Job Card under MGNREGA", "is_mandatory": True, "description": "Active job card"},
                    {"name": "Certificate of Land ownership", "is_mandatory": True, "description": "Proof that you own the building land"},
                    {"name": "Income Certificate", "is_mandatory": True, "description": "Income verification document"}
                ]
            }
        ]
        
        for scheme_item in schemes_data:
            s = Scheme(
                name=scheme_item["name"],
                description=scheme_item["description"],
                benefits=scheme_item["benefits"],
                category=scheme_item["category"],
                ministry=scheme_item["ministry"],
                state=scheme_item["state"],
                application_url=scheme_item["application_url"]
            )
            db.session.add(s)
            db.session.flush() # Resolve scheme ID
            
            # Rules
            r_data = scheme_item["rules"]
            r = SchemeEligibilityRule(
                scheme_id=s.id,
                min_age=r_data["min_age"],
                max_age=r_data["max_age"],
                max_income=r_data["max_income"],
                allowed_genders=r_data["allowed_genders"],
                allowed_occupations=r_data["allowed_occupations"],
                allowed_states=r_data["allowed_states"],
                requires_disability=r_data["requires_disability"],
                requires_widow=r_data["requires_widow"],
                requires_student=r_data["requires_student"],
                requires_farmer=r_data["requires_farmer"]
            )
            db.session.add(r)
            
            # Docs
            for doc in scheme_item["documents"]:
                d = SchemeDocument(
                    scheme_id=s.id,
                    document_name=doc["name"],
                    is_mandatory=doc["is_mandatory"],
                    description=doc["description"]
                )
                db.session.add(d)
                
        # 3. Office Locations
        offices_data = [
            {"name": "Pattambi Village Office", "office_type": "Village Office", "district": "Palakkad", "state": "Kerala", "lat": 10.8066, "lon": 76.1915},
            {"name": "Palakkad Collectorate", "office_type": "Collectorate", "district": "Palakkad", "state": "Kerala", "lat": 10.7867, "lon": 76.6548},
            {"name": "Akshaya Centre - Palakkad Town", "office_type": "Akshaya Centre", "district": "Palakkad", "state": "Kerala", "lat": 10.7788, "lon": 76.6534},
            {"name": "Ernakulam Passport Seva Kendra", "office_type": "Passport Office", "district": "Ernakulam", "state": "Kerala", "lat": 9.9723, "lon": 76.2798},
            {"name": "Vyttila RTO Office", "office_type": "RTO", "district": "Ernakulam", "state": "Kerala", "lat": 9.9678, "lon": 76.3218},
            {"name": "Thiruvananthapuram Secretariat", "office_type": "Panchayat", "district": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5015, "lon": 76.9515}
        ]
        
        for office in offices_data:
            o = OfficeLocation(
                name=office["name"],
                office_type=office["office_type"],
                district=office["district"],
                state=office["state"],
                latitude=office["lat"],
                longitude=office["lon"]
            )
            db.session.add(o)
            
        db.session.commit()
        print("Database seeded successfully.")
