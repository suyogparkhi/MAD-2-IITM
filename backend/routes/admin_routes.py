from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.models import db, User, Service, Professional, Customer, ServiceRequest, Review
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# Custom decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# Service Management Routes
@admin_bp.route('/services', methods=['GET'])
@login_required
@admin_required
def get_services():
    services = Service.query.all()
    result = []
    
    for service in services:
        result.append({
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': service.base_price,
            'time_required': service.time_required,
            'created_at': service.created_at
        })
    
    return jsonify(result), 200


@admin_bp.route('/services', methods=['POST'])
@login_required
@admin_required
def create_service():
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('name') or not data.get('base_price'):
        return jsonify({'message': 'Name and base price are required'}), 400
    
    # Create new service
    new_service = Service(
        name=data['name'],
        description=data.get('description', ''),
        base_price=float(data['base_price']),
        time_required=data.get('time_required', '')
    )
    
    db.session.add(new_service)
    db.session.commit()
    
    return jsonify({
        'message': 'Service created successfully',
        'service': {
            'id': new_service.id,
            'name': new_service.name,
            'description': new_service.description,
            'base_price': new_service.base_price,
            'time_required': new_service.time_required
        }
    }), 201


@admin_bp.route('/services/<int:service_id>', methods=['PUT'])
@login_required
@admin_required
def update_service(service_id):
    service = Service.query.get_or_404(service_id)
    data = request.get_json()
    
    if 'name' in data:
        service.name = data['name']
    if 'description' in data:
        service.description = data['description']
    if 'base_price' in data:
        service.base_price = float(data['base_price'])
    if 'time_required' in data:
        service.time_required = data['time_required']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Service updated successfully',
        'service': {
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': service.base_price,
            'time_required': service.time_required
        }
    }), 200


@admin_bp.route('/services/<int:service_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    
    # Check if service is being used by professionals or service requests
    if service.professionals or service.service_requests:
        return jsonify({'message': 'Cannot delete service: it is being used by professionals or service requests'}), 400
    
    db.session.delete(service)
    db.session.commit()
    
    return jsonify({'message': 'Service deleted successfully'}), 200


# Professional Management Routes
@admin_bp.route('/professionals', methods=['GET'])
@login_required
@admin_required
def get_professionals():
    professionals = Professional.query.all()
    result = []
    
    for professional in professionals:
        result.append({
            'id': professional.id,
            'user_id': professional.user_id,
            'username': professional.user.username,
            'email': professional.user.email,
            'service_id': professional.service_id,
            'service_name': professional.service.name,
            'experience': professional.experience,
            'verification_status': professional.verification_status,
            'documents': professional.documents
        })
    
    return jsonify(result), 200


@admin_bp.route('/professionals/<int:professional_id>/verify', methods=['PUT'])
@login_required
@admin_required
def verify_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'message': 'Verification status required'}), 400
    
    status = data['status']
    if status not in ['approved', 'rejected']:
        return jsonify({'message': 'Invalid status. Must be "approved" or "rejected"'}), 400
    
    professional.verification_status = status
    db.session.commit()
    
    return jsonify({'message': f'Professional {status} successfully'}), 200


# User Management Routes
@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    users = User.query.filter(User.role != 'admin').all()
    result = []
    
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at
        }
        result.append(user_data)
    
    return jsonify(result), 200


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['PUT'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow admins to be deactivated
    if user.is_admin():
        return jsonify({'message': 'Cannot modify admin user status'}), 403
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    return jsonify({'message': f'User {status} successfully'}), 200


# Service Request Management Routes
@admin_bp.route('/service-requests', methods=['GET'])
@login_required
@admin_required
def get_service_requests():
    service_requests = ServiceRequest.query.all()
    result = []
    
    for req in service_requests:
        result.append({
            'id': req.id,
            'service_id': req.service_id,
            'service_name': req.service.name,
            'customer_id': req.customer_id,
            'customer_name': req.customer.user.username,
            'professional_id': req.professional_id,
            'professional_name': req.professional.user.username if req.professional else None,
            'date_of_request': req.date_of_request,
            'date_of_completion': req.date_of_completion,
            'service_status': req.service_status,
            'remarks': req.remarks
        })
    
    return jsonify(result), 200


# Dashboard Summary Route
@admin_bp.route('/dashboard-summary', methods=['GET'])
@login_required
@admin_required
def dashboard_summary():
    total_services = Service.query.count()
    total_professionals = Professional.query.count()
    total_customers = Customer.query.count()
    total_service_requests = ServiceRequest.query.count()
    pending_approvals = Professional.query.filter_by(verification_status='pending').count()
    
    # Service request status counts
    requested = ServiceRequest.query.filter_by(service_status='requested').count()
    assigned = ServiceRequest.query.filter_by(service_status='assigned').count()
    accepted = ServiceRequest.query.filter_by(service_status='accepted').count()
    completed = ServiceRequest.query.filter_by(service_status='completed').count()
    closed = ServiceRequest.query.filter_by(service_status='closed').count()
    
    # Average ratings calculation
    reviews = Review.query.all()
    total_ratings = sum(review.rating for review in reviews) if reviews else 0
    avg_rating = total_ratings / len(reviews) if reviews else 0
    
    summary = {
        'total_services': total_services,
        'total_professionals': total_professionals,
        'total_customers': total_customers,
        'total_service_requests': total_service_requests,
        'pending_approvals': pending_approvals,
        'service_request_stats': {
            'requested': requested,
            'assigned': assigned,
            'accepted': accepted,
            'completed': completed,
            'closed': closed
        },
        'average_rating': avg_rating
    }
    
    return jsonify(summary), 200