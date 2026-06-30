from flask import Blueprint, request, jsonify
from database import db, Scheme, SchemeEligibilityRule, SchemeDocument, Bookmark, UserProfile
from sqlalchemy import or_

schemes_bp = Blueprint('schemes', __name__)

def evaluate_eligibility(profile, rule):
    """Calculates compatibility confidence score and details."""
    reasons = []
    total_checks = 0
    passed_checks = 0
    
    # 1. Age
    if rule.min_age is not None or rule.max_age is not None:
        total_checks += 1
        age = profile.age or 0
        min_a = rule.min_age or 0
        max_a = rule.max_age or 150
        if min_a <= age <= max_a:
            passed_checks += 1
        else:
            reasons.append(f"Age is {age}, but scheme requires between {min_a} and {max_a} years.")

    # 2. Income
    if rule.max_income is not None:
        total_checks += 1
        income = profile.annual_income or 0.0
        if income <= rule.max_income:
            passed_checks += 1
        else:
            reasons.append(f"Annual income is ₹{income:,.2f}, which exceeds the limit of ₹{rule.max_income:,.2f}.")

    # 3. Gender
    if rule.allowed_genders:
        total_checks += 1
        allowed = [g.strip().lower() for g in rule.allowed_genders.split(',')]
        gender = (profile.gender or '').strip().lower()
        if gender in allowed:
            passed_checks += 1
        else:
            reasons.append(f"Gender is '{profile.gender}', but scheme is limited to: {rule.allowed_genders}.")

    # 4. State
    if rule.allowed_states and rule.allowed_states.lower() != 'central':
        total_checks += 1
        allowed = [s.strip().lower() for s in rule.allowed_states.split(',')]
        state = (profile.state or '').strip().lower()
        if state in allowed or 'central' in allowed:
            passed_checks += 1
        else:
            reasons.append(f"State is '{profile.state}', but scheme is for residents of: {rule.allowed_states}.")

    # 5. Farmer status
    if rule.requires_farmer:
        total_checks += 1
        if profile.is_farmer:
            passed_checks += 1
        else:
            reasons.append("Scheme is reserved exclusively for Farmers.")

    # 6. Student status
    if rule.requires_student:
        total_checks += 1
        if profile.is_student:
            passed_checks += 1
        else:
            reasons.append("Scheme is reserved exclusively for Students.")

    # 7. Entrepreneur status
    if rule.requires_entrepreneur:
        total_checks += 1
        if profile.is_entrepreneur:
            passed_checks += 1
        else:
            reasons.append("Scheme is reserved for Entrepreneurs / Greenfield startups.")

    # 8. Disability status
    if rule.requires_disability:
        total_checks += 1
        if profile.has_disability:
            passed_checks += 1
        else:
            reasons.append("Scheme requires Persons with Disabilities (PwD) criteria.")

    # 9. Widow status
    if rule.requires_widow:
        total_checks += 1
        if profile.is_widow:
            passed_checks += 1
        else:
            reasons.append("Scheme is reserved for widows.")

    # 10. Occupation
    if rule.allowed_occupations:
        total_checks += 1
        allowed_occs = [o.strip().lower() for o in rule.allowed_occupations.split(',')]
        occ = (profile.occupation or '').strip().lower()
        if occ in allowed_occs or 'any' in allowed_occs or not occ:
            passed_checks += 1
        else:
            reasons.append(f"Occupation is '{profile.occupation}', but scheme allows: {rule.allowed_occupations}.")

    confidence_score = int((passed_checks / total_checks) * 100) if total_checks > 0 else 100
    is_eligible = len(reasons) == 0
    
    return is_eligible, confidence_score, reasons

@schemes_bp.route('/recommend', methods=['POST'])
def recommend_schemes():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
        
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"error": "User profile not found"}), 404
        
    schemes = Scheme.query.all()
    recommendations = []
    
    for s in schemes:
        if s.eligibility_rules:
            is_eligible, confidence_score, reasons = evaluate_eligibility(profile, s.eligibility_rules)
            
            # Fetch required docs
            docs = [{"name": d.document_name, "mandatory": d.is_mandatory, "desc": d.description} for d in s.documents]
            
            recommendations.append({
                "scheme_id": s.id,
                "name": s.name,
                "description": s.description,
                "benefits": s.benefits,
                "category": s.category,
                "ministry": s.ministry,
                "state": s.state,
                "application_url": s.application_url,
                "is_eligible": is_eligible,
                "confidence_score": confidence_score,
                "reasons": reasons,
                "documents": docs
            })
            
    # Sort recommendations by confidence score (descending)
    recommendations.sort(key=lambda x: x["confidence_score"], reverse=True)
    return jsonify(recommendations), 200

@schemes_bp.route('/check_eligibility', methods=['POST'])
def check_eligibility():
    data = request.get_json() or {}
    scheme_id = data.get('scheme_id')
    
    if not scheme_id:
        return jsonify({"error": "Scheme ID is required"}), 400
        
    scheme = Scheme.query.get(scheme_id)
    if not scheme or not scheme.eligibility_rules:
        return jsonify({"error": "Scheme eligibility rules not found"}), 404
        
    # Build temporary UserProfile from data
    temp_profile = UserProfile(
        age=int(data.get('age', 18)),
        gender=data.get('gender', 'Male'),
        occupation=data.get('occupation', 'None'),
        annual_income=float(data.get('annual_income', 0.0)),
        state=data.get('state', 'Central'),
        is_student=bool(data.get('is_student', False)),
        is_farmer=bool(data.get('is_farmer', False)),
        is_entrepreneur=bool(data.get('is_entrepreneur', False)),
        has_disability=bool(data.get('has_disability', False)),
        is_widow=bool(data.get('is_widow', False)),
        is_senior_citizen=int(data.get('age', 18)) >= 60
    )
    
    is_eligible, confidence_score, reasons = evaluate_eligibility(temp_profile, scheme.eligibility_rules)
    
    # Suggest alternatives if not eligible
    alternatives = []
    if not is_eligible:
        other_schemes = Scheme.query.filter(Scheme.id != scheme_id).all()
        for os in other_schemes:
            if os.eligibility_rules:
                ok, score, _ = evaluate_eligibility(temp_profile, os.eligibility_rules)
                if ok:
                    alternatives.append({"scheme_id": os.id, "name": os.name, "category": os.category})
                    
    return jsonify({
        "scheme_name": scheme.name,
        "is_eligible": is_eligible,
        "confidence_score": confidence_score,
        "reasons": reasons,
        "alternatives": alternatives[:3]
    }), 200

@schemes_bp.route('/search', methods=['GET'])
def search_schemes():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    state = request.args.get('state', '')
    
    stmt = Scheme.query
    if query:
        stmt = stmt.filter(or_(
            Scheme.name.like(f'%{query}%'),
            Scheme.description.like(f'%{query}%'),
            Scheme.category.like(f'%{query}%')
        ))
    if category:
        stmt = stmt.filter(Scheme.category == category)
    if state:
        stmt = stmt.filter(Scheme.state == state)
        
    results = stmt.all()
    output = []
    for s in results:
        docs = [{"name": d.document_name, "mandatory": d.is_mandatory} for d in s.documents]
        rules_dict = {}
        if s.eligibility_rules:
            rules_dict = {
                "min_age": s.eligibility_rules.min_age,
                "max_age": s.eligibility_rules.max_age,
                "max_income": s.eligibility_rules.max_income,
                "allowed_genders": s.eligibility_rules.allowed_genders,
                "allowed_occupations": s.eligibility_rules.allowed_occupations,
                "allowed_states": s.eligibility_rules.allowed_states,
                "requires_disability": s.eligibility_rules.requires_disability,
                "requires_widow": s.eligibility_rules.requires_widow,
                "requires_student": s.eligibility_rules.requires_student,
                "requires_farmer": s.eligibility_rules.requires_farmer,
                "requires_entrepreneur": s.eligibility_rules.requires_entrepreneur,
            }
        output.append({
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "benefits": s.benefits,
            "category": s.category,
            "ministry": s.ministry,
            "state": s.state,
            "application_url": s.application_url,
            "documents": docs,
            "rules": rules_dict
        })
    return jsonify(output), 200

@schemes_bp.route('/compare', methods=['POST'])
def compare_schemes():
    data = request.get_json() or {}
    id1 = data.get('scheme_id_1')
    id2 = data.get('scheme_id_2')
    
    if not id1 or not id2:
        return jsonify({"error": "Two scheme IDs are required"}), 400
        
    s1 = Scheme.query.get(id1)
    s2 = Scheme.query.get(id2)
    
    if not s1 or not s2:
        return jsonify({"error": "One or both schemes not found"}), 404
        
    def serialize_scheme_comp(s):
        r = s.eligibility_rules
        return {
            "name": s.name,
            "description": s.description,
            "benefits": s.benefits,
            "category": s.category,
            "ministry": s.ministry,
            "state": s.state,
            "eligibility": {
                "age_limit": f"{r.min_age or 0} to {r.max_age or 'No limit'}" if r else "None",
                "income_limit": f"Up to ₹{r.max_income:,.2f}" if r and r.max_income else "No limit",
                "allowed_genders": r.allowed_genders if r and r.allowed_genders else "All",
                "allowed_occupations": r.allowed_occupations if r and r.allowed_occupations else "All",
                "requires_farmer": r.requires_farmer if r else False,
                "requires_student": r.requires_student if r else False
            },
            "documents": [d.document_name for d in s.documents]
        }
        
    return jsonify({
        "scheme_1": serialize_scheme_comp(s1),
        "scheme_2": serialize_scheme_comp(s2)
    }), 200

@schemes_bp.route('/bookmark', methods=['POST'])
def bookmark_scheme():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    scheme_id = data.get('scheme_id')
    
    if not user_id or not scheme_id:
        return jsonify({"error": "User ID and Scheme ID are required"}), 400
        
    existing = Bookmark.query.filter_by(user_id=user_id, item_type='scheme', item_id=scheme_id).first()
    if existing:
        # Toggle: delete if exists
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"message": "Bookmark removed", "bookmarked": False}), 200
        
    new_bookmark = Bookmark(user_id=user_id, item_type='scheme', item_id=scheme_id)
    db.session.add(new_bookmark)
    db.session.commit()
    return jsonify({"message": "Bookmark added", "bookmarked": True}), 201

@schemes_bp.route('/bookmarks/<int:user_id>', methods=['GET'])
def get_bookmarks(user_id):
    bookmarks = Bookmark.query.filter_by(user_id=user_id, item_type='scheme').all()
    results = []
    for b in bookmarks:
        s = Scheme.query.get(b.item_id)
        if s:
            results.append({
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "description": s.description
            })
    return jsonify(results), 200


@schemes_bp.route('/checklist/<int:scheme_id>', methods=['GET'])
def document_checklist(scheme_id):
    """Returns categorized document checklist with validity tips."""
    scheme = Scheme.query.get(scheme_id)
    if not scheme:
        return jsonify({"error": "Scheme not found"}), 404

    docs = SchemeDocument.query.filter_by(scheme_id=scheme_id).all()

    required_docs = []
    optional_docs = []

    # Standard validity tips database
    validity_map = {
        "aadhaar card": "Lifetime validity. Update address if moved. Ensure mobile number is linked.",
        "pan card": "Lifetime validity. Must be linked with Aadhaar.",
        "income certificate": "Typically valid for 1 year from date of issue. Renew annually.",
        "caste certificate": "Lifetime validity once issued by competent authority.",
        "bank account passbook": "Must show recent transactions (within last 3 months). Ensure IFSC code is visible.",
        "land holding documents": "Must be current season RoR (Record of Rights). Verify with Tehsildar office.",
        "birth certificate": "Lifetime validity. Keep original safe for passport applications.",
        "age proof certificate": "Lifetime validity. School leaving certificate or birth certificate accepted.",
        "bpl ration card": "Renewed during NFSA surveys. Verify eligibility status annually.",
        "marksheet": "Lifetime validity. Attested copies accepted for most applications.",
        "project report": "Must be current. Include cost estimates, revenue projections, and employment plan.",
        "job card under mgnrega": "Must be active for current financial year. Renew at Gram Panchayat.",
        "passport": "Valid for 10 years (adults) / 5 years (minors). Renew 1 year before expiry.",
        "driving licence": "Valid for 20 years from date of issue or until age 50 (whichever is later).",
        "marriage certificate": "Lifetime validity. Essential for spouse-related benefit claims.",
        "disability certificate": "Permanent for 80%+ disability. Others need renewal as per medical board.",
        "domicile certificate": "Typically lifetime validity. Some states require renewal.",
        "voter id": "Lifetime validity. Update address when you relocate."
    }

    for d in docs:
        doc_name_lower = d.document_name.lower()
        validity_tip = validity_map.get(doc_name_lower, "Verify validity with the issuing authority before submission.")

        doc_entry = {
            "name": d.document_name,
            "description": d.description or "",
            "is_mandatory": d.is_mandatory,
            "validity_tip": validity_tip
        }

        if d.is_mandatory:
            required_docs.append(doc_entry)
        else:
            optional_docs.append(doc_entry)

    # Common missing documents advisory
    common_missing = []
    doc_names_lower = [d.document_name.lower() for d in docs]
    if "aadhaar card" not in doc_names_lower:
        common_missing.append({"name": "Aadhaar Card", "reason": "Most government schemes require Aadhaar for DBT verification."})
    if "bank account passbook" not in doc_names_lower and "bank passbook details" not in doc_names_lower:
        common_missing.append({"name": "Bank Account Passbook", "reason": "Needed for Direct Benefit Transfer (DBT) of scheme funds."})
    if "passport photo" not in doc_names_lower:
        common_missing.append({"name": "Recent Passport-size Photographs", "reason": "Typically required for physical applications and ID verification."})

    return jsonify({
        "scheme_name": scheme.name,
        "scheme_id": scheme.id,
        "required_documents": required_docs,
        "optional_documents": optional_docs,
        "commonly_missing": common_missing,
        "total_required": len(required_docs),
        "total_optional": len(optional_docs)
    }), 200


@schemes_bp.route('/application_guide/<int:scheme_id>', methods=['GET'])
def application_guide(scheme_id):
    """Returns step-by-step application guide with estimated times."""
    scheme = Scheme.query.get(scheme_id)
    if not scheme:
        return jsonify({"error": "Scheme not found"}), 404

    docs = SchemeDocument.query.filter_by(scheme_id=scheme_id, is_mandatory=True).all()
    doc_names = [d.document_name for d in docs]

    # Build application steps
    steps = [
        {
            "step_number": 1,
            "title": "Registration & Account Setup",
            "description": f"Visit the official portal ({scheme.application_url or 'scheme portal'}) and create an account. Use your Aadhaar-linked mobile number for OTP verification.",
            "estimated_time": "10-15 minutes",
            "tips": [
                "Use a valid email address you check regularly for updates.",
                "Save your registration ID / application reference number."
            ]
        },
        {
            "step_number": 2,
            "title": "Profile Verification & KYC",
            "description": "Complete your profile by providing personal details — name, date of birth, address, occupation, and family income. Some portals verify through Aadhaar eKYC.",
            "estimated_time": "10-20 minutes",
            "tips": [
                "Ensure your Aadhaar details match exactly (name spelling, DOB).",
                "If eKYC fails, you may need to visit a Common Service Centre (CSC)."
            ]
        },
        {
            "step_number": 3,
            "title": "Document Upload",
            "description": f"Upload scanned copies of the required documents: {', '.join(doc_names)}. Ensure files are clear, properly oriented, and under the size limit (usually 2MB per file).",
            "estimated_time": "15-30 minutes",
            "tips": [
                "Scan documents at 200-300 DPI for clarity.",
                "PDF format is preferred. JPEG is acceptable for photos and cards.",
                "Self-attest all copies before uploading."
            ]
        },
        {
            "step_number": 4,
            "title": "Payment of Fees (If Applicable)",
            "description": "Some schemes require nominal processing fees. Payment is usually via UPI, Net Banking, or Challan. Most central welfare schemes are FREE.",
            "estimated_time": "5-10 minutes",
            "tips": [
                "Save the payment receipt / transaction ID.",
                "If the scheme is free, this step will be skipped on the portal."
            ]
        },
        {
            "step_number": 5,
            "title": "Application Review & Submission",
            "description": "Review all filled details and uploaded documents carefully. Submit the application and note down the Application Reference Number (ARN).",
            "estimated_time": "5-10 minutes",
            "tips": [
                "Double-check spelling, income figures, and bank account numbers.",
                "Take a screenshot of the confirmation page."
            ]
        },
        {
            "step_number": 6,
            "title": "Verification & Approval",
            "description": "The concerned department will verify your application. This may involve field verification by a local officer (Block Development Officer / Gram Sevak).",
            "estimated_time": "7-45 days (varies by scheme and state)",
            "tips": [
                "Keep your phone accessible — you may receive calls from verifying officers.",
                "Visit the local office if verification is delayed beyond expected timeline."
            ]
        },
        {
            "step_number": 7,
            "title": "Tracking & Status Updates",
            "description": f"Track your application status using the reference number on the official portal ({scheme.application_url or 'scheme portal'}). You will also receive SMS updates.",
            "estimated_time": "Ongoing",
            "tips": [
                "Check status weekly until approval.",
                "Contact the helpline number if status shows 'pending' for over 30 days.",
                "Use the GovAssist AI dashboard to track all your applications in one place."
            ]
        }
    ]

    # Estimated total completion
    total_estimate = "15-60 days end-to-end (varies by scheme complexity, verification backlog, and state processing speed)"

    return jsonify({
        "scheme_name": scheme.name,
        "scheme_id": scheme.id,
        "application_url": scheme.application_url,
        "ministry": scheme.ministry,
        "steps": steps,
        "estimated_total_completion": total_estimate,
        "required_documents": doc_names,
        "helpline_tip": "For issues, contact the scheme's toll-free helpline or visit the nearest Common Service Centre (CSC) / Akshaya Centre."
    }), 200
