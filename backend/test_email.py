#!/usr/bin/env python3
"""
Test script for email sending functionality
Run this script to verify your email configuration is working properly
"""

import os
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_email(recipient=None, subject=None, body=None):
    """Test sending email with Flask-Mail"""
    print("Starting email test...")
    
    # Create a minimal Flask app
    app = Flask(__name__)
    
    # Configure Flask-Mail from environment or default values
    app.config.update(
        MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't'),
        MAIL_USERNAME=os.getenv('MAIL_USERNAME', ''),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD', ''),
        MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER', '')
    )
    
    # Print current config (without password)
    print(f"Mail Configuration:")
    print(f"  MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"  MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"  MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
    print(f"  MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"  MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
    
    # Initialize Flask-Mail
    mail = Mail(app)
    
    # Use recipient from args, or send to self
    if not recipient:
        recipient = app.config['MAIL_USERNAME']
    
    if not subject:
        subject = "A-Z Household Services: Email Configuration Test"
    
    if not body:
        body = """This is a test email from the A-Z Household Services application.
        
If you're receiving this, your email configuration is working correctly!

You can now use the email notification features in the application.
"""
    
    try:
        with app.app_context():
            print(f"Sending test email to: {recipient}")
            msg = Message(
                subject=subject,
                recipients=[recipient],
                body=body,
                sender=app.config['MAIL_DEFAULT_SENDER'] or app.config['MAIL_USERNAME']
            )
            mail.send(msg)
            print("Test email sent successfully!")
            return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Ensure 2-Step Verification is enabled on your Google account")
        print("2. Generate an App Password at https://myaccount.google.com/apppasswords")
        print("3. Use the App Password in your .env file, not your regular password")
        print("4. Check your .env file contains all required mail settings")
        return False

if __name__ == "__main__":
    import sys
    recipient = sys.argv[1] if len(sys.argv) > 1 else None
    test_email(recipient) 