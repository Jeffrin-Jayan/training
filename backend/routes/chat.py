from flask import Blueprint, request, jsonify
from database import db, ChatSession, ChatMessage, User, UserProfile
from ai_engine import ai_engine

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/session', methods=['POST'])
def create_session():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    title = data.get('title', 'New Conversation')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
        
    try:
        new_session = ChatSession(user_id=user_id, session_title=title)
        db.session.add(new_session)
        db.session.commit()
        return jsonify({
            "id": new_session.id,
            "title": new_session.session_title,
            "created_at": new_session.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create chat session: {str(e)}"}), 500

@chat_bp.route('/history/<int:user_id>', methods=['GET'])
def get_history(user_id):
    sessions = ChatSession.query.filter_by(user_id=user_id).order_by(ChatSession.created_at.desc()).all()
    results = []
    for s in sessions:
        results.append({
            "id": s.id,
            "title": s.session_title,
            "created_at": s.created_at.isoformat()
        })
    return jsonify(results), 200

@chat_bp.route('/messages/<int:session_id>', methods=['GET'])
def get_messages(session_id):
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.asc()).all()
    results = []
    for m in messages:
        results.append({
            "id": m.id,
            "sender": m.sender,
            "message_text": m.message_text,
            "timestamp": m.timestamp.isoformat()
        })
    return jsonify(results), 200

@chat_bp.route('/message', methods=['POST'])
def send_message():
    data = request.get_json() or {}
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    message_text = data.get('message_text')
    
    if not session_id or not user_id or not message_text:
        return jsonify({"error": "Session ID, User ID, and message text are required"}), 400
        
    session = ChatSession.query.get(session_id)
    if not session or session.user_id != user_id:
        return jsonify({"error": "Invalid session ID or session not owned by user"}), 403
        
    # 1. Retrieve User Profile to construct system prompt context
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    profile_summary = ""
    if profile:
        profile_summary = (
            f"User profile details:\n"
            f"- Name: {profile.full_name}\n"
            f"- Age: {profile.age}\n"
            f"- Gender: {profile.gender}\n"
            f"- Occupation: {profile.occupation}\n"
            f"- Annual Income: ₹{profile.annual_income:,.2f}\n"
            f"- State: {profile.state}\n"
            f"- Special categories: Farmer={profile.is_farmer}, Student={profile.is_student}, "
            f"Disability={profile.has_disability}, Widow={profile.is_widow}, Senior={profile.is_senior_citizen}"
        )
        
    # 2. Build system prompt
    system_prompt = (
        "You are GovAssist AI, an empathetic and highly knowledgeable citizen assistant for Indian government schemes.\n"
        "You have access to the user's profile and vector context documents.\n"
        "Rules:\n"
        "- Give clear, concise, and helpful answers.\n"
        "- Explain criteria explicitly in simple words.\n"
        "- If the query is related to matching schemes, list them.\n"
        "- Refer to the provided document context to give fact-based answers.\n"
        f"{profile_summary}"
    )
    
    # 3. Retrieve relevant chunks using RAG similarity search
    chunks = ai_engine.search_similar_chunks(message_text, k=3)
    
    # 4. Generate response
    response_text = ai_engine.generate_response(system_prompt, message_text, chunks)
    
    # 5. Log both messages into DB
    try:
        user_msg = ChatMessage(session_id=session_id, sender='user', message_text=message_text)
        assistant_msg = ChatMessage(session_id=session_id, sender='assistant', message_text=response_text)
        
        # Auto rename session title if it was default
        if session.session_title == "New Conversation":
            session.session_title = message_text[:30] + ("..." if len(message_text) > 30 else "")
            
        db.session.add(user_msg)
        db.session.add(assistant_msg)
        db.session.commit()
        
        # Follow-up questions generator helper
        follow_ups = _generate_follow_up_questions(message_text, response_text)
        
        return jsonify({
            "message": response_text,
            "session_title": session.session_title,
            "follow_ups": follow_ups
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save and process message: {str(e)}"}), 500

def _generate_follow_up_questions(query, response):
    """Suggests dynamic chips for the chat interface based on query themes."""
    q_low = query.lower()
    r_low = response.lower()
    
    if "pm-kisan" in q_low or "farmer" in q_low:
        return [
            "What documents are required for PM-KISAN?",
            "How do I apply online for PM-KISAN?",
            "Show me other agricultural schemes"
        ]
    if "scholarship" in q_low or "student" in q_low:
        return [
            "Post-Matric Scholarship eligibility details",
            "What is the income certificate validity?",
            "Show me central student schemes"
        ]
    if "pension" in q_low or "senior citizen" in q_low:
        return [
            "IGNOAPS age proof requirements",
            "How to apply for Old Age Pension?",
            "Is there a widow pension scheme?"
        ]
    if "business" in q_low or "entrepreneur" in q_low or "loan" in q_low:
        return [
            "Stand-Up India application process",
            "How to write a business project report?",
            "Are there subsidies for women entrepreneurs?"
        ]
    return [
        "Check my eligibility for schemes",
        "How can I generate a complaint?",
        "Find nearest Akshaya / Common Service Centre"
    ]

@chat_bp.route('/session/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    session = ChatSession.query.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    try:
        db.session.delete(session)
        db.session.commit()
        return jsonify({"message": "Session deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete session: {str(e)}"}), 500
