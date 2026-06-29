import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, Float, Boolean, DateTime, Text

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default='user') # user, admin
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="user", cascade="all, delete-orphan")
    admin_actions = relationship("AdminAction", back_populates="user", cascade="all, delete-orphan")

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    occupation: Mapped[str] = mapped_column(String(50), nullable=True)
    annual_income: Mapped[float] = mapped_column(Float, nullable=True)
    state: Mapped[str] = mapped_column(String(50), nullable=True)
    district: Mapped[str] = mapped_column(String(50), nullable=True)
    education: Mapped[str] = mapped_column(String(50), nullable=True)
    is_student: Mapped[bool] = mapped_column(Boolean, default=False)
    is_farmer: Mapped[bool] = mapped_column(Boolean, default=False)
    is_entrepreneur: Mapped[bool] = mapped_column(Boolean, default=False)
    has_disability: Mapped[bool] = mapped_column(Boolean, default=False)
    is_widow: Mapped[bool] = mapped_column(Boolean, default=False)
    is_senior_citizen: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user = relationship("User", back_populates="profile")

class Scheme(db.Model):
    __tablename__ = 'schemes'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    benefits: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False) # Education, Agriculture, Business, Social Welfare
    ministry: Mapped[str] = mapped_column(String(150), nullable=True)
    state: Mapped[str] = mapped_column(String(100), default='Central') # Central, or specific State
    application_url: Mapped[str] = mapped_column(String(250), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    eligibility_rules = relationship("SchemeEligibilityRule", back_populates="scheme", uselist=False, cascade="all, delete-orphan")
    documents = relationship("SchemeDocument", back_populates="scheme", cascade="all, delete-orphan")

class SchemeEligibilityRule(db.Model):
    __tablename__ = 'scheme_eligibility_rules'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scheme_id: Mapped[int] = mapped_column(Integer, ForeignKey('schemes.id'), nullable=False)
    min_age: Mapped[int] = mapped_column(Integer, nullable=True)
    max_age: Mapped[int] = mapped_column(Integer, nullable=True)
    max_income: Mapped[float] = mapped_column(Float, nullable=True)
    allowed_genders: Mapped[str] = mapped_column(String(100), nullable=True) # comma separated values e.g., Male, Female
    allowed_occupations: Mapped[str] = mapped_column(String(200), nullable=True)
    allowed_states: Mapped[str] = mapped_column(String(200), nullable=True) # Central, or specific list
    requires_disability: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_widow: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_student: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_farmer: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_entrepreneur: Mapped[bool] = mapped_column(Boolean, default=False)
    
    scheme = relationship("Scheme", back_populates="eligibility_rules")

class SchemeDocument(db.Model):
    __tablename__ = 'scheme_documents'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scheme_id: Mapped[int] = mapped_column(Integer, ForeignKey('schemes.id'), nullable=False)
    document_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    
    scheme = relationship("Scheme", back_populates="documents")

class PDFDocument(db.Model):
    __tablename__ = 'pdf_documents'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(150), nullable=False)
    file_path: Mapped[str] = mapped_column(String(250), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    chunks = relationship("PDFChunk", back_populates="pdf", cascade="all, delete-orphan")

class PDFChunk(db.Model):
    __tablename__ = 'pdf_chunks'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pdf_id: Mapped[int] = mapped_column(Integer, ForeignKey('pdf_documents.id'), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    
    pdf = relationship("PDFDocument", back_populates="chunks")

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    session_title: Mapped[str] = mapped_column(String(150), default="New Conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    sender: Mapped[str] = mapped_column(String(20), nullable=False) # user, assistant
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    session = relationship("ChatSession", back_populates="messages")

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False) # scheme, pdf, guide
    item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="bookmarks")

class Application(db.Model):
    __tablename__ = 'applications'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    scheme_id: Mapped[int] = mapped_column(Integer, ForeignKey('schemes.id'), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="In Progress") # In Progress, Submitted, Approved, Rejected
    remarks: Mapped[str] = mapped_column(String(250), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="applications")
    scheme = relationship("Scheme")

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    message: Mapped[str] = mapped_column(String(250), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notifications")

class Complaint(db.Model):
    __tablename__ = 'complaints'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    subject: Mapped[str] = mapped_column(String(150), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Generated")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="complaints")

class OfficeLocation(db.Model):
    __tablename__ = 'office_locations'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    office_type: Mapped[str] = mapped_column(String(100), nullable=False) # Akshaya Centre, Village Office, Panchayat, RTO, Collectorate
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

class AdminAction(db.Model):
    __tablename__ = 'admin_actions'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False) # upload_pdf, add_scheme, delete_pdf
    target: Mapped[str] = mapped_column(String(150), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="admin_actions")

class AnalyticsEvent(db.Model):
    __tablename__ = 'analytics_events'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False) # search, scheme_view, chat_query
    payload: Mapped[str] = mapped_column(Text, nullable=True) # JSON details
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
