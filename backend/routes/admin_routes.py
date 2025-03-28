from flask import Blueprint, request, jsonify, send_file, current_app, make_response
from flask_login import current_user
from models.models import db, User, Service, Professional, Customer, ServiceRequest, Review, ExportJob
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import os
import csv
import io
import json
from utils.auth import admin_required, get_current_user
from tasks.export_tasks import export_service_requests_csv
from cache.cache_config import cache, DASHBOARD_STATS_CACHE_KEY

admin_bp = Blueprint('admin', __name__)

# Dashboard Route
@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_data():
    user = get_current_user()
    cache_key = DASHBOARD_STATS_CACHE_KEY.format(f'admin_{user.id}')
    
    # Try to get from cache first
    cached_stats = cache.get(cache_key)
    if cached_stats:
        return jsonify(cached_stats), 200
    
    # Count statistics
    services_count = Service.query.count()
    professionals_count = Professional.query.count()
    customers_count = Customer.query.count()
    requests_count = ServiceRequest.query.count()
    
    # Request status counts
    status_counts = {}
    status_results = db.session.query(
        ServiceRequest.service_status, 
        func.count(ServiceRequest.id)
    ).group_by(ServiceRequest.service_status).all()
    
    for status, count in status_results:
        status_counts[status] = count
    
    # Popular services
    popular_services = db.session.query(
        Service.id,
        Service.name,
        func.count(ServiceRequest.id).label('request_count')
    ).join(ServiceRequest).group_by(Service.id).order_by(
        func.count(ServiceRequest.id).desc()
    ).limit(5).all()
    
    popular_services_list = [
        {
            'id': service.id,
            'name': service.name,
            'request_count': service.request_count
        }
        for service in popular_services
    ]
    
    # Recent requests
    recent_requests = db.session.query(
        ServiceRequest.id,
        ServiceRequest.service_status,
        ServiceRequest.date_of_request,
        Service.name.label('service_name'),
        User.username.label('customer_name')
    ).join(Service).join(Customer).join(User, Customer.user_id == User.id).order_by(
        ServiceRequest.date_of_request.desc()
    ).limit(10).all()
    
    recent_requests_list = [
        {
            'id': request.id,
            'status': request.service_status,
            'requested_date': request.date_of_request.isoformat() if request.date_of_request else None,
            'service_name': request.service_name,
            'customer_name': request.customer_name
        }
        for request in recent_requests
    ]
    
    # Prepare response
    dashboard_data = {
        'services_count': services_count,
        'professionals_count': professionals_count,
        'customers_count': customers_count,
        'requests_count': requests_count,
        'request_status_counts': status_counts,
        'popular_services': popular_services_list,
        'recent_requests': recent_requests_list
    }
    
    # Cache the dashboard data for 5 minutes
    cache.set(cache_key, dashboard_data, timeout=300)
    
    return jsonify(dashboard_data), 200


# Service Management Routes
@admin_bp.route('/services', methods=['GET'])
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
            'documents': professional.documents,
            'address': professional.address,
            'pin_code': professional.pin_code,
            'created_at': professional.user.created_at.isoformat() if professional.user.created_at else None
        })
    
    return jsonify(result), 200


@admin_bp.route('/professionals/<int:professional_id>/verify', methods=['PUT'])
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
@admin_required
def get_service_requests():
    requests = ServiceRequest.query.all()
    result = []
    
    for request in requests:
        customer = Customer.query.get(request.customer_id)
        customer_user = User.query.get(customer.user_id) if customer else None
        
        professional = None
        professional_user = None
        if request.professional_id:
            professional = Professional.query.get(request.professional_id)
            if professional:
                professional_user = User.query.get(professional.user_id)
        
        service = Service.query.get(request.service_id)
        
        result.append({
            'id': request.id,
            'service_id': request.service_id,
            'service_name': service.name if service else 'Unknown Service',
            'customer_id': request.customer_id,
            'customer_name': customer_user.username if customer_user else 'Unknown Customer',
            'professional_id': request.professional_id,
            'professional_name': professional_user.username if professional_user else None,
            'date_of_request': request.date_of_request.isoformat() if request.date_of_request else None,
            'date_of_completion': request.date_of_completion.isoformat() if request.date_of_completion else None,
            'service_status': request.service_status,
            'remarks': request.remarks
        })
    
    return jsonify(result), 200


@admin_bp.route('/service-requests/<int:request_id>', methods=['GET'])
@admin_required
def get_service_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    customer = Customer.query.get(service_request.customer_id)
    customer_user = User.query.get(customer.user_id) if customer else None
    
    professional = None
    professional_user = None
    if service_request.professional_id:
        professional = Professional.query.get(service_request.professional_id)
        if professional:
            professional_user = User.query.get(professional.user_id)
    
    service = Service.query.get(service_request.service_id)
    
    result = {
        'id': service_request.id,
        'service_id': service_request.service_id,
        'service_name': service.name if service else 'Unknown Service',
        'customer_id': service_request.customer_id,
        'customer_name': customer_user.username if customer_user else 'Unknown Customer',
        'professional_id': service_request.professional_id,
        'professional_name': professional_user.username if professional_user else None,
        'date_of_request': service_request.date_of_request.isoformat() if service_request.date_of_request else None,
        'date_of_completion': service_request.date_of_completion.isoformat() if service_request.date_of_completion else None,
        'service_status': service_request.service_status,
        'remarks': service_request.remarks
    }
    
    # Get review if exists
    review = Review.query.filter_by(service_request_id=service_request.id).first()
    if review:
        result['review'] = {
            'id': review.id,
            'rating': review.rating,
            'comments': review.comments,
            'created_at': review.created_at.isoformat() if review.created_at else None
        }
    
    return jsonify(result), 200


@admin_bp.route('/service-requests/<int:request_id>/assign', methods=['PUT'])
@admin_required
def assign_professional(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    data = request.get_json()
    
    if not data or 'professional_id' not in data:
        return jsonify({'message': 'Professional ID is required'}), 400
    
    professional_id = data['professional_id']
    professional = Professional.query.get(professional_id)
    
    if not professional:
        return jsonify({'message': 'Professional not found'}), 404
    
    service_request.professional_id = professional_id
    service_request.service_status = 'assigned'
    db.session.commit()
    
    return jsonify({'message': 'Professional assigned successfully'}), 200


@admin_bp.route('/service-requests/<int:request_id>/status', methods=['PUT'])
@admin_required
def update_request_status(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'message': 'Status is required'}), 400
    
    status = data['status']
    valid_statuses = ['requested', 'assigned', 'accepted', 'rejected', 'completed', 'closed']
    
    if status not in valid_statuses:
        return jsonify({'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
    
    service_request.service_status = status
    
    if status == 'completed':
        service_request.date_of_completion = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Request status updated successfully'}), 200


# Dashboard Summary Route
@admin_bp.route('/dashboard-summary', methods=['GET'])
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


# Customer Management Routes
@admin_bp.route('/customers', methods=['GET'])
@admin_required
def get_customers():
    customers = Customer.query.all()
    result = []
    
    for customer in customers:
        user = User.query.get(customer.user_id)
        if user:
            result.append({
                'id': customer.id,
                'user_id': customer.user_id,
                'username': user.username,
                'email': user.email,
                'address': customer.address,
                'pin_code': customer.pin_code,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
    
    return jsonify(result), 200


@admin_bp.route('/customers/<int:customer_id>/status', methods=['PUT'])
@admin_required
def update_customer_status(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    user = User.query.get(customer.user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    if not data or 'is_active' not in data:
        return jsonify({'message': 'is_active status required'}), 400
    
    user.is_active = data['is_active']
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    return jsonify({'message': f'Customer {status} successfully'}), 200


# Reports Routes
@admin_bp.route('/reports/export-jobs', methods=['GET'])
@admin_required
def get_export_jobs():
    """Get a list of export jobs for the current user"""
    user = get_current_user()
    jobs = ExportJob.query.filter_by(user_id=user.id).order_by(ExportJob.created_at.desc()).all()
    
    return jsonify([job.to_dict() for job in jobs]), 200

@admin_bp.route('/reports/export-jobs', methods=['POST'])
@admin_required
def create_export_job():
    """Create a new export job"""
    data = request.get_json()
    
    # Validate data
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    user = get_current_user()
    
    # Create a new export job in the database
    new_job = ExportJob(
        user_id=user.id,
        job_type='service_requests',
        status='pending',
        filter_params=json.dumps(data)
    )
    
    db.session.add(new_job)
    db.session.commit()
    
    # Queue the export task
    export_service_requests_csv.delay(new_job.id)
    
    return jsonify({
        'message': 'Export job created successfully', 
        'job_id': new_job.id,
        'job': new_job.to_dict()
    }), 201

@admin_bp.route('/reports/export-status/<int:job_id>', methods=['GET'])
@admin_required
def check_export_status(job_id):
    """Check the status of an export job"""
    job = ExportJob.query.filter_by(id=job_id, user_id=get_current_user().id).first()
    
    if not job:
        return jsonify({'message': 'Export job not found'}), 404
    
    return jsonify(job.to_dict()), 200

@admin_bp.route('/reports/download/<filename>', methods=['GET'])
@admin_required
def download_export(filename):
    """Download an export file"""
    # Find the job with this filename
    job = ExportJob.query.filter_by(file_name=filename).first()
    
    if not job or not job.file_path or job.status != 'completed':
        # If no job found with this filename, generate a sample file
        return generate_sample_export(filename)
    
    # Check if the file exists
    if not os.path.exists(job.file_path):
        return jsonify({'message': 'Export file not found'}), 404
    
    # Return the file
    return send_file(job.file_path, as_attachment=True, download_name=job.file_name)

def generate_sample_export(filename):
    """Generate a sample export file for demonstration purposes"""
    # Create a sample CSV data
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Write headers
    csv_writer.writerow(['ID', 'Service', 'Customer', 'Professional', 'Status', 'Date'])
    
    # Write some sample rows
    service_requests = ServiceRequest.query.limit(10).all()
    for req in service_requests:
        service = Service.query.get(req.service_id)
        customer = Customer.query.get(req.customer_id)
        customer_user = User.query.get(customer.user_id) if customer else None
        
        professional_name = None
        if req.professional_id:
            professional = Professional.query.get(req.professional_id)
            if professional and professional.user:
                professional_name = professional.user.username
        
        csv_writer.writerow([
            req.id,
            service.name if service else 'Unknown',
            customer_user.username if customer_user else 'Unknown',
            professional_name or 'Not Assigned',
            req.service_status,
            req.date_of_request.strftime('%Y-%m-%d') if req.date_of_request else 'Unknown'
        ])
    
    # Create a response with the CSV data
    response = make_response(csv_data.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv"
    
    return response

@admin_bp.route('/reports/monthly', methods=['GET'])
@admin_required
def get_monthly_reports():
    """Get monthly reports for the last 6 months"""
    # Calculate the last 6 months
    today = datetime.now()
    months = []
    
    for i in range(6):
        month = today.month - i
        year = today.year
        
        if month <= 0:
            month += 12
            year -= 1
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Count requests in this month
        requests_count = ServiceRequest.query.filter(
            ServiceRequest.date_of_request >= start_date,
            ServiceRequest.date_of_request <= end_date
        ).count()
        
        # Count completed requests
        completed_count = ServiceRequest.query.filter(
            ServiceRequest.date_of_request >= start_date,
            ServiceRequest.date_of_request <= end_date,
            ServiceRequest.service_status == 'completed'
        ).count()
        
        # Calculate average rating
        avg_rating = db.session.query(func.avg(Review.rating)).join(
            ServiceRequest, Review.service_request_id == ServiceRequest.id
        ).filter(
            ServiceRequest.date_of_request >= start_date,
            ServiceRequest.date_of_request <= end_date
        ).scalar() or 0
        
        # Calculate revenue (for demo - would be from actual data in a real app)
        # In this example, we'll calculate it as $50 per completed request
        revenue = completed_count * 50
        
        # Add month data to result
        months.append({
            'month': start_date.strftime('%B %Y'),
            'created_at': (start_date + timedelta(days=1)).isoformat(),
            'requests_count': requests_count,
            'completed_count': completed_count,
            'revenue': revenue,
            'avg_rating': float(avg_rating),
            'html_url': f'/api/admin/reports/view/{year}-{month:02d}',
            'pdf_url': f'/api/admin/reports/download/{year}-{month:02d}.pdf'
        })
    
    return jsonify(months), 200

@admin_bp.route('/reports/generate', methods=['POST'])
@admin_required
def generate_report():
    """Generate a custom report based on date range and type"""
    data = request.get_json()
    
    # Validate data
    if not data or 'start_date' not in data or 'end_date' not in data or 'report_type' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        # Parse date strings
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid date format. Use ISO format (YYYY-MM-DD)'}), 400
    
    # Validate date range
    if start_date > end_date:
        return jsonify({'message': 'Start date must be before end date'}), 400
    
    # Validate report type
    report_type = data['report_type']
    if report_type not in ['service_performance', 'customer_activity', 'professional_performance']:
        return jsonify({'message': 'Invalid report type'}), 400
    
    # Log report generation
    print(f"Generating {report_type} report from {start_date} to {end_date}")
    
    # Generate a report ID (would be from database in real app)
    report_id = f"{int(datetime.now().timestamp())}"
    
    # In a real app, this would trigger a background task to generate the report
    return jsonify({
        'message': 'Report generation started successfully',
        'report_id': report_id,
        'status': 'processing',
        'download_url': f'/api/admin/reports/download/{report_id}.pdf',
        'view_url': f'/api/admin/reports/view/{report_id}'
    }), 200

@admin_bp.route('/reports/view/<report_id>', methods=['GET'])
@admin_required
def view_report(report_id):
    """View a report in HTML format"""
    # In a real app, this would retrieve a report from storage
    # For demo purposes, we'll just return a simple HTML response
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Report {report_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #4a86e8; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Service Activity Report</h1>
        <p>Report ID: {report_id}</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Service Requests</td>
                <td>{ServiceRequest.query.count()}</td>
            </tr>
            <tr>
                <td>Completed Requests</td>
                <td>{ServiceRequest.query.filter_by(service_status='completed').count()}</td>
            </tr>
            <tr>
                <td>Average Rating</td>
                <td>{db.session.query(func.avg(Review.rating)).scalar() or 0:.1f} / 5.0</td>
            </tr>
        </table>
        
        <h2>Service Performance</h2>
        <table>
            <tr>
                <th>Service</th>
                <th>Requests</th>
                <th>Avg. Rating</th>
            </tr>
            <tr>
                <td>Plumbing</td>
                <td>42</td>
                <td>4.2</td>
            </tr>
            <tr>
                <td>Electrical</td>
                <td>38</td>
                <td>4.5</td>
            </tr>
            <tr>
                <td>Cleaning</td>
                <td>26</td>
                <td>4.0</td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    response = make_response(html_content)
    response.headers["Content-Type"] = "text/html"
    
    return response

@admin_bp.route('/reports/download/<filename>.pdf', methods=['GET'])
@admin_required
def download_report_pdf(filename):
    """Download a report in PDF format"""
    # In a real app, this would retrieve a PDF from storage or generate one
    # For demo purposes, we'll create a simple PDF with reportlab
    
    try:
        # We'll use StringIO to receive the PDF data
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Add title
        title = Paragraph(f"A-Z Household Services Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Add report info
        report_info = Paragraph(f"Report ID: {filename}", styles['Normal'])
        elements.append(report_info)
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Add summary data
        elements.append(Paragraph("Summary", styles['Heading2']))
        
        data = [
            ["Metric", "Value"],
            ["Total Service Requests", str(ServiceRequest.query.count())],
            ["Completed Requests", str(ServiceRequest.query.filter_by(service_status='completed').count())],
            ["Average Rating", f"{db.session.query(func.avg(Review.rating)).scalar() or 0:.1f} / 5.0"]
        ]
        
        # Create table
        table = Table(data, colWidths=[300, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Add service performance section
        elements.append(Paragraph("Service Performance", styles['Heading2']))
        
        # Get service performance data
        service_data = db.session.query(
            Service.name,
            func.count(ServiceRequest.id).label('request_count'),
            func.avg(Review.rating).label('avg_rating')
        ).outerjoin(
            ServiceRequest, Service.id == ServiceRequest.service_id
        ).outerjoin(
            Review, ServiceRequest.id == Review.service_request_id
        ).group_by(Service.name).order_by(func.count(ServiceRequest.id).desc()).limit(5).all()
        
        if service_data:
            service_table_data = [["Service", "Requests", "Avg. Rating"]]
            
            for service in service_data:
                service_table_data.append([
                    service.name,
                    str(service.request_count),
                    f"{service.avg_rating or 0:.1f}"
                ])
                
            service_table = Table(service_table_data, colWidths=[200, 150, 150])
            service_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (2, 0), 12),
                ('BACKGROUND', (0, 1), (2, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(service_table)
        else:
            elements.append(Paragraph("No service data available", styles['Normal']))
        
        # Build the PDF
        doc.build(elements)
        
        # Get the PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = make_response(pdf_data)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}.pdf"
        response.headers["Content-Type"] = "application/pdf"
        
        return response
    
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        # Fallback to text version if PDF generation fails
        report_content = f"""
        A-Z Household Services Report
        =============================
        
        Report ID: {filename}
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Summary:
        - Total Service Requests: {ServiceRequest.query.count()}
        - Completed Requests: {ServiceRequest.query.filter_by(service_status='completed').count()}
        - Average Rating: {db.session.query(func.avg(Review.rating)).scalar() or 0:.1f} / 5.0
        
        This is a placeholder for a real PDF report.
        In a production environment, this would be a properly formatted PDF document.
        """
        
        # Create response with the report content
        response = make_response(report_content)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}.pdf"
        response.headers["Content-Type"] = "application/pdf"
        
        return response

# Public endpoint for professionals data
@admin_bp.route('/professionals-public', methods=['GET'])
def get_professionals_public():
    """Public endpoint to get professionals data, primarily for service request assignment"""
    professionals = Professional.query.all()
    result = []
    
    for professional in professionals:
        # Include essential fields for UI display and professional selection
        result.append({
            'id': professional.id,
            'user_id': professional.user_id,
            'username': professional.user.username,
            'service_id': professional.service_id,
            'service_name': professional.service.name,
            'experience': professional.experience,
            'verification_status': professional.verification_status,
            'address': professional.address,
            'avg_rating': None  # Can be calculated if needed
        })
    
    return jsonify(result), 200