from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models.models import db, User, Professional, Customer, Service
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods = ['POST'])
def login():

    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'missing username or password'}), 400
    
    user = User.query.filter_by(username = data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'message': 'account is deactivated'}), 403
    
    login_user(user)

    return jsonify({
        'message': 'logged in successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    }), 200


@auth_bp.route('/logout', methods = ['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'logged out successfully'}), 200


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
    address = request.form.get('address')
    pin_code = request.form.get('pin_code')
    
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
        documents=filename
    )
    
    db.session.add(new_user)
    db.session.add(new_professional)
    db.session.commit()
    
    return jsonify({'message': 'Professional registration successful. Your account will be active after admin approval.'}), 201


@auth_bp.route('/user-info', methods=['GET'])
@login_required
def get_user_info():
    user_data = {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role
    }
    
    if current_user.is_customer():
        customer = current_user.customer
        user_data.update({
            'address': customer.address,
            'pin_code': customer.pin_code
        })
    
    elif current_user.is_professional():
        professional = current_user.professional
        user_data.update({
            'service': professional.service.name,
            'service_id': professional.service_id,
            'experience': professional.experience,
            'description': professional.description,
            'verification_status': professional.verification_status
        })
    
    return jsonify(user_data), 200


