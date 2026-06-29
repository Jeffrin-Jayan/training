from flask import Blueprint, jsonify, request
from database import db, User, UserProfile, Application, Complaint, Scheme, SchemeEligibilityRule, SchemeDocument, PDFDocument, AnalyticsEvent, AdminAction, ChatMessage, Notification
from sqlalchemy import func, desc
from datetime import datetime
import json

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

        # Scheme categories distribution
        category_stmt = db.session.query(
            Scheme.category, func.count(Scheme.id)
        ).group_by(Scheme.category).all()
        categories = [{"category": item[0], "count": item[1]} for item in category_stmt]

        # User demographics summary
        occupation_stmt = db.session.query(
            UserProfile.occupation, func.count(UserProfile.id)
        ).group_by(UserProfile.occupation).all()
        demographics = [{"occupation": item[0] or "Not Set", "count": item[1]} for item in occupation_stmt]

        # Recent search/chat trends (from analytics events)
        recent_events = AnalyticsEvent.query.order_by(desc(AnalyticsEvent.timestamp)).limit(20).all()
        search_trends = []
        for ev in recent_events:
            search_trends.append({
                "event_type": ev.event_type,
                "payload": ev.payload,
                "timestamp": ev.timestamp.isoformat()
            })

        # Most asked questions (from chat messages)
        recent_questions = ChatMessage.query.filter_by(sender='user').order_by(desc(ChatMessage.timestamp)).limit(15).all()
        top_questions = [{"question": q.message_text[:80], "timestamp": q.timestamp.isoformat()} for q in recent_questions]

        return jsonify({
            "users": total_users,
            "schemes": total_schemes,
            "applications": total_applications,
            "complaints": total_complaints,
            "pdfs": total_pdfs,
            "popularity": popularity,
            "categories": categories,
            "demographics": demographics,
            "search_trends": search_trends,
            "top_questions": top_questions
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
    application_url = data.get('application_url', '')

    if not name or not description or not benefits:
        return jsonify({"error": "Name, description, and benefits are required"}), 400

    try:
        new_scheme = Scheme(
            name=name,
            description=description,
            benefits=benefits,
            category=category,
            ministry=ministry,
            state=state,
            application_url=application_url
        )
        db.session.add(new_scheme)
        db.session.flush()  # Resolve ID

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


@admin_bp.route('/update_scheme/<int:scheme_id>', methods=['PUT'])
def update_scheme(scheme_id):
    """Update an existing scheme's details and eligibility rules."""
    scheme = Scheme.query.get(scheme_id)
    if not scheme:
        return jsonify({"error": "Scheme not found"}), 404

    data = request.get_json() or {}

    try:
        # Update basic scheme info
        scheme.name = data.get('name', scheme.name)
        scheme.description = data.get('description', scheme.description)
        scheme.benefits = data.get('benefits', scheme.benefits)
        scheme.category = data.get('category', scheme.category)
        scheme.ministry = data.get('ministry', scheme.ministry)
        scheme.state = data.get('state', scheme.state)
        scheme.application_url = data.get('application_url', scheme.application_url)

        # Update eligibility rules
        rules_data = data.get('rules', None)
        if rules_data and scheme.eligibility_rules:
            r = scheme.eligibility_rules
            r.min_age = rules_data.get('min_age', r.min_age)
            r.max_age = rules_data.get('max_age', r.max_age)
            r.max_income = rules_data.get('max_income', r.max_income)
            r.allowed_genders = rules_data.get('allowed_genders', r.allowed_genders)
            r.allowed_occupations = rules_data.get('allowed_occupations', r.allowed_occupations)
            r.allowed_states = rules_data.get('allowed_states', r.allowed_states)
            r.requires_farmer = bool(rules_data.get('requires_farmer', r.requires_farmer))
            r.requires_student = bool(rules_data.get('requires_student', r.requires_student))
            r.requires_entrepreneur = bool(rules_data.get('requires_entrepreneur', r.requires_entrepreneur))
            r.requires_disability = bool(rules_data.get('requires_disability', r.requires_disability))
            r.requires_widow = bool(rules_data.get('requires_widow', r.requires_widow))

        db.session.commit()
        return jsonify({"message": f"Scheme '{scheme.name}' updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update scheme: {str(e)}"}), 500


@admin_bp.route('/user_activity', methods=['GET'])
def user_activity():
    """Get comprehensive user activity summary for admin dashboard."""
    try:
        # All users with profile info
        users = User.query.filter_by(role='user').all()
        user_list = []
        for u in users:
            app_count = Application.query.filter_by(user_id=u.id).count()
            complaint_count = Complaint.query.filter_by(user_id=u.id).count()
            last_msg = ChatMessage.query.join(
                ChatMessage.session
            ).filter_by(user_id=u.id).order_by(desc(ChatMessage.timestamp)).first()

            user_list.append({
                "id": u.id,
                "email": u.email,
                "name": u.profile.full_name if u.profile else "N/A",
                "state": u.profile.state if u.profile else "N/A",
                "occupation": u.profile.occupation if u.profile else "N/A",
                "applications": app_count,
                "complaints": complaint_count,
                "last_active": last_msg.timestamp.isoformat() if last_msg else u.created_at.isoformat(),
                "registered_on": u.created_at.isoformat()
            })

        # Admin audit log
        admin_logs = AdminAction.query.order_by(desc(AdminAction.timestamp)).limit(20).all()
        logs = [{
            "admin_email": User.query.get(a.user_id).email if User.query.get(a.user_id) else "Unknown",
            "action": a.action_type,
            "target": a.target,
            "timestamp": a.timestamp.isoformat()
        } for a in admin_logs]

        return jsonify({
            "users": user_list,
            "admin_logs": logs
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch user activity: {str(e)}"}), 500


@admin_bp.route('/log_event', methods=['POST'])
def log_analytics_event():
    """Log a generic analytics event (search, scheme_view, chat_query, etc.)."""
    data = request.get_json() or {}
    event_type = data.get('event_type', 'generic')
    payload = data.get('payload', '')

    try:
        event = AnalyticsEvent(
            event_type=event_type,
            payload=json.dumps(payload) if isinstance(payload, dict) else str(payload)
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({"message": "Event logged"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
