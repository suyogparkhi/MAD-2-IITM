import os 
from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from models.models import db, User
from cache.cache_config import init_cache
from flask_cors import CORS
from flask_mail import Mail
from tasks.celery_config import make_celery

load_dotenv()

# Initialize Flask-Mail outside of create_app for Celery tasks
mail = Mail()

def create_app():
    app = Flask(__name__,
                static_folder = '../frontend/dist/assets',
                template_folder = '../frontend/dist')
    
    # Flask Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY' , 'dev_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI' , 'sqlite:///household_services.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure Mail
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'youremail@gmail.com')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'yourpassword')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@household-services.com')

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    mail.init_app(app)  # Initialize mail with app
    cache = init_cache(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    # Configure CORS to allow requests from the frontend
    CORS(app, 
         supports_credentials=True, 
         origins=["http://localhost:8080", "http://127.0.0.1:8080", 
                 "http://localhost:5000", "http://127.0.0.1:5000",
                 "http://localhost:5001", "http://127.0.0.1:5001"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"])
    
    # Initialize Celery
    celery = make_celery(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.professional_routes import professional_bp
    from routes.customer_routes import customer_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(professional_bp, url_prefix='/api/professional')
    app.register_blueprint(customer_bp, url_prefix='/api/customer')

    # Add route to serve uploaded documents
    @app.route('/uploads/documents/<path:filename>')
    def serve_document(filename):
        return send_from_directory(os.path.join(app.root_path, 'uploads', 'documents'), filename)
    
    # Create exports directory if it doesn't exist
    os.makedirs(os.path.join(app.root_path, 'exports'), exist_ok=True)

    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')  # In production, use a secure password
            db.session.add(admin)
            db.session.commit()
    
    return app
    
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
    
    