from flask import Blueprint, jsonify, request
from database import db, User, Application, Complaint, Scheme, SchemeEligibilityRule, SchemeDocument, PDFDocument
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/analytics', methods=['GET'])
def get_analytics():
    try:
        total_users = User.query.filter_by(role='user').count()
        total_schemes = Scheme.query.count()
        total_applications = Application.query.count()
        total_complaints = Complaint.query.count()
        total_pdfs = PDFDocument.query.count()
        
        # Schemes popularity (applications count per scheme)
        popularity_stmt = db.session.query(
            Scheme.name, func.count(Application.id).label('app_count')
        ).join(Application, Application.scheme_id == Scheme.id, isouter=True).group_by(Scheme.id).all()
        
        popularity = [{"scheme": item[0], "count": item[1]} for item in popularity_stmt]
        
        # User Demographics summary: occupation
        occupation_stmt = db.session.query(
            User.profile.has_key('occupation'), func.count(User.id) # fallback safe
        )
        
        # Simple count group by categories
        category_stmt = db.session.query(
            Scheme.category, func.count(Scheme.id)
        ).group_by(Scheme.category).all()
        categories = [{"category": item[0], "count": item[1]} for item in category_stmt]
        
        return jsonify({
            "users": total_users,
            "schemes": total_schemes,
            "applications": total_applications,
            "complaints": total_complaints,
            "pdfs": total_pdfs,
            "popularity": popularity,
            "categories": categories
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch analytics: {str(e)}"}), 500

@admin_bp.route('/add_scheme', methods=['POST'])
def add_scheme():
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description')
    benefits = data.get('benefits')
    category = data.get('category', 'Social Welfare')
    ministry = data.get('ministry')
    state = data.get('state', 'Central')
    
    if not name or not description or not benefits:
        return jsonify({"error": "Name, description, and benefits are required"}), 400
        
    try:
        new_scheme = Scheme(
            name=name,
            description=description,
            benefits=benefits,
            category=category,
            ministry=ministry,
            state=state
        )
        db.session.add(new_scheme)
        db.session.flush() # Resolve ID
        
        # Build rules
        rules_data = data.get('rules', {})
        new_rules = SchemeEligibilityRule(
            scheme_id=new_scheme.id,
            min_age=rules_data.get('min_age', 0),
            max_age=rules_data.get('max_age', 120),
            max_income=rules_data.get('max_income', 500000.0),
            allowed_genders=rules_data.get('allowed_genders', 'Male,Female,Other'),
            allowed_occupations=rules_data.get('allowed_occupations', 'Any'),
            allowed_states=rules_data.get('allowed_states', 'Central'),
            requires_farmer=bool(rules_data.get('requires_farmer', False)),
            requires_student=bool(rules_data.get('requires_student', False)),
            requires_entrepreneur=bool(rules_data.get('requires_entrepreneur', False)),
            requires_disability=bool(rules_data.get('requires_disability', False)),
            requires_widow=bool(rules_data.get('requires_widow', False))
        )
        db.session.add(new_rules)
        
        # Build document requirements
        docs = data.get('documents', [])
        for d in docs:
            new_doc = SchemeDocument(
                scheme_id=new_scheme.id,
                document_name=d.get('name', 'ID Card'),
                is_mandatory=bool(d.get('is_mandatory', True)),
                description=d.get('description', '')
            )
            db.session.add(new_doc)
            
        db.session.commit()
        return jsonify({"message": "Scheme added successfully", "scheme_id": new_scheme.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add scheme: {str(e)}"}), 500
