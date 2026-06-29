import requests
import streamlit as st

API_URL = "http://localhost:5000/api"

def register_user(email, password, full_name, age, gender, occupation, income, state):
    payload = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "age": int(age),
        "gender": gender,
        "occupation": occupation,
        "annual_income": float(income),
        "state": state
    }
    try:
        r = requests.post(f"{API_URL}/auth/register", json=payload)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": f"Connection failed: {str(e)}"}, 500

def login_user(email, password):
    payload = {"email": email, "password": password}
    try:
        r = requests.post(f"{API_URL}/auth/login", json=payload)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": f"Connection failed: {str(e)}"}, 500

def get_profile(user_id):
    try:
        r = requests.get(f"{API_URL}/auth/profile/{user_id}")
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def update_profile(user_id, profile_data):
    try:
        r = requests.post(f"{API_URL}/auth/profile/{user_id}", json=profile_data)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def get_dashboard_stats(user_id):
    try:
        r = requests.get(f"{API_URL}/dashboard/stats/{user_id}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"bookmarks": 0, "applications": 0, "notifications": 0}

def get_applications(user_id):
    try:
        r = requests.get(f"{API_URL}/dashboard/applications/{user_id}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def apply_scheme(user_id, scheme_id):
    try:
        r = requests.post(f"{API_URL}/dashboard/apply", json={"user_id": user_id, "scheme_id": scheme_id})
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def get_recommendations(user_id):
    try:
        r = requests.post(f"{API_URL}/schemes/recommend", json={"user_id": user_id})
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def check_eligibility(scheme_id, data):
    data["scheme_id"] = scheme_id
    try:
        r = requests.post(f"{API_URL}/schemes/check_eligibility", json=data)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def search_schemes(query="", category="", state=""):
    try:
        r = requests.get(f"{API_URL}/schemes/search", params={"q": query, "category": category, "state": state})
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def toggle_bookmark(user_id, scheme_id):
    try:
        r = requests.post(f"{API_URL}/schemes/bookmark", json={"user_id": user_id, "scheme_id": scheme_id})
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def get_bookmarks(user_id):
    try:
        r = requests.get(f"{API_URL}/schemes/bookmarks/{user_id}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def compare_schemes(scheme_id_1, scheme_id_2):
    payload = {"scheme_id_1": scheme_id_1, "scheme_id_2": scheme_id_2}
    try:
        r = requests.post(f"{API_URL}/schemes/compare", json=payload)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Chat APIs
def create_chat_session(user_id, title="New Conversation"):
    try:
        r = requests.post(f"{API_URL}/chat/session", json={"user_id": user_id, "title": title})
        if r.status_code == 201:
            return r.json()
    except Exception:
        pass
    return None

def get_chat_history(user_id):
    try:
        r = requests.get(f"{API_URL}/chat/history/{user_id}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def get_chat_messages(session_id):
    try:
        r = requests.get(f"{API_URL}/chat/messages/{session_id}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def send_chat_message(user_id, session_id, message_text):
    payload = {"user_id": user_id, "session_id": session_id, "message_text": message_text}
    try:
        r = requests.post(f"{API_URL}/chat/message", json=payload)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# OCR API
def upload_ocr_file(file):
    files = {"file": (file.name, file.getvalue(), file.type)}
    try:
        r = requests.post(f"{API_URL}/ocr/extract", files=files)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Voice APIs
def generate_tts(text, lang="en"):
    payload = {"text": text, "lang": lang}
    try:
        r = requests.post(f"{API_URL}/voice/tts", json=payload)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    return None

def transcribe_audio_file(audio_bytes, lang="en-IN"):
    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
    data = {"lang": lang}
    try:
        r = requests.post(f"{API_URL}/voice/transcribe", files=files, data=data)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Complaint Generator API
def generate_complaint(user_id, department, subject, details):
    payload = {"user_id": user_id, "department": department, "subject": subject, "details": details}
    try:
        r = requests.post(f"{API_URL}/complaints/generate", json=payload)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Office locator API
def get_offices(office_type="", district="", state=""):
    params = {"type": office_type, "district": district, "state": state}
    try:
        r = requests.get(f"{API_URL}/offices/search", params=params)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def get_office_types():
    try:
        r = requests.get(f"{API_URL}/offices/types")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

# Admin APIs
def get_admin_analytics():
    try:
        r = requests.get(f"{API_URL}/admin/analytics")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}

def upload_rag_pdf(file):
    files = {"file": (file.name, file.getvalue(), "application/pdf")}
    try:
        r = requests.post(f"{API_URL}/pdf/upload", files=files)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def list_rag_pdfs():
    try:
        r = requests.get(f"{API_URL}/pdf/list")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def delete_rag_pdf(pdf_id):
    try:
        r = requests.delete(f"{API_URL}/pdf/delete/{pdf_id}")
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def summarize_rag_pdf(file):
    files = {"file": (file.name, file.getvalue(), "application/pdf")}
    try:
        r = requests.post(f"{API_URL}/pdf/summarize", files=files)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500
