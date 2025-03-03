from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.models import db, User, Customer, Service, ServiceRequest, Review, Professional
from datetime import datetime
from functools import wraps
from sqlalchemy import or_

customer_bp = Blueprint('customer', __name__)

# Custom decorator to check if user is a customer
def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_customer():
            return jsonify({'message': 'Customer access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# Profile Management Routes
@customer_bp.route('/profile', methods=['GET'])
@login_required
@customer_required
def get_profile():
    customer = current_user.customer
    
    profile_data = {
        'id': customer.id,
        'user_id': customer.user_id,
        'username': current_user.username,
        'email': current_user.email,
        'address': customer.address,
        'pin_code': customer.pin_code
    }
    
    return jsonify(profile_data), 200


@customer_bp.route('/profile', methods=['PUT'])
@login_required
@customer_required
def update_profile():
    customer = current_user.customer
    data = request.get_json()
    
    if 'address' in data:
        customer.address = data['address']
    if 'pin_code' in data:
        customer.pin_code = data['pin_code']
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'}), 200


# Service Browsing Routes
@customer_bp.route('/services', methods=['GET'])
@login_required
@customer_required
def get_services():
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


@customer_bp.route('/search-services', methods=['GET'])
@login_required
@customer_required
def search_services():
    search_query = request.args.get('query', '')
    
    if not search_query:
        return jsonify({'message': 'Search query is required'}), 400
    
    # Search for services by name or description
    services = Service.query.filter(
        or_(
            Service.name.ilike(f'%{search_query}%'),
            Service.description.ilike(f'%{search_query}%')
        )
    ).all()
    
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


# Service Request Management Routes
@customer_bp.route('/service-requests', methods=['GET'])
@login_required
@customer_required
def get_service_requests():
    # Get all service requests made by this customer
    service_requests = ServiceRequest.query.filter_by(
        customer_id=current_user.customer.id
    ).all()
    
    result = []
    for req in service_requests:
        professional_name = None
        if req.professional:
            professional_name = req.professional.user.username
            
        result.append({
            'id': req.id,
            'service_id': req.service_id,
            'service_name': req.service.name,
            'professional_id': req.professional_id,
            'professional_name': professional_name,
            'date_of_request': req.date_of_request,
            'date_of_completion': req.date_of_completion,
            'service_status': req.service_status,
            'remarks': req.remarks,
            'has_review': req.review is not None
        })
    
    return jsonify(result), 200


@customer_bp.route('/service-requests', methods=['POST'])
@login_required
@customer_required
def create_service_request():
    data = request.get_json()
    
    # Validate required fields
    if not data or 'service_id' not in data:
        return jsonify({'message': 'Service ID is required'}), 400
    
    # Check if service exists
    service = Service.query.get(data['service_id'])
    if not service:
        return jsonify({'message': 'Invalid service ID'}), 400
    
    # Create new service request
    new_request = ServiceRequest(
        service_id=data['service_id'],
        customer_id=current_user.customer.id,
        remarks=data.get('remarks', ''),
        service_status='requested'
    )
    
    db.session.add(new_request)
    db.session.commit()
    
    return jsonify({
        'message': 'Service request created successfully',
        'request_id': new_request.id
    }), 201


@customer_bp.route('/service-requests/<int:request_id>', methods=['PUT'])
@login_required
@customer_required
def update_service_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if the request belongs to this customer
    if service_request.customer_id != current_user.customer.id:
        return jsonify({'message': 'Not authorized to update this request'}), 403
    
    data = request.get_json()
    
    # Handle closing the service request
    if 'action' in data and data['action'] == 'close':
        if service_request.service_status not in ['completed']:
            return jsonify({'message': 'Can only close completed service requests'}), 400
        
        service_request.service_status = 'closed'
        db.session.commit()
        
        return jsonify({'message': 'Service request closed successfully'}), 200
    
    # Update remarks
    if 'remarks' in data:
        service_request.remarks = data['remarks']
    
    db.session.commit()
    
    return jsonify({'message': 'Service request updated successfully'}), 200


@customer_bp.route('/service-requests/<int:request_id>/cancel', methods=['PUT'])
@login_required
@customer_required
def cancel_service_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if the request belongs to this customer
    if service_request.customer_id != current_user.customer.id:
        return jsonify({'message': 'Not authorized to cancel this request'}), 403
    
    # Can only cancel requests that are not yet completed or closed
    if service_request.service_status in ['completed', 'closed']:
        return jsonify({'message': 'Cannot cancel a completed or closed request'}), 400
    
    db.session.delete(service_request)
    db.session.commit()
    
    return jsonify({'message': 'Service request cancelled successfully'}), 200


# Review Management Routes
@customer_bp.route('/service-requests/<int:request_id>/review', methods=['POST'])
@login_required
@customer_required
def add_review(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if the request belongs to this customer
    if service_request.customer_id != current_user.customer.id:
        return jsonify({'message': 'Not authorized to review this request'}), 403
    
    # Check if the request is completed or closed
    if service_request.service_status not in ['completed', 'closed']:
        return jsonify({'message': 'Can only review completed or closed requests'}), 400
    
    # Check if a review already exists
    if service_request.review:
        return jsonify({'message': 'A review already exists for this request'}), 400
    
    data = request.get_json()
    
    # Validate required fields
    if not data or 'rating' not in data:
        return jsonify({'message': 'Rating is required'}), 400
    
    rating = int(data['rating'])
    if rating < 1 or rating > 5:
        return jsonify({'message': 'Rating must be between 1 and 5'}), 400
    
    # Create new review
    new_review = Review(
        service_request_id=request_id,
        rating=rating,
        comments=data.get('comments', '')
    )
    
    db.session.add(new_review)
    db.session.commit()
    
    return jsonify({'message': 'Review added successfully'}), 201


# Dashboard Summary Route
@customer_bp.route('/dashboard-summary', methods=['GET'])
@login_required
@customer_required
def dashboard_summary():
    customer = current_user.customer
    
    # Count requests by status
    total_requests = ServiceRequest.query.filter_by(customer_id=customer.id).count()
    requested = ServiceRequest.query.filter_by(customer_id=customer.id, service_status='requested').count()
    accepted = ServiceRequest.query.filter_by(customer_id=customer.id, service_status='accepted').count()
    completed = ServiceRequest.query.filter_by(customer_id=customer.id, service_status='completed').count()
    closed = ServiceRequest.query.filter_by(customer_id=customer.id, service_status='closed').count()
    
    summary = {
        'total_requests': total_requests,
        'requested': requested,
        'accepted': accepted,
        'completed': completed,
        'closed': closed
    }
    
    return jsonify(summary), 200