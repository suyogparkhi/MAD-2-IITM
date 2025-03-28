from tasks.celery_config import make_celery
from models.models import db, ServiceRequest, Professional, User
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import requests
import os 

celery = make_celery()
mail = Mail()

@celery.task
def send_daily_reminders():

    from app import create_app
    app = create_app()

    with app.app_context():

        pending_requests = ServiceRequest.query.filter_by(service_status='pending').all()

        professionals_to_notify = {}

        for req in pending_requests:
            if req.professional_id and req.professional_id not in professionals_to_notify:
                professionals_to_notify[req.professional_id] = []
            
            if req.professional_id:
                professionals_to_notify[req.professional_id].append({
                    'request_id': req.id,
                    'service_name': req.service.name,
                    'customer_name': req.customer.user.username,
                    'date_of_request': req.date_of_request
                })

        
        for prof_id, reqs in professionals_to_notify.items():
            prof = Professional.query.get(prof_id)
            if prof and prof.user:
                send_remainder_notification(prof.user, reqs)


def send_remainder_notification(user, reqs):

    if not user.email:
        return
    
    subject = "Reminder: You have pending service requests"
    
    body = f"Hello {user.username},\n\n"
    body += "This is a reminder that you have the following pending service requests:\n\n"
    
    for req in reqs:
        body += f"- Request #{req['request_id']}: {req['service_name']} for {req['customer_name']}"
        body += f" (Requested on: {req['date_of_request'].strftime('%Y-%m-%d')})\n"
    
    body += "\nPlease log in to your account to manage these requests.\n\n"
    body += "Thank you,\nA-Z Household Services Team"


    try:
        msg = Message(
            subject = subject,
            recipients = [user.email],
            body = body,
            sender = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@household-services.com')
        )
        mail.send(msg)

    except Exception as e:
        print(f'Error sending email to {user.email}: {e}')
