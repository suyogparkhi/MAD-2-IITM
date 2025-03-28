from tasks.celery_config import make_celery
from models.models import db, ServiceRequest, Customer, User, Review
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import os 
from sqlalchemy import func
import jinja2
import pdfkit

celery = make_celery()
mail = Mail()

@celery.task
def generate_monthly_reports():

    from app import create_app
    app = create_app()

    with app.app_context():

        today = datetime.today()
        first_day_of_month = datetime(today.year, today.month, 1)
        last_month_end = first_day_of_month = timedelta(days=1)
        last_month_start = datetime(last_month_end.year, last_month_end.month, 1)

        customers = Customer.query.join(ServiceRequest).filter(
            ServiceRequest.date_of_request >= last_month_start,
            ServiceRequest.date_of_request <= last_month_end,
        ).distinct().all()

        for customer in customers:
            if customer.user and customer.user.email:
                generate_customer_report(customer, last_month_start, last_month_end)

    return f'monthly report generated at {datetime.now()}'
    
def generate_customer_report(customer, start_date, end_date):

    service_requests = ServiceRequest.query.filter(
        ServiceRequest.customer_id == customer.id,
        ServiceRequest.date_of_request >= start_date,
        ServiceRequest.date_of_request <= end_date
    ).all()
    
    # Calculate statistics
    total_requests = len(service_requests)
    completed_requests = sum(1 for req in service_requests if req.service_status in ['completed', 'closed'])
    total_cost = sum(req.service.base_price for req in service_requests)
    
    # Get average rating if the customer left reviews
    ratings = [review.rating for req in service_requests if req.review for review in [req.review]]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Generate the report HTML
    report_html = render_report_template(
        customer=customer,
        service_requests=service_requests,
        total_requests=total_requests,
        completed_requests=completed_requests,
        total_cost=total_cost,
        avg_rating=avg_rating,
        month_name=start_date.strftime("%B %Y")
    )
    
    # Optional: Convert HTML to PDF
    # pdf_file = convert_html_to_pdf(report_html)
    
    # Send the report by email
    month_name = start_date.strftime("%B %Y")
    subject = f"Your Monthly Activity Report - {month_name}"
    
    try:
        msg = Message(
            subject=subject,
            recipients=[customer.user.email],
            html=report_html,
            sender=os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')
        )
        
        # If using PDF:
        # if pdf_file:
        #     with app.open_resource(pdf_file) as fp:
        #         msg.attach(f"monthly_report_{month_name.replace(' ', '_')}.pdf", "application/pdf", fp.read())
        
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send report to {customer.user.email}: {str(e)}")


def render_report_template(customer, service_requests, total_requests, completed_requests, total_cost, avg_rating, month_name):
    """
    Renders the HTML template for the monthly report
    """
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Monthly Activity Report - {{ month_name }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #2c3e50; margin-bottom: 10px; }
            .summary { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
            .summary-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
            .summary-item { text-align: center; }
            .summary-item h3 { margin-bottom: 5px; color: #2980b9; }
            .requests-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
            .requests-table th { background-color: #2980b9; color: white; text-align: left; padding: 10px; }
            .requests-table td { border-bottom: 1px solid #ddd; padding: 10px; }
            .footer { margin-top: 50px; text-align: center; font-size: 12px; color: #7f8c8d; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Monthly Activity Report</h1>
                <p>{{ month_name }}</p>
                <p>Prepared for: {{ customer.user.username }}</p>
            </div>
            
            <div class="summary">
                <h2>Monthly Summary</h2>
                <div class="summary-grid">
                    <div class="summary-item">
                        <h3>{{ total_requests }}</h3>
                        <p>Total Service Requests</p>
                    </div>
                    <div class="summary-item">
                        <h3>{{ completed_requests }}</h3>
                        <p>Completed Requests</p>
                    </div>
                    <div class="summary-item">
                        <h3>${{ "%.2f"|format(total_cost) }}</h3>
                        <p>Total Service Cost</p>
                    </div>
                    <div class="summary-item">
                        <h3>{{ "%.1f"|format(avg_rating) }}/5</h3>
                        <p>Average Rating</p>
                    </div>
                </div>
            </div>
            
            <h2>Service Request Details</h2>
            {% if service_requests %}
            <table class="requests-table">
                <thead>
                    <tr>
                        <th>Service</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>
                    {% for request in service_requests %}
                    <tr>
                        <td>{{ request.service.name }}</td>
                        <td>{{ request.date_of_request.strftime('%Y-%m-%d') }}</td>
                        <td>{{ request.service_status }}</td>
                        <td>${{ "%.2f"|format(request.service.base_price) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>No service requests were made during this period.</p>
            {% endif %}
            
            <div class="footer">
                <p>Thank you for using A-Z Household Services!</p>
                <p>If you have any questions about this report, please contact customer support.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    template = jinja2.Template(template_str)
    return template.render(
        customer=customer,
        service_requests=service_requests,
        total_requests=total_requests,
        completed_requests=completed_requests,
        total_cost=total_cost,
        avg_rating=avg_rating,
        month_name=month_name
    )


def convert_html_to_pdf(html_content):
    """
    Converts HTML content to a PDF file
    Requires wkhtmltopdf to be installed: https://wkhtmltopdf.org/
    """
    try:
        # Create a temporary file for the PDF
        import tempfile
        temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_pdf.close()
        
        # Convert the HTML to PDF
        pdfkit.from_string(html_content, temp_pdf.name)
        
        return temp_pdf.name
    except Exception as e:
        print(f"Failed to convert HTML to PDF: {str(e)}")
        return None
        