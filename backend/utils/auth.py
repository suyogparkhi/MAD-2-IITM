from flask import request, jsonify, current_app
from flask.globals import _request_ctx_stack
from flask_login import current_user
from models.models import User
from functools import wraps
import jwt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_jwt_token(token):
    try:
        logger.info(f"Verifying JWT token: {token[:10]}...")
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        logger.info(f"Token valid, payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return None

def get_current_user():
    """
    Get the current user from either session or JWT token
    """
    if current_user.is_authenticated:
        logger.info(f"User authenticated via session: {current_user.username} (ID: {current_user.id})")
        return current_user
    
    # Check if user is authenticated via JWT token
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        logger.info(f"Found token in Authorization header: {token[:10]}...")
        payload = verify_jwt_token(token)
        
        if payload:
            user_id = payload.get('user_id')
            if user_id:
                user = User.query.get(user_id)
                if user:
                    logger.info(f"User authenticated via token: {user.username} (ID: {user.id})")
                    return user
                else:
                    logger.warning(f"User ID {user_id} from token not found in database")
            else:
                logger.warning("No user_id in token payload")
        else:
            logger.warning("Invalid or expired token")
    else:
        logger.warning("No Authorization header with Bearer token found")
    
    return None

def role_required(role):
    """
    Decorator for checking if the user has the required role
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            
            if not user:
                logger.warning(f"Authentication required for {request.path}")
                return jsonify({'message': 'Authentication required'}), 401
            
            logger.info(f"Checking if user {user.username} has role: {role} (actual role: {user.role})")
            
            if role == 'admin' and not user.is_admin():
                logger.warning(f"Admin access required for {request.path}, but user is {user.role}")
                return jsonify({'message': 'Admin access required'}), 403
                
            if role == 'professional' and not user.is_professional():
                logger.warning(f"Professional access required for {request.path}, but user is {user.role}")
                return jsonify({'message': 'Professional access required'}), 403
                
            if role == 'customer' and not user.is_customer():
                logger.warning(f"Customer access required for {request.path}, but user is {user.role}")
                return jsonify({'message': 'Customer access required'}), 403
            
            # Set user for this request
            _request_ctx_stack.top.user = user
            logger.info(f"User {user.username} with role {user.role} granted access to {request.path}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Specific role decorators
def admin_required(f):
    return role_required('admin')(f)

def professional_required(f):
    return role_required('professional')(f)

def customer_required(f):
    return role_required('customer')(f) 