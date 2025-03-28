from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.models import db, User, Professional, ServiceRequest, Service
from datetime import datetime
from functools import wraps

professional_bp = Blueprint('professional', __name__)

# Custom decorator to check if user is a professional
def professional_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_professional():
            return jsonify({'message': 'Professional access required'}), 403
        if current_user.professional.verification_status != 'approved':
            return jsonify({'message': 'Your account is not yet approved'}), 403
        return f(*args, **kwargs)
    return decorated_function


# Profile Management Routes
@professional_bp.route('/profile', methods=['GET'])
@login_required
@professional_required
def get_profile():
    professional = current_user.professional
    
    profile_data = {
        'id': professional.id,
        'user_id': professional.user_id,
        'username': current_user.username,
        'email': current_user.email,
        'service_id': professional.service_id,
        'service_name': professional.service.name,
        'experience': professional.experience,
        'description': professional.description,
        'verification_status': professional.verification_status
    }
    
    return jsonify(profile_data), 200


@professional_bp.route('/profile', methods=['PUT'])
@login_required
@professional_required
def update_profile():
    professional = current_user.professional
    data = request.get_json()
    
    if 'description' in data:
        professional.description = data['description']
    if 'experience' in data:
        professional.experience = data['experience']
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'}), 200


# Service Request Management Routes
@professional_bp.route('/service-requests', methods=['GET'])
@login_required
@professional_required
def get_service_requests():
    # Get all service requests assigned to this professional
    professional = current_user.professional
    print(f"Looking for requests with professional_id={professional.id}")
    
    service_requests = ServiceRequest.query.filter_by(
        professional_id=professional.id
    ).all()
    
    print(f"Found {len(service_requests)} professional requests")
    
    result = []
    for req in service_requests:
        # Get the service details
        service = Service.query.get(req.service_id)
        
        result.append({
            'id': req.id,
            'service_id': req.service_id,
            'service_name': req.service.name,
            'service': {
                'name': service.name,
                'base_price': float(service.base_price),
                'time_required': service.time_required
            },
            'customer_id': req.customer_id,
            'customer_name': req.customer.user.username,
            'customer_address': req.customer.address if hasattr(req.customer, 'address') else None,
            'customer_pin_code': req.customer.pin_code if hasattr(req.customer, 'pin_code') else None,
            'date_of_request': req.date_of_request,
            'date_of_completion': req.date_of_completion,
            'service_status': req.service_status,
            'remarks': req.remarks
        })
    
    return jsonify(result), 200


@professional_bp.route('/available-requests', methods=['GET'])
@login_required
@professional_required
def get_available_requests():
    # Get service requests that match the professional's service type and are in 'requested' status
    professional = current_user.professional
    
    # Diagnostic print to debug
    print(f"Looking for requests with service_id={professional.service_id}, status='requested', professional_id=None")
    
    available_requests = ServiceRequest.query.filter_by(
        service_id=professional.service_id,
        service_status='requested'
    ).filter(ServiceRequest.professional_id == None).all()
    
    print(f"Found {len(available_requests)} available requests")
    
    result = []
    for req in available_requests:
        # Get the service details
        service = Service.query.get(req.service_id)
        
        result.append({
            'id': req.id,
            'service_id': req.service_id,
            'service_name': req.service.name,
            'service': {
                'name': service.name,
                'base_price': float(service.base_price),
                'time_required': service.time_required
            },
            'customer_id': req.customer_id,
            'customer_name': req.customer.user.username,
            'customer_address': req.customer.address,
            'customer_pin_code': req.customer.pin_code,
            'date_of_request': req.date_of_request,
            'remarks': req.remarks
        })
    
    return jsonify(result), 200


@professional_bp.route('/service-requests/<int:request_id>/action', methods=['PUT'])
@login_required
@professional_required
def update_service_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    data = request.get_json()
    
    if 'action' not in data:
        return jsonify({'message': 'Action is required'}), 400
    
    action = data['action']
    
    # Check if the service request belongs to this professional's service type
    professional = current_user.professional
    if service_request.service_id != professional.service_id:
        return jsonify({'message': 'This service request does not match your expertise'}), 403
    
    # Handle different actions
    if action == 'accept':
        if service_request.service_status != 'requested':
            return jsonify({'message': 'This request can no longer be accepted'}), 400
        
        service_request.professional_id = professional.id
        service_request.service_status = 'accepted'
    
    elif action == 'reject':
        if service_request.professional_id != professional.id or service_request.service_status not in ['assigned', 'accepted']:
            return jsonify({'message': 'Cannot reject this request'}), 400
        
        service_request.professional_id = None
        service_request.service_status = 'requested'
    
    elif action == 'complete':
        if service_request.professional_id != professional.id or service_request.service_status != 'accepted':
            return jsonify({'message': 'Cannot complete this request'}), 400
        
        service_request.service_status = 'completed'
        service_request.date_of_completion = datetime.utcnow()
    
    else:
        return jsonify({'message': 'Invalid action'}), 400
    
    db.session.commit()
    
    return jsonify({'message': f'Service request {action}ed successfully'}), 200


# Dashboard Summary Route
@professional_bp.route('/dashboard-summary', methods=['GET'])
@login_required
@professional_required
def dashboard_summary():
    professional = current_user.professional
    
    # Count requests by status
    total_requests = ServiceRequest.query.filter_by(professional_id=professional.id).count()
    accepted_requests = ServiceRequest.query.filter_by(professional_id=professional.id, service_status='accepted').count()
    completed_requests = ServiceRequest.query.filter_by(professional_id=professional.id, service_status='completed').count()
    closed_requests = ServiceRequest.query.filter_by(professional_id=professional.id, service_status='closed').count()
    
    # Get average rating
    from sqlalchemy import func
    from models.models import Review
    
    avg_rating = db.session.query(func.avg(Review.rating)).join(
        ServiceRequest, ServiceRequest.id == Review.service_request_id
    ).filter(ServiceRequest.professional_id == professional.id).scalar() or 0
    
    # Available requests
    available_requests = ServiceRequest.query.filter_by(
        service_id=professional.service_id,
        service_status='requested',
        professional_id=None
    ).count()
    
    summary = {
        'total_requests': total_requests,
        'accepted_requests': accepted_requests,
        'completed_requests': completed_requests,
        'closed_requests': closed_requests,
        'available_requests': available_requests,
        'average_rating': float(avg_rating)
    }
    
    return jsonify(summary), 200

@professional_bp.route('/dashboard/stats', methods=['GET'])
@login_required
@professional_required
def get_dashboard_stats():
    professional = current_user.professional
    
    # Count active requests (assigned, accepted)
    active_count = ServiceRequest.query.filter_by(professional_id=professional.id).filter(
        ServiceRequest.service_status.in_(['assigned', 'accepted'])
    ).count()
    
    # Count completed requests
    completed_count = ServiceRequest.query.filter_by(
        professional_id=professional.id, 
        service_status='completed'
    ).count()
    
    # Count available requests
    available_count = ServiceRequest.query.filter_by(
        service_id=professional.service_id,
        service_status='requested',
        professional_id=None
    ).count()
    
    # Get average rating
    from sqlalchemy import func
    from models.models import Review
    
    avg_rating = db.session.query(func.avg(Review.rating)).join(
        ServiceRequest, ServiceRequest.id == Review.service_request_id
    ).filter(ServiceRequest.professional_id == professional.id).scalar() or 0
    
    stats = {
        'active': active_count,
        'completed': completed_count,
        'available': available_count,
        'rating': float(avg_rating)
    }
    
    return jsonify(stats), 200