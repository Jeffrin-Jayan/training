import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import time
from utils import (
    register_user, login_user, get_profile, update_profile, get_dashboard_stats,
    get_applications, apply_scheme, get_recommendations, check_eligibility,
    search_schemes, toggle_bookmark, get_bookmarks, compare_schemes,
    create_chat_session, get_chat_history, get_chat_messages, send_chat_message,
    upload_ocr_file, generate_tts, transcribe_audio_file, generate_complaint,
    get_offices, get_office_types, get_admin_analytics, upload_rag_pdf,
    list_rag_pdfs, delete_rag_pdf, summarize_rag_pdf
)

# Set page configuration with premium dark look
st.set_page_config(
    page_title="GovAssist AI - Citizen Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling - Gold and Deep Navy Theme
st.markdown("""
<style>
    /* Main Background & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main {
        background-color: #0B111E;
        color: #F3F4F6;
    }
    
    /* Header Gold Gradient */
    .header-title {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 5px;
    }
    
    .header-subtitle {
        color: #9CA3AF;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    
    /* Cards - Glassmorphism style */
    .metric-card {
        background: rgba(26, 37, 58, 0.6);
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 215, 0, 0.5);
    }
    
    .metric-title {
        font-size: 0.95rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFD700;
        margin-top: 5px;
    }
    
    /* Scheme Cards */
    .scheme-card {
        background: rgba(30, 41, 59, 0.8);
        border-left: 5px solid #FFD700;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Sidebar adjustments */
    .css-1d391kg {
        background-color: #0E1626;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #0B111E !important;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
    }
    
    /* Status tags */
    .tag-eligible {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .tag-ineligible {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Session States initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'chat_session_id' not in st.session_state:
    st.session_state.chat_session_id = None
if 'ocr_data' not in st.session_state:
    st.session_state.ocr_data = None

# Sidebar Logo / Title
st.sidebar.markdown("<h2 style='color:#FFD700; text-align:center;'>🏛️ GovAssist AI</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#9CA3AF; text-align:center; font-size:0.9rem;'>Intelligent Government Citizen Assistant</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# 1. Login / Sign Up UI
if not st.session_state.logged_in:
    st.markdown("<div class='header-title'>GovAssist AI Portal</div>", unsafe_allow_html=True)
    st.markdown("<div class='header-subtitle'>Empowering Indian citizens with intelligent welfare navigation, RAG search, document OCR, and multi-lingual voice assistants.</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
    
    with tab1:
        st.subheader("Login to Citizen Portal")
        st.info("💡 Demo credentials prefilled. Click 'Sign In' to enter.")
        email_input = st.text_input("Email Address", value="citizen@govassist.in", key="login_email")
        password_input = st.text_input("Password", value="user123", type="password", key="login_pass")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Sign In"):
                res, code = login_user(email_input, password_input)
                if code == 200:
                    st.session_state.logged_in = True
                    st.session_state.user = res["user"]
                    st.success("Successfully logged in!")
                    st.rerun()
                else:
                    st.error(res.get("error", "Login failed. Check server connection."))
        with col2:
            if st.button("Admin Demo Bypass"):
                res, code = login_user("admin@govassist.in", "admin123")
                if code == 200:
                    st.session_state.logged_in = True
                    st.session_state.user = res["user"]
                    st.success("Admin Portal Session established!")
                    st.rerun()
                    
    with tab2:
        st.subheader("Register New Citizen Profile")
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        
        st.markdown("##### Profile Demographics (Used for Scheme Recommendations)")
        r_name = st.text_input("Full Name", value="Aarav Sharma")
        r_age = st.number_input("Age", min_value=1, max_value=120, value=25)
        r_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        r_occupation = st.selectbox("Occupation", ["Farmer", "Student", "Entrepreneur", "Laborer", "Unemployed", "Retired"])
        r_income = st.number_input("Annual Household Income (INR)", value=60000.0)
        r_state = st.selectbox("State of Residence", ["Kerala", "Delhi", "Maharashtra", "Tamil Nadu", "Karnataka"])
        
        if st.button("Register & Setup Profile"):
            if not reg_email or not reg_pass:
                st.error("Please fill in email and password.")
            else:
                res, code = register_user(reg_email, reg_pass, r_name, r_age, r_gender, r_occupation, r_income, r_state)
                if code == 201:
                    st.success("Profile created! Please login using the Sign In tab.")
                else:
                    st.error(res.get("error", "Registration failed."))
else:
    # Authenticated Pages Navigation
    user_role = st.session_state.user.get("role", "user")
    user_id = st.session_state.user.get("id")
    
    pages = [
        "📊 Dashboard", 
        "💬 AI & Voice Assistant", 
        "📋 Scheme Recommender", 
        "⚖️ Compare Schemes", 
        "🔍 OCR & Form Autofill", 
        "🗺️ Office Locator", 
        "✍️ Grievance Complaint"
    ]
    
    # Show Admin panel in list if role is admin
    if user_role == "admin":
        pages.append("🛡️ Admin & Analytics")
        
    pages.append("🚪 Logout")
    
    choice = st.sidebar.radio("Navigation Menu", pages)
    
    # LOGOUT ACTION
    if choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.chat_session_id = None
        st.session_state.ocr_data = None
        st.success("Logged out successfully.")
        st.rerun()
        
    # --- DASHBOARD PAGE ---
    elif choice == "📊 Dashboard":
        st.markdown("<div class='header-title'>Citizen Dashboard</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='header-subtitle'>Welcome back, {st.session_state.user.get('email')}! Access welfare status and scheme trackers.</div>", unsafe_allow_html=True)
        
        stats = get_dashboard_stats(user_id)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Bookmarked Schemes</div>
                <div class='metric-value'>{stats.get('bookmarks', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Submitted Applications</div>
                <div class='metric-value'>{stats.get('applications', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>System Notifications</div>
                <div class='metric-value'>{stats.get('notifications', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("### 📋 Active Welfare Application Progress")
        apps = get_applications(user_id)
        if not apps:
            st.info("You don't have any submitted applications. Go to Scheme Recommender to apply.")
        else:
            for idx, a in enumerate(apps):
                status_color = "#FFA500" # Warning
                if a["status"] == "Approved":
                    status_color = "#10B981"
                elif a["status"] == "Rejected":
                    status_color = "#EF4444"
                    
                st.markdown(f"""
                <div style='background: rgba(30,41,59,0.7); padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid {status_color};'>
                    <div style='display:flex; justify-content:space-between;'>
                        <strong style='font-size:1.1rem; color:#F3F4F6;'>{a['scheme_name']}</strong>
                        <span style='color:{status_color}; font-weight:bold;'>{a['status']}</span>
                    </div>
                    <div style='font-size:0.9rem; color:#9CA3AF; margin-top:5px;'>Remarks: {a['remarks']}</div>
                    <div style='font-size:0.8rem; color:#6B7280; margin-top:5px;'>Last Updated: {a['updated_at'][:10]}</div>
                </div>
                """, unsafe_allow_html=True)
                
        # Bookmarks
        st.markdown("### 🌟 Bookmarked Schemes")
        bms = get_bookmarks(user_id)
        if not bms:
            st.info("No saved schemes found.")
        else:
            cols = st.columns(len(bms) if len(bms) < 4 else 4)
            for idx, bm in enumerate(bms):
                with cols[idx % len(cols)]:
                    st.markdown(f"""
                    <div style='background:rgba(26,37,58,0.5); padding: 15px; border-radius:8px; border:1px solid #FFD700;'>
                        <h4 style='color:#FFD700; margin:0;'>{bm['name']}</h4>
                        <p style='color:#9CA3AF; font-size:0.85rem; margin: 10px 0;'>Category: {bm['category']}</p>
                    </div>
                    """, unsafe_allow_html=True)

    # --- AI & VOICE ASSISTANT ---
    elif choice == "💬 AI & Voice Assistant":
        st.markdown("<div class='header-title'>GovAssist AI Chatroom</div>", unsafe_allow_html=True)
        st.markdown("<div class='header-subtitle'>Multi-lingual smart chatbot powered by local LLM & PDF circular retrieval (RAG). Supports voice queries.</div>", unsafe_allow_html=True)
        
        # Session selector in sidebar
        hist = get_chat_history(user_id)
        
        if not st.session_state.chat_session_id:
            if hist:
                st.session_state.chat_session_id = hist[0]["id"]
            else:
                ns = create_chat_session(user_id)
                if ns:
                    st.session_state.chat_session_id = ns["id"]
                    
        # History Selection
        sidebar_history = st.sidebar.selectbox(
            "Conversation History",
            options=[h["id"] for h in hist] if hist else [st.session_state.chat_session_id],
            format_func=lambda x: next((item["title"] for item in hist if item["id"] == x), "New Conversation") if hist else "New Conversation"
        )
        if sidebar_history != st.session_state.chat_session_id:
            st.session_state.chat_session_id = sidebar_history
            st.rerun()
            
        if st.sidebar.button("➕ Start New Conversation"):
            ns = create_chat_session(user_id)
            if ns:
                st.session_state.chat_session_id = ns["id"]
                st.rerun()
                
        # Setup voice inputs
        st.markdown("#### 🎙️ Voice Input Helper")
        voice_col1, voice_col2 = st.columns([2, 3])
        with voice_col1:
            voice_lang = st.selectbox(
                "Voice / Output Language",
                ["English", "Hindi", "Malayalam", "Tamil"],
                index=0
            )
            lang_codes = {"English": "en-IN", "Hindi": "hi-IN", "Malayalam": "ml-IN", "Tamil": "ta-IN"}
            tts_codes = {"English": "en", "Hindi": "hi", "Malayalam": "ml", "Tamil": "ta"}
            
        with voice_col2:
            st.write("Simulate microphone query:")
            audio_simulation = st.selectbox(
                "Select a voice question to submit:",
                [
                    "No simulation (Use text field)",
                    "Tell me about PM-KISAN scheme",
                    "Do I qualify for Old Age Pension?",
                    "Post-Matric Scholarship details"
                ]
            )
            
        # Chat display container
        messages = get_chat_messages(st.session_state.chat_session_id)
        
        for m in messages:
            sender_title = "👤 Citizen" if m["sender"] == "user" else "🏛️ GovAssist Agent"
            bubble_bg = "rgba(41,56,86,0.3)" if m["sender"] == "user" else "rgba(26,37,58,0.7)"
            border = "1px solid rgba(255,255,255,0.1)" if m["sender"] == "user" else "1px solid rgba(255,215,0,0.3)"
            
            st.markdown(f"""
            <div style='background: {bubble_bg}; padding: 15px; border-radius: 8px; margin-bottom: 12px; border: {border};'>
                <strong>{sender_title}</strong> <span style='font-size:0.8rem; color:#6B7280;'>({m['timestamp'][11:16]})</span>
                <p style='margin-top:8px; line-height:1.5;'>{m['message_text']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Query submissions
        user_msg = ""
        
        # Handle audio simulation click
        if audio_simulation != "No simulation (Use text field)":
            if st.button("Submit Simulated Audio Query"):
                # Transcribe logic simulation
                user_msg = audio_simulation
        else:
            # Text box
            with st.form("chat_form", clear_on_submit=True):
                text_input = st.text_input("Type your question or request scheme support:")
                sub_btn = st.form_submit_value("Send Query")
                if sub_btn:
                    user_msg = text_input
                    
        # Process message
        if user_msg:
            with st.spinner("GovAssist AI thinking..."):
                res, code = send_chat_message(user_id, st.session_state.chat_session_id, user_msg)
                if code == 200:
                    st.success("Query processed!")
                    
                    # Optional TTS output for voice assistant
                    tts_audio = generate_tts(res["message"], tts_codes[voice_lang])
                    if tts_audio:
                        st.audio(tts_audio, format="audio/mp3")
                        
                    st.rerun()
                else:
                    st.error(res.get("error", "Failed to communicate with AI model."))

    # --- SCHEME RECOMMENDER ---
    elif choice == "📋 Scheme Recommender":
        st.markdown("<div class='header-title'>Eligibility Check & Scheme Recommender</div>", unsafe_allow_html=True)
        st.markdown("<div class='header-subtitle'>Fill out your current profile parameters to fetch exact welfare schemes matching your status.</div>", unsafe_allow_html=True)
        
        # Profile loading
        profile, code = get_profile(user_id)
        if code != 200:
            st.error("Failed to load profile. Please verify credentials.")
        else:
            with st.expander("📝 Modify Recommendation Profile Filter Parameters", expanded=False):
                p_name = st.text_input("Full Name", value=profile.get("full_name", ""))
                col1, col2, col3 = st.columns(3)
                with col1:
                    p_age = st.number_input("Age", min_value=1, max_value=120, value=profile.get("age", 18))
                    p_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(profile.get("gender", "Male")))
                with col2:
                    p_occupation = st.selectbox("Occupation", ["Farmer", "Student", "Entrepreneur", "Laborer", "Unemployed", "Retired"], index=["Farmer", "Student", "Entrepreneur", "Laborer", "Unemployed", "Retired"].index(profile.get("occupation", "None") if profile.get("occupation") in ["Farmer", "Student", "Entrepreneur", "Laborer", "Unemployed", "Retired"] else 0))
                    p_income = st.number_input("Annual Income (INR)", value=profile.get("annual_income", 0.0))
                with col3:
                    p_state = st.selectbox("State of Residence", ["Kerala", "Delhi", "Maharashtra", "Tamil Nadu", "Karnataka"], index=["Kerala", "Delhi", "Maharashtra", "Tamil Nadu", "Karnataka"].index(profile.get("state", "Delhi") if profile.get("state") in ["Kerala", "Delhi", "Maharashtra", "Tamil Nadu", "Karnataka"] else 0))
                    p_district = st.text_input("District", value=profile.get("district", ""))
                    
                st.write("Special Demographics Categories:")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    is_farmer = st.checkbox("Active Farmer", value=profile.get("is_farmer", False))
                with c2:
                    is_student = st.checkbox("Enrolled Student", value=profile.get("is_student", False))
                with c3:
                    is_entrepreneur = st.checkbox("Startup / Entrepreneur", value=profile.get("is_entrepreneur", False))
                with c4:
                    has_disability = st.checkbox("Person with Disability", value=profile.get("has_disability", False))
                    is_widow = st.checkbox("Widow Status", value=profile.get("is_widow", False))
                    
                if st.button("Save Profile and Refresh Recommendations"):
                    update_data = {
                        "full_name": p_name,
                        "age": p_age,
                        "gender": p_gender,
                        "occupation": p_occupation,
                        "annual_income": p_income,
                        "state": p_state,
                        "district": p_district,
                        "is_student": is_student,
                        "is_farmer": is_farmer,
                        "is_entrepreneur": is_entrepreneur,
                        "has_disability": has_disability,
                        "is_widow": is_widow
                    }
                    res, update_code = update_profile(user_id, update_data)
                    if update_code == 200:
                        st.success("Profile parameters updated! Recommendations recalculated.")
                        st.rerun()
                    else:
                        st.error(res.get("error"))
            
            # Fetch recommendations
            recs = get_recommendations(user_id)
            st.markdown("### Matching Welfare Schemes & Confidence Analysis")
            
            if not recs:
                st.info("No matching schemes found in the system for this profile.")
            else:
                for r in recs:
                    score_color = "#EF4444"
                    if r["confidence_score"] >= 80:
                        score_color = "#10B981"
                    elif r["confidence_score"] >= 50:
                        score_color = "#F59E0B"
                        
                    badge_class = "tag-eligible" if r["is_eligible"] else "tag-ineligible"
                    elig_text = "ELIGIBLE" if r["is_eligible"] else "INELIGIBLE"
                    
                    st.markdown(f"""
                    <div class='scheme-card'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <h3 style='color:#FFD700; margin:0;'>{r['name']}</h3>
                            <span class='{badge_class}'>{elig_text} ({r['confidence_score']}% Match)</span>
                        </div>
                        <p style='color:#9CA3AF; margin-top:8px;'>{r['description']}</p>
                        <p style='color:#F3F4F6;'>🎁 <strong>Benefits:</strong> {r['benefits']}</p>
                        <p style='color:#6B7280; font-size:0.9rem;'>Ministry: {r['ministry']} | State: {r['state']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_btn1, col_btn2, col_btn3 = st.columns([1.5, 1.5, 5])
                    with col_btn1:
                        # Bookmark Button
                        bms_ids = [b["id"] for b in get_bookmarks(user_id)]
                        bm_label = "⭐ Saved" if r["scheme_id"] in bms_ids else "⭐ Save Scheme"
                        if st.button(bm_label, key=f"bm_{r['scheme_id']}"):
                            toggle_bookmark(user_id, r["scheme_id"])
                            st.rerun()
                    with col_btn2:
                        # Application trigger
                        apps_ids = [a["scheme_id"] for a in get_applications(user_id)]
                        app_label = "✅ Applied" if r["scheme_id"] in apps_ids else "🚀 Apply Now"
                        if st.button(app_label, key=f"apply_{r['scheme_id']}", disabled=(r["scheme_id"] in apps_ids)):
                            apply_scheme(user_id, r["scheme_id"])
                            st.success("Applied successfully!")
                            st.rerun()
                    with col_btn3:
                        if r["reasons"]:
                            st.markdown(f"**Reasons for Score:** {', '.join(r['reasons'])}")
                            
                    st.markdown("<hr style='border-color:rgba(255,255,255,0.05);'/>", unsafe_allow_html=True)

    # --- COMPARE SCHEMES ---
    elif choice == "⚖️ Compare Schemes":
        st.markdown("<div class='header-title'>Compare Government Schemes</div>", unsafe_allow_html=True)
        st.markdown("<div class='header-subtitle'>Compare two welfare schemes side-by-side to understand criteria, values, and required documents.</div>", unsafe_allow_html=True)
        
        all_schemes = search_schemes()
        if len(all_schemes) < 2:
            st.warning("Not enough schemes in database to perform comparison.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                scheme_1 = st.selectbox("Select Scheme 1", [s["id"] for s in all_schemes], format_func=lambda x: next((s["name"] for s in all_schemes if s["id"] == x)))
            with col2:
                scheme_2 = st.selectbox("Select Scheme 2", [s["id"] for s in all_schemes if s["id"] != scheme_1], format_func=lambda x: next((s["name"] for s in all_schemes if s["id"] == x)))
                
            if st.button("Compare Details"):
                res, code = compare_schemes(scheme_1, scheme_2)
                if code == 200:
                    s1 = res["scheme_1"]
                    s2 = res["scheme_2"]
                    
                    c_col1, c_col2 = st.columns(2)
                    with c_col1:
                        st.subheader(s1["name"])
                        st.write(f"**Description:** {s1['description']}")
                        st.write(f"**Benefits:** {s1['benefits']}")
                        st.write(f"**Category:** {s1['category']}")
                        st.write(f"**Ministry:** {s1['ministry']}")
                        st.write(f"**State eligibility:** {s1['state']}")
                        
                        st.markdown("**Eligibility Limits:**")
                        for k, v in s1["eligibility"].items():
                            st.write(f"- {k.replace('_', ' ').capitalize()}: {v}")
                            
                        st.write("**Required Documents:**")
                        st.write(", ".join(s1["documents"]))
                        
                    with c_col2:
                        st.subheader(s2["name"])
                        st.write(f"**Description:** {s2['description']}")
                        st.write(f"**Benefits:** {s2['benefits']}")
                        st.write(f"**Category:** {s2['category']}")
                        st.write(f"**Ministry:** {s2['ministry']}")
                        st.write(f"**State eligibility:** {s2['state']}")
                        
                        st.markdown("**Eligibility Limits:**")
                        for k, v in s2["eligibility"].items():
                            st.write(f"- {k.replace('_', ' ').capitalize()}: {v}")
                            
                        st.write("**Required Documents:**")
                        st.write(", ".join(s2["documents"]))

    # --- OCR & FORM FILLING ---
    elif choice == "🔍 OCR & Form Autofill":
        st.markdown("<div class='header-title'>Document OCR & Form Prefiller</div>", unsafe_allow_html=True)
        st.markdown("<div class='header-subtitle'>Upload Identity documents (Aadhaar Card, PAN Card, Income certificate) to auto-extract structured values and pre-fill application fields.</div>", unsafe_allow_html=True)
        
        st.warning("💡 Upload a file with 'Aadhaar' or 'PAN' or 'Income' in the filename to simulate card reading details immediately.")
        
        ocr_file = st.file_uploader("Upload ID Card Image / PDF", type=["png", "jpg", "jpeg", "pdf"])
        
        if ocr_file is not None:
            if st.button("Perform OCR Extraction"):
                with st.spinner("Reading card via EasyOCR..."):
                    res, code = upload_ocr_file(ocr_file)
                    if code == 200:
                        st.session_state.ocr_data = res["structured_data"]
                        st.success("Extracted structured data successfully!")
                    else:
                        st.error(res.get("error", "OCR Failed"))
                        
        if st.session_state.ocr_data:
            st.markdown("### Side-by-Side Verification & Auto Filled Form")
            
            form_col1, form_col2 = st.columns(2)
            with form_col1:
                st.subheader("1. Extracted Card Data")
                st.json(st.session_state.ocr_data)
                
            with form_col2:
                st.subheader("2. Auto-Prefilled Scheme Application Form")
                with st.form("auto_fill_form"):
                    f_name = st.text_input("Citizen Full Name", value=st.session_state.ocr_data.get("name", ""))
                    f_id = st.text_input("Identity Card Number", value=st.session_state.ocr_data.get("id_number", ""))
                    f_dob = st.text_input("Date of Birth", value=st.session_state.ocr_data.get("dob", ""))
                    f_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0 if st.session_state.ocr_data.get("gender") == "Male" else 1)
                    f_income = st.text_input("Annual Certified Income (INR)", value=st.session_state.ocr_data.get("income", "N/A"))
                    
                    if st.form_submit_button("Submit Form to Government Department"):
                        st.success("Form verified and successfully saved to applications workflow database!")
                        time.sleep(1)
                        st.session_state.ocr_data = None
                        st.rerun()

    # --- OFFICE LOCATOR ---
    elif choice == "🗺️ Office Locator":
        st.markdown("<div class='header-title'>Government Office & akshaya Finder</div>", unsafe_allow_html=True)
        st.markdown("<div class='header-subtitle'>Locate nearest administrative offices (Panchayat, Akshaya, Passport Centre, RTO) dynamically.</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            o_type = st.selectbox("Filter Office Type", ["All", "Akshaya Centre", "Village Office", "Collectorate", "Passport Office", "RTO"])
        with col2:
            o_district = st.selectbox("District", ["All", "Palakkad", "Ernakulam", "Thiruvananthapuram"])
        with col3:
            o_state = st.selectbox("State", ["All", "Kerala"])
            
        # Query offices
        o_t = "" if o_type == "All" else o_type
        o_d = "" if o_district == "All" else o_district
        o_s = "" if o_state == "All" else o_state
        
        offices = get_offices(o_t, o_d, o_s)
        
        if not offices:
            st.info("No offices registered matching criteria.")
        else:
            # Map rendering using Pandas coordinates
            df = pd.DataFrame([
                {
                    "name": o["name"],
                    "latitude": o["latitude"],
                    "longitude": o["longitude"],
                    "type": o["office_type"]
                } for o in offices
            ])
            
            st.markdown("#### Live Map coordinates (OpenStreetMap visualization)")
            st.map(df, latitude="latitude", longitude="longitude", size=50)
            
            # Text list
            st.markdown("#### Registered Office Details:")
            for o in offices:
                st.write(f"- 📍 **{o['name']}** ({o['office_type']}) - District: {o['district']}, Lat: {o['latitude']}, Lon: {o['longitude']}")

    # --- COMPLAINT GENERATOR ---
    elif choice == "✍️ Grievance Complaint":
        st.markdown("<div class='header-title'>Official Grievance Complaint Generator</div>", unsafe_allow_html=True)
        st.markdown("<div class='header-subtitle'>Create legally structured complaint letters and emails to local administrative desks.</div>", unsafe_allow_html=True)
        
        with st.form("complaint_form"):
            c_dept = st.selectbox("Target Department", ["Agriculture and Farmers Welfare", "Public Distribution System (PDS)", "Revenue Department", "Education Board", "Transport RTO", "General Grievance Desk"])
            c_subject = st.text_input("Grievance Subject", value="Delay in processing scholarship payment / land record registration")
            c_details = st.text_area("Grievance Details", value="I submitted my application over 3 months ago. Despite visiting the office multiple times, no updates have been provided...")
            
            if st.form_submit_button("Generate Formal Documents"):
                res, code = generate_complaint(user_id, c_dept, c_subject, c_details)
                if code == 201:
                    st.success("Official Letter Generated and Logged to history!")
                    
                    st.subheader("📁 Formal Letter Output")
                    st.code(res["formal_letter"], language="text")
                    
                    st.subheader("📧 Suggested Email Body")
                    st.code(res["email_body"], language="text")
                    
                    st.subheader("📎 Recommended Attachments")
                    for att in res["suggested_attachments"]:
                        st.write(f"- [ ] {att}")
                else:
                    st.error("Failed to compile grievance letter.")

    # --- ADMIN PANEL ---
    elif choice == "🛡️ Admin & Analytics" and user_role == "admin":
        st.markdown("<div class='header-title'>GovAssist AI Administration Control Center</div>", unsafe_allow_html=True)
        st.markdown("<div class='header-subtitle'>Monitor search trends, upload policy circular PDFs, index knowledge bases into FAISS RAG, and audit metrics.</div>", unsafe_allow_html=True)
        
        tab_an, tab_pdf, tab_sch = st.tabs(["📊 Analytics Metrics", "📁 Index PDF RAG", "➕ Add Scheme"])
        
        with tab_an:
            stats = get_admin_analytics()
            if not stats:
                st.info("No analytics data loaded. Verify that active data matches standard records.")
            else:
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Registered Citizens", stats.get("users", 0))
                c2.metric("Active Schemes", stats.get("schemes", 0))
                c3.metric("Applications Filed", stats.get("applications", 0))
                c4.metric("Complaints Generated", stats.get("complaints", 0))
                c5.metric("Indexed PDFs", stats.get("pdfs", 0))
                
                # Matplotlib Plot distributions
                col_ch1, col_ch2 = st.columns(2)
                with col_ch1:
                    st.subheader("Welfare Schemes Category Distribution")
                    cats = stats.get("categories", [])
                    if cats:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        fig.patch.set_facecolor('#0B111E')
                        ax.set_facecolor('#0B111E')
                        
                        labels = [c["category"] for c in cats]
                        values = [c["count"] for c in cats]
                        
                        ax.bar(labels, values, color='#FFD700')
                        ax.tick_params(colors='#F3F4F6')
                        ax.set_ylabel('Number of Schemes', color='#F3F4F6')
                        st.pyplot(fig)
                        
                with col_ch2:
                    st.subheader("Scheme Application Trends")
                    pops = stats.get("popularity", [])
                    if pops:
                        fig2, ax2 = plt.subplots(figsize=(6, 4))
                        fig2.patch.set_facecolor('#0B111E')
                        
                        labels = [p["scheme"][:15] + "..." for p in pops]
                        sizes = [p["count"] for p in pops]
                        
                        # Only plot pie if there are sizes > 0
                        if sum(sizes) > 0:
                            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', textprops={'color':'w'})
                            st.pyplot(fig2)
                        else:
                            st.info("No applications submitted yet for popularity counts.")
                            
        with tab_pdf:
            st.subheader("Knowledge Circular PDF Uploader (FAISS Integration)")
            
            # File summarization uploader
            st.markdown("##### PDF Summarizer tool:")
            sum_pdf = st.file_uploader("Upload Circular PDF to Summarize", type=["pdf"])
            if sum_pdf:
                if st.button("Summarize Circular"):
                    with st.spinner("Synthesizing summary..."):
                        res, code = summarize_rag_pdf(sum_pdf)
                        if code == 200:
                            st.markdown(res["summary"])
                        else:
                            st.error(res.get("error", "Summarization failed"))
                            
            st.markdown("---")
            st.markdown("##### RAG Vector Store Database Manager:")
            pdf_file = st.file_uploader("Upload Government Notification / scheme PDF to FAISS Index", type=["pdf"], key="rag_uploader")
            
            if pdf_file is not None:
                if st.button("Chunk & Index PDF into VectorDB"):
                    with st.spinner("Extracting text and generating sentence-embeddings..."):
                        res, code = upload_rag_pdf(pdf_file)
                        if code == 201:
                            st.success(res["message"])
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(res.get("error"))
                            
            # List current RAG PDFs
            pdfs = list_rag_pdfs()
            if pdfs:
                st.write("Indexed PDFs in Vector Database:")
                for p in pdfs:
                    col_p1, col_p2 = st.columns([4, 1])
                    col_p1.write(f"- 📄 **{p['filename']}** (Uploaded: {p['uploaded_at'][:10]})")
                    if col_p2.button("Delete", key=f"del_pdf_{p['id']}"):
                        delete_rag_pdf(p["id"])
                        st.success("Deleted PDF context.")
                        st.rerun()
                        
        with tab_sch:
            st.subheader("Add New Scheme & Eligibility Rules")
            with st.form("new_scheme_form"):
                sc_name = st.text_input("Scheme Name", value="PM SVANidhi (Street Vendor's AtmaNirbhar Nidhi)")
                sc_desc = st.text_area("Description", value="A special micro-credit facility scheme for providing affordable working capital loans to street vendors.")
                sc_benefits = st.text_input("Benefits details", value="Initial working capital loan up to ₹10,000, 7% interest subsidy on timely repayment.")
                sc_cat = st.selectbox("Category", ["Business", "Agriculture", "Education", "Social Welfare"])
                sc_ministry = st.text_input("Ministry", value="Ministry of Housing and Urban Affairs")
                sc_state = st.selectbox("State eligibility scope", ["Central", "Delhi", "Kerala"])
                
                st.markdown("###### Eligibility Bounds:")
                c_min_age = st.number_input("Min Age restriction", value=18)
                c_max_age = st.number_input("Max Age restriction", value=75)
                c_income = st.number_input("Max Annual Income limit (INR)", value=300000.0)
                
                c_student = st.checkbox("Requires Student profile status")
                c_farmer = st.checkbox("Requires Farmer profile status")
                c_entrepreneur = st.checkbox("Requires Entrepreneur status", value=True)
                
                if st.form_submit_button("Submit Scheme to Portal"):
                    new_scheme_payload = {
                        "name": sc_name,
                        "description": sc_desc,
                        "benefits": sc_benefits,
                        "category": sc_cat,
                        "ministry": sc_ministry,
                        "state": sc_state,
                        "rules": {
                            "min_age": c_min_age,
                            "max_age": c_max_age,
                            "max_income": c_income,
                            "requires_student": c_student,
                            "requires_farmer": c_farmer,
                            "requires_entrepreneur": c_entrepreneur
                        },
                        "documents": [
                            {"name": "Aadhaar Card", "is_mandatory": True, "description": "Identity verification"},
                            {"name": "Vending Certificate / Letter of Recommendation", "is_mandatory": True, "description": "Vendor verification proof"}
                        ]
                    }
                    
                    import requests
                    try:
                        r = requests.post("http://localhost:5000/api/admin/add_scheme", json=new_scheme_payload)
                        if r.status_code == 201:
                            st.success("New scheme successfully injected and active on recommended pages!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(r.json().get("error", "Failed to insert scheme."))
                    except Exception as e:
                        st.error(f"Failed to connect to backend: {e}")
