from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    business_name = db.Column(db.String(200))
    google_business_url = db.Column(db.Text)
    gmail_credentials = db.Column(db.Text)  # JSON string for Gmail API credentials
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    templates = db.relationship('ReviewTemplate', backref='user', lazy=True, cascade='all, delete-orphan')
    customers = db.relationship('Customer', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class ReviewTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(300), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Template variables that can be used: {customer_name}, {business_name}, {review_link}
    
    def __repr__(self):
        return f'<ReviewTemplate {self.name}>'

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    appointment_date = db.Column(db.DateTime)
    service_type = db.Column(db.String(200))
    notes = db.Column(db.Text)
    review_requested = db.Column(db.Boolean, default=False)
    review_request_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Segmentation fields
    total_services = db.Column(db.Integer, default=1)
    average_rating = db.Column(db.Float)
    last_rating = db.Column(db.Integer)
    location = db.Column(db.String(200))
    segment_tags = db.Column(db.Text)  # JSON array of tags
    
    # Relationships
    reviews = db.relationship('Review', backref='customer', lazy=True)
    follow_ups = db.relationship('FollowUpSequence', backref='customer', lazy=True, cascade='all, delete-orphan')
    sent_referrals = db.relationship('Referral', foreign_keys='Referral.customer_id', backref='referrer_customer', lazy=True, cascade='all, delete-orphan')
    received_referrals = db.relationship('Referral', foreign_keys='Referral.referred_customer_id', backref='referred_customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, responded, forwarded_to_google
    admin_response = db.Column(db.Text)
    response_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI Enhancement fields
    sentiment = db.Column(db.String(50))  # satisfied, confused, frustrated, angry, neutral
    sentiment_score = db.Column(db.Float)  # confidence score 0-1
    ai_suggested_response = db.Column(db.Text)
    voice_recording_path = db.Column(db.String(500))  # path to voice file
    voice_transcription = db.Column(db.Text)
    review_category = db.Column(db.String(100))  # complaint, praise, suggestion
    
    # Relationships
    conversation_history = db.relationship('ReviewConversation', backref='review', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Review {self.rating} stars from {self.customer.name}>'

class ReviewRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('review_template.id'), nullable=False)
    unique_token = db.Column(db.String(100), unique=True, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    opened_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='sent')  # sent, opened, completed
    
    # Relationships
    template = db.relationship('ReviewTemplate', backref='requests')
    
    def __repr__(self):
        return f'<ReviewRequest {self.unique_token}>'

# New models for AI automation features

class ReviewConversation(db.Model):
    """Track conversation history for each review"""
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(50), nullable=False)  # 'admin', 'ai', 'customer'
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_ai_generated = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ReviewConversation {self.sender}: {self.message[:50]}>'

class FollowUpSequence(db.Model):
    """Track automated follow-up email sequences"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    sequence_step = db.Column(db.Integer, default=1)  # 1, 2, 3
    scheduled_for = db.Column(db.DateTime, nullable=False)
    sent_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, sent, cancelled
    email_content = db.Column(db.Text)
    
    def __repr__(self):
        return f'<FollowUpSequence Step {self.sequence_step} for {self.customer.name}>'

class Referral(db.Model):
    """Track referral links and conversions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # referrer
    referral_token = db.Column(db.String(100), unique=True, nullable=False)
    referred_customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))  # referred customer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime)
    reward_sent = db.Column(db.Boolean, default=False)
    
    # Relationships with explicit foreign keys to avoid ambiguity
    referrer = db.relationship('Customer', foreign_keys=[customer_id])
    referred = db.relationship('Customer', foreign_keys=[referred_customer_id])
    
    def __repr__(self):
        return f'<Referral {self.referral_token}>'

class AutomationSettings(db.Model):
    """User-configurable automation settings"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Follow-up settings
    follow_up_enabled = db.Column(db.Boolean, default=True)
    follow_up_delay_1 = db.Column(db.Integer, default=3)  # days
    follow_up_delay_2 = db.Column(db.Integer, default=7)  # days  
    follow_up_delay_3 = db.Column(db.Integer, default=14)  # days
    follow_up_message_1 = db.Column(db.Text)
    follow_up_message_2 = db.Column(db.Text)
    follow_up_message_3 = db.Column(db.Text)
    
    # AI response settings
    ai_auto_reply_enabled = db.Column(db.Boolean, default=False)
    ai_tone = db.Column(db.String(50), default='professional')  # professional, friendly, casual
    ai_language = db.Column(db.String(10), default='en')
    
    # Report settings
    report_frequency = db.Column(db.String(20), default='weekly')  # weekly, monthly
    report_recipients = db.Column(db.Text)  # JSON array of emails
    
    # Referral settings
    referral_reward_enabled = db.Column(db.Boolean, default=True)
    referral_reward_type = db.Column(db.String(50), default='discount')  # discount, loyalty_points
    referral_reward_value = db.Column(db.String(100), default='10% off next service')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('automation_settings', uselist=False))
    
    def __repr__(self):
        return f'<AutomationSettings for {self.user.username}>'

class ReportGeneration(db.Model):
    """Track generated reports"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # weekly, monthly
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(500))
    sent_to = db.Column(db.Text)  # JSON array of recipient emails
    
    def __repr__(self):
        return f'<ReportGeneration {self.report_type} for {self.user.username}>'
