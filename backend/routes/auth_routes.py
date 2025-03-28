from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models.models import db, User, Professional, Customer, Service
import os
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods = ['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400
    
    # Add debug logging
    print(f"Login attempt with username: {data.get('username')}")
    
    user = User.query.filter_by(username = data['username']).first()

    if not user:
        print(f"User not found: {data.get('username')}")
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.check_password(data['password']):
        print(f"Invalid password for user: {data.get('username')}")
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.is_active:
        print(f"Account is deactivated for user: {data.get('username')}")
        return jsonify({'message': 'Account is deactivated'}), 403
    
    # Login successful
    login_user(user)
    print(f"Login successful for user: {user.username}, role: {user.role}")
    
    # Generate JWT token
    token_expiry = datetime.utcnow() + timedelta(days=1)
    token_payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': token_expiry
    }
    token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    print(f"Generated token for user: {user.username}")

    return jsonify({
        'message': 'Logged in successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        },
        'token': token
    }), 200


@auth_bp.route('/logout', methods = ['POST'])
def logout():
    # Check if the user is logged in before attempting to log them out
    if current_user.is_authenticated:
        print(f"Logging out user: {current_user.username}")
        logout_user()
        return jsonify({'message': 'Logged out successfully'}), 200
    else:
        print("Logout attempt for non-logged in user")
        return jsonify({'message': 'No user logged in'}), 200


@auth_bp.route('/register/customer', methods=['POST'])
def register_customer():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'fullname', 'address', 'pin_code']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email'],
        role='customer'
    )
    new_user.set_password(data['password'])
    
    # Create customer profile
    new_customer = Customer(
        user=new_user,
        address=data['address'],
        pin_code=data['pin_code']
    )
    
    db.session.add(new_user)
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify({'message': 'Customer registration successful'}), 201


@auth_bp.route('/register/professional', methods=['POST'])
def register_professional():
    # Handle file upload for documents
    if 'documents' not in request.files:
        return jsonify({'message': 'No document file provided'}), 400
    
    file = request.files['documents']
    if file.filename == '':
        return jsonify({'message': 'No document file selected'}), 400
    
    # Validate form data
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    fullname = request.form.get('fullname')
    service_id = request.form.get('service_id')
    experience = request.form.get('experience')
    description = request.form.get('description')
    
    # Get address and pin_code fields
    address = request.form.get('address')
    pin_code = request.form.get('pin_code')
    phone = request.form.get('phone')
    
    # Check required fields
    if not all([username, email, password, service_id, experience]):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    # Check if service exists
    service = Service.query.get(service_id)
    if not service:
        return jsonify({'message': 'Invalid service ID'}), 400
    
    # Save the document file
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.root_path, 'uploads', 'documents')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # Create new user
    new_user = User(
        username=username,
        email=email,
        role='professional'
    )
    new_user.set_password(password)
    
    # Create professional profile
    new_professional = Professional(
        user=new_user,
        service_id=service_id,
        experience=experience,
        description=description,
        documents=filename,
        address=address,
        pin_code=pin_code,
        phone=phone
    )
    
    db.session.add(new_user)
    db.session.add(new_professional)
    db.session.commit()
    
    return jsonify({'message': 'Professional registration successful. Your account will be active after admin approval.'}), 201


@auth_bp.route('/user-info', methods=['GET'])
def get_user_info():
    # First check if user is authenticated through session
    if current_user.is_authenticated:
        user = current_user
    else:
        # Check if user is authenticated via JWT token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                user_id = payload.get('user_id')
                user = User.query.get(user_id)
                if not user:
                    return jsonify({'message': 'User not found'}), 404
            except:
                return jsonify({'message': 'Invalid token'}), 401
        else:
            return jsonify({'message': 'Authentication required'}), 401
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }
    
    if user.is_customer():
        customer = user.customer
        user_data.update({
            'address': customer.address,
            'pin_code': customer.pin_code
        })
    
    elif user.is_professional():
        professional = user.professional
        user_data.update({
            'service': professional.service.name,
            'service_id': professional.service_id,
            'experience': professional.experience,
            'description': professional.description,
            'verification_status': professional.verification_status
        })
    
    return jsonify(user_data), 200


@auth_bp.route('/services', methods=['GET'])
def get_public_services():
    """Public endpoint to get all services without authentication"""
    services = Service.query.all()
    result = []
    
    for service in services:
        result.append({
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': service.base_price,
            'time_required': service.time_required
        })
    
    return jsonify(result), 200


@auth_bp.route('/change-password', methods=['PUT'])
@login_required
def change_password():
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'message': 'Missing current password or new password'}), 400
    
    current_password = data['current_password']
    new_password = data['new_password']
    
    # Verify current password
    if not current_user.check_password(current_password):
        return jsonify({'message': 'Current password is incorrect'}), 401
    
    # Update password
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password updated successfully'}), 200


