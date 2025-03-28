from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models.models import db, User, Customer, Service, ServiceRequest, Review, Professional
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.sql import func
from utils.auth import customer_required, get_current_user
from cache.cache_config import cache, SERVICE_CACHE_KEY

customer_bp = Blueprint('customer', __name__)

# Profile Management Routes
@customer_bp.route('/profile', methods=['GET'])
@customer_required
def get_profile():
    user = get_current_user()
    customer = user.customer
    
    profile_data = {
        'id': customer.id,
        'user_id': customer.user_id,
        'username': user.username,
        'email': user.email,
        'address': customer.address,
        'pin_code': customer.pin_code
    }
    
    return jsonify(profile_data), 200


@customer_bp.route('/profile', methods=['PUT'])
@customer_required
def update_profile():
    user = get_current_user()
    customer = user.customer
    data = request.get_json()
    
    if 'address' in data:
        customer.address = data['address']
    if 'pin_code' in data:
        customer.pin_code = data['pin_code']
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'}), 200


# Service Browsing Routes
@customer_bp.route('/services', methods=['GET'])
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
@customer_required
def get_service_requests():
    user = get_current_user()
    # Get all service requests made by this customer
    service_requests = ServiceRequest.query.filter_by(
        customer_id=user.customer.id
    ).all()
    
    result = []
    for req in service_requests:
        professional_name = None
        if req.professional:
            professional_name = req.professional.user.username
        
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
@customer_required
def create_service_request():
    user = get_current_user()
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
        customer_id=user.customer.id,
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
@customer_required
def update_service_request(request_id):
    user = get_current_user()
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if the request belongs to this customer
    if service_request.customer_id != user.customer.id:
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
@customer_required
def cancel_service_request(request_id):
    user = get_current_user()
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if the request belongs to this customer
    if service_request.customer_id != user.customer.id:
        return jsonify({'message': 'Not authorized to cancel this request'}), 403
    
    # Can only cancel requests that are not yet completed or closed
    if service_request.service_status in ['completed', 'closed']:
        return jsonify({'message': 'Cannot cancel a completed or closed request'}), 400
    
    db.session.delete(service_request)
    db.session.commit()
    
    return jsonify({'message': 'Service request cancelled successfully'}), 200


# Review Management Routes
@customer_bp.route('/service-requests/<int:request_id>/review', methods=['POST'])
@customer_required
def add_review(request_id):
    user = get_current_user()
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if the request belongs to this customer
    if service_request.customer_id != user.customer.id:
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
@customer_required
def dashboard_summary():
    user = get_current_user()
    customer = user.customer
    
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

@customer_bp.route('/dashboard/stats', methods=['GET'])
@customer_required
def get_dashboard_stats():
    user = get_current_user()
    customer = user.customer
    
    # Count active requests (requested, assigned, accepted)
    active_count = ServiceRequest.query.filter_by(customer_id=customer.id).filter(
        ServiceRequest.service_status.in_(['requested', 'assigned', 'accepted', 'in_progress'])
    ).count()
    
    # Count completed requests
    completed_count = ServiceRequest.query.filter_by(
        customer_id=customer.id, 
        service_status='completed'
    ).count()
    
    # Count available services
    services_count = Service.query.filter_by(is_active=True).count()
    
    stats = {
        'active': active_count,
        'completed': completed_count,
        'services': services_count
    }
    
    return jsonify(stats), 200

@customer_bp.route('/professionals', methods=['GET'])
@customer_required
def get_professionals():
    # Get query parameters
    service_id = request.args.get('service_id', type=int)
    search_query = request.args.get('query', '')
    
    # Start with base query for verified professionals
    query = Professional.query.filter_by(verification_status='approved')
    
    # Add service filter if provided
    if service_id:
        query = query.filter_by(service_id=service_id)
    
    # Add search query filter if provided
    if search_query:
        query = query.join(User).filter(
            User.username.ilike(f'%{search_query}%')
        )
    
    # Execute query
    professionals = query.all()
    
    # Prepare results
    result = []
    for professional in professionals:
        # Get average rating from reviews
        avg_rating = db.session.query(func.avg(Review.rating)).join(
            ServiceRequest, ServiceRequest.id == Review.service_request_id
        ).filter(
            ServiceRequest.professional_id == professional.id
        ).scalar()
        
        # Get review count
        review_count = db.session.query(func.count(Review.id)).join(
            ServiceRequest, ServiceRequest.id == Review.service_request_id
        ).filter(
            ServiceRequest.professional_id == professional.id
        ).scalar()
        
        # Get completed services count
        completed_count = ServiceRequest.query.filter_by(
            professional_id=professional.id,
            service_status='completed'
        ).count()
        
        result.append({
            'id': professional.id,
            'name': professional.user.username,
            'service_id': professional.service_id,
            'service_name': professional.service.name,
            'experience': professional.experience,
            'description': professional.description,
            'avg_rating': float(avg_rating) if avg_rating else None,
            'review_count': review_count or 0,
            'completed_services': completed_count
        })
    
    return jsonify(result), 200

@customer_bp.route('/service-requests/active', methods=['GET'])
@customer_required
def get_active_requests():
    user = get_current_user()
    customer = user.customer
    
    # Get active requests (requested, assigned, accepted, in_progress)
    active_requests = ServiceRequest.query.filter_by(customer_id=customer.id).filter(
        ServiceRequest.service_status.in_(['requested', 'assigned', 'accepted', 'in_progress', 'completed'])
    ).order_by(ServiceRequest.date_of_request.desc()).all()
    
    result = []
    for request in active_requests:
        service = Service.query.get(request.service_id)
        professional = None
        if request.professional_id:
            professional = Professional.query.get(request.professional_id)
            professional_data = {
                'id': professional.id,
                'user': {
                    'id': professional.user.id,
                    'username': professional.user.username,
                    'fullname': professional.user.username  # Using username as fullname
                }
            }
        else:
            professional_data = None
            
        result.append({
            'id': request.id,
            'service': {
                'id': service.id,
                'name': service.name,
                'base_price': float(service.base_price),
                'time_required': service.time_required
            },
            'professional': professional_data,
            'date_of_request': request.date_of_request.isoformat(),
            'service_status': request.service_status,
            'remarks': request.remarks
        })
    
    return jsonify(result), 200

# Service Browsing Routes (public)
@customer_bp.route('/services-public', methods=['GET'])
def get_services_public():
    # Try to get from cache first
    cached_services = cache.get(SERVICE_CACHE_KEY)
    if cached_services:
        return jsonify(cached_services), 200
    
    # If not in cache, get from database
    services = Service.query.all()
    result = []
    
    for service in services:
        result.append({
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': float(service.base_price),
            'time_required': service.time_required,
            'is_active': service.is_active
        })
    
    # Store in cache for 5 minutes
    cache.set(SERVICE_CACHE_KEY, result, timeout=300)
    
    return jsonify(result), 200