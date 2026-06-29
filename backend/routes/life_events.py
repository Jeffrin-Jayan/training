from flask import Blueprint, request, jsonify
from database import db, Scheme, SchemeEligibilityRule, SchemeDocument

life_events_bp = Blueprint('life_events', __name__)

# Comprehensive life event definitions with related services and schemes
LIFE_EVENTS = {
    "birth_of_child": {
        "title": "Birth of a Child",
        "icon": "👶",
        "description": "Welcoming a new member to the family comes with government support for maternal health, child welfare, and financial assistance.",
        "related_categories": ["Social Welfare", "Health"],
        "keywords": ["child", "birth", "maternity", "maternal", "newborn", "baby"],
        "services": [
            {"name": "Birth Certificate Registration", "department": "Municipal Corporation / Panchayat", "deadline": "Within 21 days of birth", "documents": ["Hospital Discharge Summary", "Parent Aadhaar Cards", "Marriage Certificate"]},
            {"name": "Aadhaar Enrolment for Child", "department": "UIDAI / Aadhaar Centre", "deadline": "Any time after birth", "documents": ["Birth Certificate", "Parent Aadhaar Card"]},
            {"name": "Child Immunization Registration", "department": "Primary Health Centre", "deadline": "Immediately after birth", "documents": ["Birth Certificate", "Parent ID Proof"]},
            {"name": "Ration Card Update (Add member)", "department": "Civil Supplies Department", "deadline": "Within 3 months", "documents": ["Birth Certificate", "Existing Ration Card", "Aadhaar of Parents"]}
        ],
        "tips": [
            "Register the birth within 21 days to avoid penalties.",
            "Get Aadhaar enrolment done early for the child — it's needed for many scheme benefits.",
            "Ensure the mother's bank account is linked to Aadhaar for Direct Benefit Transfers."
        ]
    },
    "marriage": {
        "title": "Marriage",
        "icon": "💍",
        "description": "Marriage is a significant life milestone. Government offers housing, loan, and welfare support for newly married couples.",
        "related_categories": ["Social Welfare", "Housing"],
        "keywords": ["marriage", "wedding", "spouse", "married"],
        "services": [
            {"name": "Marriage Certificate Registration", "department": "Sub-Registrar Office", "deadline": "Within 30 days of marriage", "documents": ["Marriage Invitation / Photos", "Aadhaar of Both Parties", "Age Proof", "Address Proof", "Two Witnesses with ID"]},
            {"name": "Name Change in Aadhaar / PAN / Passport", "department": "UIDAI / Income Tax / Passport Seva Kendra", "deadline": "As soon as possible", "documents": ["Marriage Certificate", "Current ID Proofs"]},
            {"name": "Joint Bank Account Opening", "department": "Any Bank Branch", "deadline": "Any time", "documents": ["Marriage Certificate", "Aadhaar", "PAN Card"]}
        ],
        "tips": [
            "Marriage registration is mandatory and useful for passport, visa, and insurance claims.",
            "Update your name and address across government IDs after marriage to avoid issues.",
            "Apply for joint housing schemes (PMAY) if eligible after marriage."
        ]
    },
    "graduation": {
        "title": "Graduation / Higher Education",
        "icon": "🎓",
        "description": "Completing education opens doors to scholarships, skill programs, and career-building government support.",
        "related_categories": ["Education"],
        "keywords": ["graduation", "degree", "education", "university", "college", "higher education", "scholarship"],
        "services": [
            {"name": "Skill India Registration", "department": "Ministry of Skill Development", "deadline": "Open enrollment", "documents": ["Degree Certificate", "Aadhaar", "Resume"]},
            {"name": "Employment Exchange Registration", "department": "District Employment Office", "deadline": "Within 1 year of graduation", "documents": ["Degree Certificate", "Aadhaar", "Passport Photos"]},
            {"name": "Education Loan Interest Subsidy", "department": "Central Government via Bank", "deadline": "During course period", "documents": ["Admission Letter", "Fee Receipt", "Income Certificate"]}
        ],
        "tips": [
            "Register on the National Career Service (NCS) portal for job opportunities.",
            "Apply for post-graduation scholarships if continuing studies.",
            "Check state-specific study abroad scholarship schemes."
        ]
    },
    "first_job": {
        "title": "First Job / Employment",
        "icon": "💼",
        "description": "Starting your career involves PF registration, tax filing, and access to employment-linked government benefits.",
        "related_categories": ["Employment", "Business"],
        "keywords": ["job", "employment", "first job", "career", "salary", "work"],
        "services": [
            {"name": "PAN Card Application", "department": "Income Tax Department / NSDL", "deadline": "Before first salary", "documents": ["Aadhaar Card", "Address Proof", "Passport Photo"]},
            {"name": "EPF / UAN Registration", "department": "EPFO (via employer)", "deadline": "At joining", "documents": ["Aadhaar", "PAN Card", "Bank Account Details"]},
            {"name": "Income Tax e-Filing Registration", "department": "Income Tax Department", "deadline": "Before July 31 of first FY", "documents": ["PAN Card", "Bank Account", "Form 16 from Employer"]}
        ],
        "tips": [
            "Ensure your employer registers you under EPF/ESI from day one.",
            "File income tax returns even if income is below taxable limit for loan and visa purposes.",
            "Activate your UAN and link it with Aadhaar for seamless PF withdrawals."
        ]
    },
    "job_loss": {
        "title": "Job Loss / Unemployment",
        "icon": "📉",
        "description": "Losing a job can be challenging. Government provides unemployment assistance, retraining, and social security benefits.",
        "related_categories": ["Social Welfare", "Employment"],
        "keywords": ["job loss", "unemployed", "retrenchment", "layoff", "termination"],
        "services": [
            {"name": "Atal Bimit Vyakti Kalyan Yojana (ESIC)", "department": "ESIC", "deadline": "Within 30 days of unemployment", "documents": ["ESIC Card", "Termination Letter", "Bank Account", "Aadhaar"]},
            {"name": "Employment Exchange Re-registration", "department": "District Employment Office", "deadline": "Immediately", "documents": ["Previous Registration", "Last Salary Slip", "Aadhaar"]},
            {"name": "Skill Reskilling Programs", "department": "Skill India / State Skill Mission", "deadline": "Open enrollment", "documents": ["Aadhaar", "Education Certificates"]}
        ],
        "tips": [
            "Withdraw PF only partially — keep EPF intact for long-term retirement benefit.",
            "Register at the employment exchange immediately to access state unemployment benefits.",
            "Explore PMEGP for starting your own micro-enterprise during the transition."
        ]
    },
    "starting_business": {
        "title": "Starting a Business",
        "icon": "🚀",
        "description": "Entrepreneurs can access government loans, subsidies, tax benefits, and startup registration support.",
        "related_categories": ["Business"],
        "keywords": ["business", "startup", "entrepreneur", "enterprise", "company", "self-employed"],
        "services": [
            {"name": "Udyam Registration (MSME)", "department": "Ministry of MSME", "deadline": "Before availing MSME benefits", "documents": ["Aadhaar", "PAN Card", "Business Details"]},
            {"name": "GST Registration", "department": "GST Portal", "deadline": "If turnover > ₹20 Lakhs (₹10L for NE states)", "documents": ["PAN Card", "Aadhaar", "Business Address Proof", "Bank Statement"]},
            {"name": "Startup India Registration (DPIIT)", "department": "DPIIT / Startup India Portal", "deadline": "Within 10 years of incorporation", "documents": ["Certificate of Incorporation", "Business Plan", "PAN", "Aadhaar"]},
            {"name": "Trade License", "department": "Municipal Corporation", "deadline": "Before commencing business", "documents": ["Business Address Proof", "NOC from Fire Dept", "Identity Proof"]}
        ],
        "tips": [
            "Register under Udyam for credit access, subsidies, and tax benefits.",
            "DPIIT recognition gives you 3-year tax holiday and easier compliance.",
            "Explore MUDRA loans (up to ₹10 Lakhs) for micro-enterprises without collateral."
        ]
    },
    "building_house": {
        "title": "Building a House",
        "icon": "🏠",
        "description": "Building or buying your first house? Government offers housing subsidies, interest rate concessions, and construction support.",
        "related_categories": ["Housing", "Social Welfare"],
        "keywords": ["house", "home", "construction", "building", "housing", "property"],
        "services": [
            {"name": "PMAY Application (Pradhan Mantri Awas Yojana)", "department": "Ministry of Housing / Urban Local Body", "deadline": "Open enrollment (income-based)", "documents": ["Aadhaar", "Income Certificate", "Land Documents", "Bank Account"]},
            {"name": "Building Permission / Plan Approval", "department": "Municipal Corporation / Panchayat", "deadline": "Before construction begins", "documents": ["Land Title Deed", "Approved Building Plan", "NOC from Neighbors"]},
            {"name": "Home Loan Subsidy (CLSS)", "department": "NHB via participating banks", "deadline": "At time of loan application", "documents": ["Income Proof", "Property Documents", "Aadhaar", "PAN"]}
        ],
        "tips": [
            "PMAY-Gramin provides ₹1.20 Lakh (plain areas) or ₹1.30 Lakh (hilly areas) for construction.",
            "CLSS offers up to ₹2.67 Lakh interest subsidy for EWS/LIG categories under PMAY-Urban.",
            "Always get building plan approved before construction to avoid demolition notices."
        ]
    },
    "buying_land": {
        "title": "Buying Land / Property",
        "icon": "🏗️",
        "description": "Land purchase involves registration, mutation, and legal documentation. Government services help ensure clean titles.",
        "related_categories": ["Housing"],
        "keywords": ["land", "property", "plot", "purchase", "registration", "real estate"],
        "services": [
            {"name": "Property Registration (Sale Deed)", "department": "Sub-Registrar Office", "deadline": "Within 4 months of sale agreement", "documents": ["Sale Deed", "Seller & Buyer Aadhaar + PAN", "Encumbrance Certificate", "Stamp Duty Payment Receipt"]},
            {"name": "Land Mutation / Patta Transfer", "department": "Revenue Department / Taluk Office", "deadline": "After registration", "documents": ["Registered Sale Deed", "Tax Receipts", "Aadhaar"]},
            {"name": "Encumbrance Certificate (EC)", "department": "Sub-Registrar Office", "deadline": "Before purchase", "documents": ["Property Survey Number", "Application Form"]}
        ],
        "tips": [
            "Always obtain an Encumbrance Certificate (EC) for last 30 years before buying.",
            "Verify property on state land records portal (e.g., ROR / 7/12 extract).",
            "Pay stamp duty and registration fees before the deadline to avoid penalties."
        ]
    },
    "retirement": {
        "title": "Retirement",
        "icon": "🏖️",
        "description": "Retirement brings pension claims, health insurance changes, and senior citizen benefits from the government.",
        "related_categories": ["Social Welfare"],
        "keywords": ["retirement", "pension", "senior citizen", "old age", "retired"],
        "services": [
            {"name": "Pension Application (EPF / NPS)", "department": "EPFO / NPS Trust", "deadline": "Around retirement date", "documents": ["Aadhaar", "PAN", "Bank Account", "Service Proof", "PPO (if applicable)"]},
            {"name": "Senior Citizen Health Insurance (PMJAY / SCHIS)", "department": "Ayushman Bharat / State Health Dept", "deadline": "After turning 60", "documents": ["Age Proof", "Aadhaar", "Income Certificate (if needed)"]},
            {"name": "Senior Citizen Savings Scheme (SCSS)", "department": "Post Office / Bank", "deadline": "Within 1 month of receiving retirement benefits", "documents": ["Retirement Proof", "Age Proof", "Aadhaar", "PAN"]}
        ],
        "tips": [
            "Apply for IGNOAPS if you belong to BPL category — monthly pension of ₹200-500.",
            "SCSS offers 8%+ interest rates and tax benefits under Section 80C.",
            "Get a Senior Citizen card for travel discounts on railways and airlines."
        ]
    },
    "death_in_family": {
        "title": "Death Certificate & Survivor Benefits",
        "icon": "🕯️",
        "description": "After the loss of a family member, government helps with death registration, insurance claims, and survivor benefits.",
        "related_categories": ["Social Welfare"],
        "keywords": ["death", "death certificate", "survivor", "widow", "bereaved", "funeral"],
        "services": [
            {"name": "Death Certificate Registration", "department": "Municipal Corporation / Panchayat", "deadline": "Within 21 days of death", "documents": ["Hospital Death Summary (if applicable)", "Deceased's Aadhaar", "Informant's Aadhaar"]},
            {"name": "Insurance / Pension Claim Settlement", "department": "LIC / Bank / Employer", "deadline": "Within 6 months", "documents": ["Death Certificate", "Nominee Aadhaar", "Policy Documents", "Bank Account"]},
            {"name": "Succession / Legal Heir Certificate", "department": "Taluk / Revenue Office / Court", "deadline": "As needed", "documents": ["Death Certificate", "Ration Card", "Family Details Affidavit", "Applicant Aadhaar"]},
            {"name": "Widow Pension Application", "department": "Social Welfare Department", "deadline": "As soon as possible", "documents": ["Death Certificate of Spouse", "Marriage Certificate", "Aadhaar", "Income Certificate", "Bank Account"]}
        ],
        "tips": [
            "Register death within 21 days to avoid penalties and court procedures.",
            "Apply for succession certificate early to access bank accounts and property.",
            "Widow pension (IGNWPS) provides ₹300/month for BPL widows aged 40-79."
        ]
    }
}


@life_events_bp.route('/list', methods=['GET'])
def list_life_events():
    """Returns all supported life events with metadata."""
    events = []
    for key, event in LIFE_EVENTS.items():
        events.append({
            "id": key,
            "title": event["title"],
            "icon": event["icon"],
            "description": event["description"]
        })
    return jsonify(events), 200


@life_events_bp.route('/details/<event_id>', methods=['GET'])
def get_event_details(event_id):
    """Get full details for a specific life event including matched schemes."""
    if event_id not in LIFE_EVENTS:
        return jsonify({"error": "Life event not found"}), 404

    event = LIFE_EVENTS[event_id]

    # Find matching schemes from database by category keywords
    matched_schemes = []
    all_schemes = Scheme.query.all()
    for s in all_schemes:
        score = 0
        # Match by category
        if s.category in event.get("related_categories", []):
            score += 50
        # Match by keywords in description/name
        for kw in event.get("keywords", []):
            if kw.lower() in s.name.lower() or kw.lower() in s.description.lower():
                score += 10
        if score > 0:
            docs = [{"name": d.document_name, "mandatory": d.is_mandatory, "desc": d.description} for d in s.documents]
            matched_schemes.append({
                "scheme_id": s.id,
                "name": s.name,
                "description": s.description,
                "benefits": s.benefits,
                "category": s.category,
                "relevance_score": min(score, 100),
                "documents": docs
            })

    matched_schemes.sort(key=lambda x: x["relevance_score"], reverse=True)

    return jsonify({
        "id": event_id,
        "title": event["title"],
        "icon": event["icon"],
        "description": event["description"],
        "services": event["services"],
        "tips": event["tips"],
        "matched_schemes": matched_schemes
    }), 200


@life_events_bp.route('/recommend', methods=['POST'])
def recommend_by_event():
    """Given a life event and user profile, return tailored recommendations."""
    data = request.get_json() or {}
    event_id = data.get('event_id')
    user_age = data.get('age', 25)
    user_gender = data.get('gender', 'Male')
    user_state = data.get('state', 'Central')

    if event_id not in LIFE_EVENTS:
        return jsonify({"error": "Invalid life event ID"}), 400

    event = LIFE_EVENTS[event_id]

    # Build personalized response
    return jsonify({
        "event": event["title"],
        "personalized_message": f"Based on your profile (Age: {user_age}, Gender: {user_gender}, State: {user_state}), "
                                f"here are the services and schemes relevant to '{event['title']}'.",
        "services": event["services"],
        "tips": event["tips"]
    }), 200
