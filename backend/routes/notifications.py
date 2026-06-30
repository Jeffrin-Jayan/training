from flask import Blueprint, jsonify, request
from database import db, Notification

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/list/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    results = []
    for n in notifs:
        results.append({
            "id": n.id,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        })
    return jsonify(results), 200

@notifications_bp.route('/read/<int:notification_id>', methods=['POST'])
def mark_read(notification_id):
    n = Notification.query.get(notification_id)
    if not n:
        return jsonify({"error": "Notification not found"}), 404
        
    try:
        n.is_read = True
        db.session.commit()
        return jsonify({"message": "Notification marked as read"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update notification: {str(e)}"}), 500
