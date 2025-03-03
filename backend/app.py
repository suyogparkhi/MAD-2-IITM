import os 
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from models.models import db, User
from cache.cache_config import init_cache
from flask_cors import CORS

load_dotenv()


def create_app():

    app = Flask(__name__,
                static_folder = '../frontend/dist/assets',
                template_folder = '../frontend/dist')
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY' , 'dev_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI' , 'sqlite:///household_services.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure CORS to allow requests from the frontend
    CORS(app, 
         supports_credentials=True, 
         origins=["http://localhost:8080"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"])

    db.init_app(app)
    migrate = Migrate(app, db)
    cache = init_cache(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
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
    
    