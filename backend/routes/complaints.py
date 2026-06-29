from flask import Blueprint, request, jsonify
from database import db, Complaint, User
from datetime import datetime

complaints_bp = Blueprint('complaints', __name__)

@complaints_bp.route('/generate', methods=['POST'])
def generate_complaint():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    subject = data.get('subject', 'Grievance submission')
    body_details = data.get('details', '')
    department = data.get('department', 'General Administration')
    
    if not user_id or not body_details:
        return jsonify({"error": "User ID and complaint details are required"}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Get user profile information to prefill sender details
    profile_name = user.profile.full_name if user.profile else "Citizen"
    profile_addr = f"{user.profile.district if user.profile else ''}, {user.profile.state if user.profile else ''}"
    
    date_str = datetime.utcnow().strftime("%d %B %Y")
    
    # Structure a highly professional letter
    formal_letter = (
        f"To,\n"
        f"The Public Grievance Officer,\n"
        f"Department of {department},\n"
        f"Government of India / State Authority.\n\n"
        f"Date: {date_str}\n\n"
        f"Subject: {subject}\n\n"
        f"Respected Sir/Madam,\n\n"
        f"I am writing to formally lodge a complaint regarding the following issue:\n"
        f"{body_details}\n\n"
        f"Kindly review this matter and initiate corrective action at the earliest.\n\n"
        f"Thanking you,\n\n"
        f"Yours faithfully,\n"
        f"{profile_name}\n"
        f"Address/Location: {profile_addr}\n"
        f"Email: {user.email}\n"
    )
    
    # Structure email
    email_body = (
        f"Dear Sir/Madam,\n\n"
        f"Please find attached a grievance letter regarding '{subject}'.\n\n"
        f"Brief Summary:\n"
        f"{body_details[:200]}...\n\n"
        f"Regards,\n"
        f"{profile_name}\n"
        f"GovAssist Assistant Portal Reference"
    )
    
    # Attachment recommendation
    attachments = ["Aadhaar Card copy", "Proof of grievance (receipt/photos/screenshots)", "Previous communication records (if any)"]
    
    try:
        new_complaint = Complaint(
            user_id=user_id,
            subject=subject,
            body=formal_letter,
            department=department,
            status="Generated"
        )
        db.session.add(new_complaint)
        db.session.commit()
        
        return jsonify({
            "complaint_id": new_complaint.id,
            "formal_letter": formal_letter,
            "email_body": email_body,
            "suggested_attachments": attachments,
            "department": department
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save complaint: {str(e)}"}), 500
