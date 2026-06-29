import os
import sys
import unittest
import json

# Add backend directory to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app import create_app
from database import db, User, UserProfile, Scheme, SchemeEligibilityRule
from ai_engine import ai_engine

class GovAssistTest(unittest.TestCase):
    def setUp(self):
        """Set up a temporary testing database context."""
        # Use an in-memory database for quick, isolated tests
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        """Clean up the database context."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_api_health(self):
        """Test the health check endpoint."""
        r = self.client.get('/health')
        self.assertEqual(r.status_code, 200)
        self.assertIn("healthy", r.get_data(as_text=True))
        
    def test_auth_registration_and_login(self):
        """Test complete user registration, profile parameters and login flow."""
        # 1. Registration
        reg_payload = {
            "email": "test_citizen@govassist.in",
            "password": "secure_pass_123",
            "full_name": "Test Citizen",
            "age": 30,
            "gender": "Female",
            "occupation": "Entrepreneur",
            "annual_income": 120000.0,
            "state": "Kerala"
        }
        r = self.client.post('/api/auth/register', json=reg_payload)
        self.assertEqual(r.status_code, 201)
        data = json.loads(r.get_data(as_text=True))
        self.assertIn("user", data)
        user_id = data["user"]["id"]
        
        # 2. Login
        login_payload = {
            "email": "test_citizen@govassist.in",
            "password": "secure_pass_123"
        }
        r = self.client.post('/api/auth/login', json=login_payload)
        self.assertEqual(r.status_code, 200)
        
        # 3. Profile Fetch
        r = self.client.get(f'/api/auth/profile/{user_id}')
        self.assertEqual(r.status_code, 200)
        p_data = json.loads(r.get_data(as_text=True))
        self.assertEqual(p_data["full_name"], "Test Citizen")
        self.assertEqual(p_data["occupation"], "Entrepreneur")
        
    def test_scheme_recommendations(self):
        """Test scheme filtering engine and confidence scores calculation."""
        # Register a student profile
        reg_payload = {
            "email": "student_user@govassist.in",
            "password": "pass123",
            "full_name": "Kumar Student",
            "age": 20,
            "gender": "Male",
            "occupation": "Student",
            "annual_income": 40000.0,
            "state": "Kerala",
            "is_student": True
        }
        r = self.client.post('/api/auth/register', json=reg_payload)
        user_data = json.loads(r.get_data(as_text=True))
        user_id = user_data["user"]["id"]
        
        # Fetch recommendations
        r = self.client.post('/api/schemes/recommend', json={"user_id": user_id})
        self.assertEqual(r.status_code, 200)
        recs = json.loads(r.get_data(as_text=True))
        
        # We expect schemes like "Post-Matric Scholarship" to rank high/eligible
        scholarships = [item for item in recs if "scholarship" in item["name"].lower()]
        if scholarships:
            self.assertTrue(scholarships[0]["is_eligible"])
            self.assertGreaterEqual(scholarships[0]["confidence_score"], 90)

    def test_ai_text_chunking(self):
        """Test that the text chunker splits text correctly."""
        text = "This is a simple sentence that is repeated to simulate a large notification document. " * 30
        chunks = ai_engine.chunk_text(text, chunk_size=10, chunk_overlap=2)
        self.assertTrue(len(chunks) > 0)
        self.assertTrue(all(len(c.split()) <= 15 for c in chunks))

if __name__ == '__main__':
    unittest.main()
