from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User, UserProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 400
        
    try:
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
            role=role
        )
        db.session.add(new_user)
        db.session.flush() # Resolve user.id
        
        # Create an empty profile
        new_profile = UserProfile(
            user_id=new_user.id,
            full_name=data.get('full_name', email.split('@')[0].capitalize()),
            age=data.get('age', 18),
            gender=data.get('gender', 'Male'),
            occupation=data.get('occupation', 'None'),
            annual_income=data.get('annual_income', 0.0),
            state=data.get('state', 'Delhi'),
            district=data.get('district', 'New Delhi'),
            education=data.get('education', 'None'),
            is_student=data.get('is_student', False),
            is_farmer=data.get('is_farmer', False),
            is_entrepreneur=data.get('is_entrepreneur', False),
            has_disability=data.get('has_disability', False),
            is_widow=data.get('is_widow', False),
            is_senior_citizen=data.get('is_senior_citizen', False)
        )
        db.session.add(new_profile)
        db.session.commit()
        
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "role": new_user.role
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to register user: {str(e)}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
        
    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 200

@auth_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    user = User.query.get(user_id)
    if not user or not user.profile:
        return jsonify({"error": "User profile not found"}), 404
        
    p = user.profile
    return jsonify({
        "user_id": p.user_id,
        "full_name": p.full_name,
        "age": p.age,
        "gender": p.gender,
        "occupation": p.occupation,
        "annual_income": p.annual_income,
        "state": p.state,
        "district": p.district,
        "education": p.education,
        "is_student": p.is_student,
        "is_farmer": p.is_farmer,
        "is_entrepreneur": p.is_entrepreneur,
        "has_disability": p.has_disability,
        "is_widow": p.is_widow,
        "is_senior_citizen": p.is_senior_citizen
    }), 200

@auth_bp.route('/profile/<int:user_id>', methods=['POST'])
def update_profile(user_id):
    user = User.query.get(user_id)
    if not user or not user.profile:
        return jsonify({"error": "User profile not found"}), 404
        
    data = request.get_json() or {}
    p = user.profile
    
    try:
        p.full_name = data.get('full_name', p.full_name)
        p.age = int(data.get('age', p.age))
        p.gender = data.get('gender', p.gender)
        p.occupation = data.get('occupation', p.occupation)
        p.annual_income = float(data.get('annual_income', p.annual_income))
        p.state = data.get('state', p.state)
        p.district = data.get('district', p.district)
        p.education = data.get('education', p.education)
        p.is_student = bool(data.get('is_student', p.is_student))
        p.is_farmer = bool(data.get('is_farmer', p.is_farmer))
        p.is_entrepreneur = bool(data.get('is_entrepreneur', p.is_entrepreneur))
        p.has_disability = bool(data.get('has_disability', p.has_disability))
        p.is_widow = bool(data.get('is_widow', p.is_widow))
        
        # Calculate senior citizen status based on age
        p.is_senior_citizen = p.age >= 60
        
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update profile: {str(e)}"}), 500


@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    """Simulates password reset for hackathon demo. In production, would send email with reset token."""
    data = request.get_json() or {}
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email address is required"}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        # Don't reveal whether email exists for security
        return jsonify({"message": "If this email is registered, a password reset link has been sent. Check your inbox."}), 200
    
    # In production: generate a JWT token, send email with reset link
    # For hackathon demo: we acknowledge and let them reset directly
    import secrets
    reset_token = secrets.token_urlsafe(32)
    
    return jsonify({
        "message": "Password reset initiated. For this demo, use the reset endpoint below.",
        "demo_reset_token": reset_token,
        "email": email,
        "note": "In production, this token would be emailed to the user. For demo, use /api/auth/reset_password."
    }), 200


@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    """Reset password for a user (demo-friendly; no real token validation)."""
    data = request.get_json() or {}
    email = data.get('email')
    new_password = data.get('new_password')
    
    if not email or not new_password:
        return jsonify({"error": "Email and new password are required"}), 400
    
    if len(new_password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found with this email"}), 404
    
    try:
        user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        return jsonify({"message": "Password reset successfully. You can now login with your new password."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to reset password: {str(e)}"}), 500
