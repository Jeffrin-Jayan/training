# 🏛️ GovAssist AI – Intelligent Government Citizen Assistant

GovAssist AI is an intelligent, unified government assistant portal that helps Indian citizens navigate welfare schemes, check eligibility, search circulars via RAG, perform OCR-based form auto-filling, generate official complaints, locate service centers, and consult multi-lingual voice assistants.

---

## 🚀 Key Features Built-In
1. **AI Chatbot & RAG Engine:** Natural language conversational assistant utilizing local LLMs and FAISS retrieval from circular PDFs.
2. **Dynamic Scheme Recommender:** Profiles citizens (age, state, income, occupations) to match welfare options with compatibility scores.
3. **Compare Schemes:** Side-by-side comparison of benefits, eligibility, and mandatory files.
4. **Document OCR & Autofill:** Upload ID scans (Aadhaar, PAN) and extract text to fill out forms automatically.
5. **Grievance Complaint Generator:** Compile official letter layouts to regional departments.
6. **Office Locator Map:** Pins common service centers (Akshaya Centers, Panchayats) on active coordinates.
7. **Admin Analytics Console:** Upload circular documents and view active applications graphs.

---

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Backend:** Flask REST API
- **Database:** SQLite (SQLAlchemy)
- **AI Modules:** FAISS Vector Store, Sentence Transformers, EasyOCR, gTTS, SpeechRecognition
- **Deployment:** Docker & Docker Compose

---

## ⚙️ Installation & Running Locally

### Option A: Running with Local Python Environment
1. **Clone/Open Workspace** and set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start Flask Backend Server:**
   ```bash
   python backend/app.py
   ```
   *The backend will automatically initialize the SQLite DB and seed default schemes and offices.*

4. **Start Streamlit Portal:**
   ```bash
   streamlit run frontend/app.py
   ```
   *Open browser at `http://localhost:8501`.*

### Option B: Running with Docker Compose
To run both backend and frontend isolated, execute:
```bash
docker-compose up --build
```
- Frontend UI: `http://localhost:8501`
- Backend API: `http://localhost:5000`

---

## 🧪 Running Unit Tests
To verify all application rules, database relationships, and mock RAG components:
```bash
python -m unittest tests/test_app.py
```

---

## 💡 Live Hackathon Demo Walkthrough Guide
For judges/presentations:
1. **Login:** Use the pre-filled citizen details on the landing screen (`citizen@govassist.in` / `user123`) to enter the Dashboard immediately.
2. **Dashboard:** Observe current applications in progress and saved schemes.
3. **Recommendation:** Open the *Scheme Recommender* page, select demographics parameters (e.g., set occupation to 'Farmer' and state to 'Kerala'), save, and view matching Central sector schemes (like PM-KISAN) with percentage indicators.
4. **Compare:** Go to the *Compare Schemes* tab to view eligibility limits and required documents side-by-side.
5. **OCR autofill:** Visit the *OCR & Form Autofill* page. Upload a mock ID image (filenames containing 'Aadhaar' or 'PAN' will trigger structured extraction) and see fields populated instantly on the right.
6. **Chat assistant:** Go to the *AI Chatroom* to ask scheme related questions, trigger follow-up questions, select regional languages (Malayalam, Hindi, Tamil), and play audio voice output.
7. **Office Finder:** Use the *Office Locator* tab to render service points on a live map.
8. **Admin Control:** Bypass login as `admin@govassist.in` / `admin123` to view analytics graphs and upload a custom policy PDF to FAISS.
