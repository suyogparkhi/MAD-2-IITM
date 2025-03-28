from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    is_active = db.Column(db.Boolean, default = True)

    # relations
    professional = db.relationship('Professional', backref = 'user', uselist = False, cascade = 'all, delete-orphan')
    customer = db.relationship('Customer', backref = 'user', uselist = False, cascade = 'all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_professional(self):
        return self.role == 'professional'
    
    def is_customer(self):
        return self.role == 'customer'
    

class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), nullable = False)
    description = db.Column(db.Text)
    base_price = db.Column(db.Float, nullable = False)
    time_required = db.Column(db.Integer, nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    is_active = db.Column(db.Boolean, default = True)

    #relations
    professionals = db.relationship('Professional', backref='service')
    service_requests = db.relationship('ServiceRequest', backref='service')

class Professional(db.Model):
    __tablename__ = 'professionals'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable = False)
    experience = db.Column(db.Integer)
    description = db.Column(db.Text)
    verification_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    documents = db.Column(db.String(200))
    address = db.Column(db.Text)
    pin_code = db.Column(db.String(10))
    phone = db.Column(db.String(20))

    service_requests = db.relationship('ServiceRequest', backref='professional')


class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.Text)
    pin_code = db.Column(db.String(10))
    
    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='customer')


class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=True)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(20), default='requested')  # requested, assigned, accepted, rejected, completed, closed
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    review = db.relationship('Review', backref='service_request', uselist=False, cascade='all, delete-orphan')


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_requests.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExportJob(db.Model):
    __tablename__ = 'export_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)  # 'service_requests', 'professionals', etc.
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    file_path = db.Column(db.String(255), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    filter_params = db.Column(db.Text, nullable=True)  # JSON string of filter parameters
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('export_jobs', lazy=True))
    
    def to_dict(self):
        """Convert job to a dictionary for API responses"""
        return {
            'id': self.id,
            'job_type': self.job_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'filter_params': json.loads(self.filter_params) if self.filter_params else {},
            'file_url': f'/api/admin/reports/download/{self.file_name}' if self.file_name else None
        }