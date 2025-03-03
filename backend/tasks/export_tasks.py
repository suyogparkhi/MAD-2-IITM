from tasks.celery_config import make_celery
from models.models import db, ServiceRequest, Professional, User, Service, Customer
from flask import current_app
from flask_mail import Mail, Message
import os
import csv
from datetime import datetime
import io
import uuid

celery = make_celery()
mail = Mail()

@celery.task
def export_service_requests_csv(professional_id=None, filter_type=None, email=None):
    """
    Exports service requests to a CSV file
    
    Args:
        professional_id: If provided, filter requests by this professional
        filter_type: Filter type ('all', 'completed', 'closed')
        email: Email address to send the CSV to
    
    Returns:
        The path to the generated CSV file
    """
    from app import create_app
    app = create_app()
    
    with app.app_context():
        # Build the query based on filters
        query = ServiceRequest.query
        
        if professional_id:
            query = query.filter(ServiceRequest.professional_id == professional_id)
        
        if filter_type == 'completed':
            query = query.filter(ServiceRequest.service_status == 'completed')
        elif filter_type == 'closed':
            query = query.filter(ServiceRequest.service_status == 'closed')
        
        # Get the service requests
        service_requests = query.all()
        
        # Generate a unique filename
        filename = f"service_requests_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.csv"
        filepath = os.path.join(current_app.root_path, 'exports', filename)
        
        # Ensure the exports directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write the CSV file
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = [
                'ID', 'Service', 'Customer', 'Professional', 'Date Requested',
                'Date Completed', 'Status', 'Remarks', 'Rating'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for req in service_requests:
                professional_name = req.professional.user.username if req.professional else 'Not Assigned'
                rating = req.review.rating if req.review else 'No Rating'
                
                writer.writerow({
                    'ID': req.id,
                    'Service': req.service.name,
                    'Customer': req.customer.user.username,
                    'Professional': professional_name,
                    'Date Requested': req.date_of_request.strftime('%Y-%m-%d'),
                    'Date Completed': req.date_of_completion.strftime('%Y-%m-%d') if req.date_of_completion else 'Not Completed',
                    'Status': req.service_status,
                    'Remarks': req.remarks or '',
                    'Rating': rating
                })
        
        # If an email is provided, send the CSV as an attachment
        if email:
            send_csv_email(email, filepath, filename)
        
        return filepath


def send_csv_email(email, filepath, filename):
    """
    Sends an email with the CSV file attached
    
    Args:
        email: Email address to send to
        filepath: Path to the CSV file
        filename: Name of the CSV file
    """
    subject = "Your Exported Service Requests"
    body = "Please find attached the exported service requests data you requested."
    
    try:
        msg = Message(
            subject=subject,
            recipients=[email],
            body=body,
            sender=os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')
        )
        
        with open(filepath, 'rb') as csv_file:
            msg.attach(filename, 'text/csv', csv_file.read())
        
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email to {email}: {str(e)}")


@celery.task
def generate_admin_report_csv(report_type, email=None):
    """
    Generates administrative reports in CSV format
    
    Args:
        report_type: Type of report ('professionals', 'customers', 'services', 'requests')
        email: Email address to send the CSV to
    
    Returns:
        The path to the generated CSV file
    """
    from app import create_app
    app = create_app()
    
    with app.app_context():
        # Generate a unique filename
        filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(current_app.root_path, 'exports', filename)
        
        # Ensure the exports directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Generate different reports based on type
        if report_type == 'professionals':
            generate_professionals_report(filepath)
        elif report_type == 'customers':
            generate_customers_report(filepath)
        elif report_type == 'services':
            generate_services_report(filepath)
        elif report_type == 'requests':
            generate_requests_report(filepath)
        else:
            return None
        
        # If an email is provided, send the CSV as an attachment
        if email:
            send_csv_email(email, filepath, filename)
        
        return filepath


def generate_professionals_report(filepath):
    """Generates a report of all professionals and their status"""
    professionals = Professional.query.all()
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = [
            'ID', 'Username', 'Email', 'Service', 'Experience',
            'Verification Status', 'Date Joined', 'Completed Requests', 'Average Rating'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for prof in professionals:
            # Count completed requests
            completed_requests = ServiceRequest.query.filter_by(
                professional_id=prof.id,
                service_status='completed'
            ).count()
            
            # Calculate average rating
            from sqlalchemy import func
            from models.models import Review
            
            avg_rating = db.session.query(func.avg(Review.rating)).join(
                ServiceRequest, ServiceRequest.id == Review.service_request_id
            ).filter(ServiceRequest.professional_id == prof.id).scalar() or 0
            
            writer.writerow({
                'ID': prof.id,
                'Username': prof.user.username,
                'Email': prof.user.email,
                'Service': prof.service.name,
                'Experience': prof.experience,
                'Verification Status': prof.verification_status,
                'Date Joined': prof.user.created_at.strftime('%Y-%m-%d'),
                'Completed Requests': completed_requests,
                'Average Rating': f"{avg_rating:.1f}"
            })


def generate_customers_report(filepath):
    """Generates a report of all customers and their activity"""
    customers = Customer.query.all()
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = [
            'ID', 'Username', 'Email', 'Pin Code', 
            'Date Joined', 'Total Requests', 'Completed Requests'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for customer in customers:
            # Count requests
            total_requests = ServiceRequest.query.filter_by(customer_id=customer.id).count()
            completed_requests = ServiceRequest.query.filter_by(
                customer_id=customer.id, 
                service_status='closed'
            ).count()
            
            writer.writerow({
                'ID': customer.id,
                'Username': customer.user.username,
                'Email': customer.user.email,
                'Pin Code': customer.pin_code,
                'Date Joined': customer.user.created_at.strftime('%Y-%m-%d'),
                'Total Requests': total_requests,
                'Completed Requests': completed_requests
            })


def generate_services_report(filepath):
    """Generates a report of all services and their usage"""
    services = Service.query.all()
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = [
            'ID', 'Name', 'Base Price', 'Time Required',
            'Professionals Count', 'Total Requests', 'Average Rating'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for service in services:
            # Count professionals
            professionals_count = Professional.query.filter_by(service_id=service.id).count()
            
            # Count requests
            total_requests = ServiceRequest.query.filter_by(service_id=service.id).count()
            
            # Calculate average rating
            from sqlalchemy import func
            from models.models import Review
            
            avg_rating = db.session.query(func.avg(Review.rating)).join(
                ServiceRequest, ServiceRequest.id == Review.service_request_id
            ).filter(ServiceRequest.service_id == service.id).scalar() or 0
            
            writer.writerow({
                'ID': service.id,
                'Name': service.name,
                'Base Price': f"${service.base_price:.2f}",
                'Time Required': service.time_required,
                'Professionals Count': professionals_count,
                'Total Requests': total_requests,
                'Average Rating': f"{avg_rating:.1f}"
            })


def generate_requests_report(filepath):
    """Generates a report of all service requests"""
    requests = ServiceRequest.query.all()
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = [
            'ID', 'Service', 'Customer', 'Professional', 
            'Date Requested', 'Date Completed', 'Status', 
            'Rating', 'Days to Complete'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for req in requests:
            professional_name = req.professional.user.username if req.professional else 'Not Assigned'
            rating = req.review.rating if req.review else 'No Rating'
            
            # Calculate days to complete
            days_to_complete = ''
            if req.date_of_completion and req.date_of_request:
                delta = req.date_of_completion - req.date_of_request
                days_to_complete = delta.days
            
            writer.writerow({
                'ID': req.id,
                'Service': req.service.name,
                'Customer': req.customer.user.username,
                'Professional': professional_name,
                'Date Requested': req.date_of_request.strftime('%Y-%m-%d'),
                'Date Completed': req.date_of_completion.strftime('%Y-%m-%d') if req.date_of_completion else 'Not Completed',
                'Status': req.service_status,
                'Rating': rating,
                'Days to Complete': days_to_complete
            })