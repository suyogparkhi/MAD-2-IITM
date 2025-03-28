# A-Z Household Services Application

A comprehensive service management system for household services, connecting customers with professionals, and providing administrative tools for business management.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Setup Instructions](#setup-instructions)
   - [Backend Setup](#backend-setup)
   - [Frontend Setup](#frontend-setup)
   - [Redis Setup](#redis-setup)
   - [Celery Setup](#celery-setup)
   - [Email Configuration](#email-configuration)
3. [Running the Application](#running-the-application)
4. [Shutting Down](#shutting-down)
5. [Key Features](#key-features)
6. [Admin Features](#admin-features)
7. [Background Processing](#background-processing)
8. [API Documentation](#api-documentation)
9. [Troubleshooting](#troubleshooting)
10. [License](#license)

## System Requirements

- Python 3.8+ (Backend)
- Node.js 14+ and npm/yarn (Frontend)
- Redis 6.0+ (For caching and Celery)
- SMTP server access (For email notifications)
- SQLite (Default) or PostgreSQL (Optional for production)

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd /path/to/MAD\ 2/backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the template:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file to configure your environment:
   - Set a strong SECRET_KEY
   - Configure database settings if using something other than SQLite
   - Configure email settings (see Email Configuration section)

6. Create the database structure:
   ```
   flask db upgrade
   ```

7. (Optional) Load sample data:
   ```
   python seed_data.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd /path/to/MAD\ 2/frontend
   ```

2. Install the required packages:
   ```
   npm install
   # or if using yarn
   yarn
   ```

3. Create a `.env` file for frontend configuration:
   ```
   cp .env.example .env
   ```

### Redis Setup

Redis is used for both caching and as a message broker for Celery.

1. Install Redis:
   - **macOS** (using Homebrew):
     ```
     brew install redis
     ```
   - **Linux** (Ubuntu):
     ```
     sudo apt-get install redis-server
     ```
   - **Windows**: Download the Windows port from https://github.com/microsoftarchive/redis/releases

2. Start Redis:
   - **macOS/Linux**:
     ```
     redis-server
     ```
   - **macOS** (as service):
     ```
     brew services start redis
     ```
   - **Linux** (as service):
     ```
     sudo systemctl start redis
     ```
   - **Windows**:
     Run the `redis-server.exe` file

3. Verify Redis is running:
   ```
   redis-cli ping
   ```
   You should receive `PONG` as a response.

### Celery Setup

Celery is used for handling background tasks like export jobs and scheduled reports.

1. Make sure Redis is running (see Redis Setup)

2. Navigate to the backend directory:
   ```
   cd /path/to/MAD\ 2/backend
   ```

3. Install Celery (should already be included in requirements.txt):
   ```
   pip install celery
   ```

4. For PDF generation (used in reports), install reportlab:
   ```
   pip install reportlab
   ```

### Email Configuration

The application sends emails for various purposes, including export notifications and reports.

1. In your `.env` file, configure the following settings:
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_DEFAULT_SENDER=your_email@gmail.com
   ```

2. For Gmail users:
   - Enable 2-Step Verification at https://myaccount.google.com/security
   - Create an "App Password" at https://myaccount.google.com/apppasswords
   - Use that password in your `.env` file instead of your regular password

### Fixing Email Configuration Issues

If you see errors like "Username and Password not accepted" when sending emails:

1. **For Gmail accounts**:
   - Make sure 2-Step Verification is enabled in your Google Account
   - Generate a specific "App Password" for this application:
     1. Go to your Google Account → Security
     2. Under "Signing in to Google", select "App passwords" (requires 2-Step Verification to be enabled)
     3. Select "Mail" as the app and "Other" as the device (name it "A-Z Household Services")
     4. Click "Generate" and copy the 16-character password
     5. Use this password in your `.env` file for `MAIL_PASSWORD`
   - Ensure `MAIL_USERNAME` is your complete Gmail address
   - If still having issues, check if "Less secure app access" needs to be enabled (though this is not recommended)

2. **For Other Email Providers**:
   - Check your email provider's documentation for SMTP settings
   - Some providers require specific ports or security settings
   - You may need to enable SMTP access in your email account settings

3. **Testing Email Configuration**:
   You can test your email configuration by running this one-time script:
   ```python
   cd /path/to/MAD\ 2/backend
   python -c "
   from flask import Flask
   from flask_mail import Mail, Message
   app = Flask(__name__)
   app.config.update(
       MAIL_SERVER = 'smtp.gmail.com',
       MAIL_PORT = 587,
       MAIL_USE_TLS = True,
       MAIL_USERNAME = 'your_email@gmail.com',  # Replace with your email
       MAIL_PASSWORD = 'your_app_password'      # Replace with your app password
   )
   mail = Mail(app)
   with app.app_context():
       msg = Message('Test Email', sender='your_email@gmail.com', recipients=['your_email@gmail.com'])
       msg.body = 'This is a test email from A-Z Household Services app.'
       mail.send(msg)
       print('Test email sent!')
   "
   ```

## Running the Application

### 1. Start Redis

If not already running as a service:

```
redis-server
```

### 2. (Optional) Test the Email Configuration

Before starting the Celery workers, it's a good idea to test your email configuration:

```
cd /path/to/MAD\ 2/backend
source venv/bin/activate  # If using virtual environment
python test_email.py
```

If successful, you'll see "Test email sent successfully!" and receive a test email.
If it fails, follow the troubleshooting tips displayed in the console.

### 3. Start the Celery Worker

Open a new terminal window and run:

```
cd /path/to/MAD\ 2/backend
source venv/bin/activate  # If using virtual environment
celery -A tasks.export_tasks worker --loglevel=info
```

### 4. Start the Celery Beat Scheduler (for periodic tasks)

Open another terminal window and run:

```
cd /path/to/MAD\ 2/backend
source venv/bin/activate  # If using virtual environment
celery -A tasks.export_tasks beat --loglevel=info
```

### 5. Start the Backend Server

Open a new terminal window and run:

```
cd /path/to/MAD\ 2/backend
source venv/bin/activate  # If using virtual environment
python app.py
```

The backend will start on http://localhost:5000 by default.

### 6. Start the Frontend Development Server

Open a new terminal window and run:

```
cd /path/to/MAD\ 2/frontend
npm run serve
# or if using yarn
yarn serve
```

The frontend will start on http://localhost:8080 by default.

### 7. Access the Application

Open your browser and navigate to:
- Frontend: http://localhost:8080
- Backend API: http://localhost:5000/api

## Shutting Down

To properly shut down all components:

### 1. Stop the Frontend Server

Press `Ctrl+C` in the terminal where the frontend server is running.

### 2. Stop the Backend Server

Press `Ctrl+C` in the terminal where the backend server is running.

### 3. Stop the Celery Worker

Press `Ctrl+C` in the terminal where the Celery worker is running.

### 4. Stop the Celery Beat Scheduler

Press `Ctrl+C` in the terminal where the Celery beat scheduler is running.

### 5. Stop Redis

If started manually:
- Press `Ctrl+C` in the terminal where Redis is running.

If started as a service:
- **macOS**:
  ```
  brew services stop redis
  ```
- **Linux**:
  ```
  sudo systemctl stop redis
  ```
- **Windows**:
  Close the Redis server window.

## Key Features

- **Service Management**: Browse, search, and request household services
- **Professional Management**: Register as a professional, manage service requests
- **Customer Management**: Place service requests, track status, review completed services
- **Admin Dashboard**: Manage services, professionals, customers, and service requests
- **Reporting**: Generate CSV exports and PDF reports for business analytics
- **Background Processing**: Asynchronously process reports and exports
- **Email Notifications**: Receive notifications for various events

## Admin Features

### Reporting and Export System

The application includes a robust reporting and export system:

1. **CSV Exports**:
   - Export service requests filtered by date range, status, or service type
   - Exports run as background jobs using Celery
   - Email notifications when exports are complete

2. **Monthly Reports**:
   - Automatically generated on the first day of each month
   - Available in both HTML and PDF formats
   - Includes service performance metrics

3. **Custom Reports**:
   - Generate reports for specific date ranges
   - Multiple report types: Service Performance, Customer Activity, Professional Performance
   - PDF output with formatted tables and charts

### How to Use the Export System

1. Navigate to the Admin Dashboard
2. Click on "Reports" in the navigation menu
3. Select the "Export Data" tab
4. Configure your export parameters:
   - Select a date range
   - Choose a status filter
   - Select a service type
   - (Optional) Enter an email to receive notification
5. Click "Generate CSV Export"
6. The export will process in the background
7. Once complete, download the file from the "Recent Export Jobs" table

## Background Processing

The application uses Celery for handling background tasks:

### Scheduled Tasks

1. **Daily Reminders**:
   - Checks for pending service requests
   - Sends reminders to professionals
   - Runs daily at a configured time

2. **Monthly Reports**:
   - Generates monthly activity reports
   - Runs on the 1st day of each month

### User-Triggered Tasks

1. **Export Service Requests**:
   - Admin triggers export through the UI
   - Data is exported as CSV
   - Email notification when export is complete

2. **Generate Custom Reports**:
   - Admin requests custom report
   - Report is generated as PDF
   - Available for download when complete

## API Documentation

API documentation can be accessed at `/api/docs` when the backend server is running.

## Troubleshooting

### Common Issues

1. **Redis Connection Error**:
   - Make sure Redis is running
   - Check the Redis URL in your `.env` file

2. **Celery Worker Not Processing Tasks**:
   - Ensure you're running the worker from the correct directory
   - Verify Redis is running
   - Check that you're using the correct Celery application

3. **Email Sending Fails**:
   - Verify your email credentials in `.env`
   - For Gmail, make sure you're using an App Password if 2FA is enabled
   - Check your mail server's security settings
   - If you see "Username and Password not accepted" error with Gmail:
     - This almost always means you need to use an App Password instead of your regular password
     - App Passwords are 16-character codes generated specifically for less secure apps
     - Regular passwords will not work with Gmail SMTP if 2FA is enabled
     - Run the `test_email.py` script to debug your email configuration

4. **PDF Generation Issues**:
   - Ensure reportlab is installed: `pip install reportlab`
   - Check permissions for the exports directory

5. **Export Jobs Stuck in "Processing" State**:
   - Make sure the Celery worker is running
   - Check Celery logs for errors

### Logging

Logs are stored in the following locations:
- Backend: `/path/to/MAD 2/backend/logs`
- Celery Worker: Console output (can be redirected to a file)
- Redis: System logs or console output

## License

This project is licensed under the MIT License - see the LICENSE file for details. 

## Contributors

- Your Name
- Your Team Members

---

For any questions or support, please contact [your-email@example.com] 