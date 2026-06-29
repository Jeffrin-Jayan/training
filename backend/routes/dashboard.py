from flask import Blueprint, jsonify, request
from database import db, Bookmark, Application, Notification, User, Scheme
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats/<int:user_id>', methods=['GET'])
def get_stats(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    num_bookmarks = Bookmark.query.filter_by(user_id=user_id, item_type='scheme').count()
    num_applications = Application.query.filter_by(user_id=user_id).count()
    num_unread_notifications = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    # Simple alert trigger for demo: if user has 0 applications, seed an "In Progress" one
    if num_applications == 0:
        s = Scheme.query.first()
        if s:
            app = Application(user_id=user_id, scheme_id=s.id, status="In Progress", remarks="Documents verification pending")
            db.session.add(app)
            
            notif = Notification(user_id=user_id, message=f"Application initialized for {s.name}.")
            db.session.add(notif)
            db.session.commit()
            
            num_applications = 1
            num_unread_notifications += 1
            
    return jsonify({
        "bookmarks": num_bookmarks,
        "applications": num_applications,
        "notifications": num_unread_notifications
    }), 200

@dashboard_bp.route('/applications/<int:user_id>', methods=['GET'])
def get_applications(user_id):
    apps = Application.query.filter_by(user_id=user_id).all()
    results = []
    for a in apps:
        results.append({
            "id": a.id,
            "scheme_name": a.scheme.name if a.scheme else "Unknown Scheme",
            "scheme_id": a.scheme_id,
            "status": a.status,
            "remarks": a.remarks,
            "updated_at": a.updated_at.isoformat()
        })
    return jsonify(results), 200

@dashboard_bp.route('/apply', methods=['POST'])
def apply_scheme():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    scheme_id = data.get('scheme_id')
    
    if not user_id or not scheme_id:
        return jsonify({"error": "User ID and Scheme ID are required"}), 400
        
    existing = Application.query.filter_by(user_id=user_id, scheme_id=scheme_id).first()
    if existing:
        return jsonify({"message": "Already applied to this scheme", "application_id": existing.id}), 200
        
    try:
        new_app = Application(
            user_id=user_id,
            scheme_id=scheme_id,
            status="Submitted",
            remarks="Application submitted successfully via GovAssist AI portal."
        )
        db.session.add(new_app)
        
        # Create notification
        scheme = Scheme.query.get(scheme_id)
        scheme_name = scheme.name if scheme else "Scheme"
        notif = Notification(
            user_id=user_id,
            message=f"Application for {scheme_name} has been submitted successfully."
        )
        db.session.add(notif)
        db.session.commit()
        
        return jsonify({
            "message": "Application submitted successfully",
            "application_id": new_app.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to submit application: {str(e)}"}), 500
