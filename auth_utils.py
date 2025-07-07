"""
Authentication utilities for session-based user management
"""
import uuid
import logging
from functools import wraps
from flask import session, jsonify, request
from models import User, db


def require_user(f):
    """
    Decorator that ensures a valid user session exists before executing the route.
    Returns 401 if no session or user is found.
    Injects the user object as the first argument to the decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if session exists
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'error': 'Session not initialized. Please call /api/init first.'
            }), 401
        
        # Find user by session_id
        user = User.query.filter_by(session_id=session_id).first()
        if not user:
            return jsonify({
                'error': 'User not found. Please call /api/init to create a new session.'
            }), 401
        
        # Call the original function with user as first argument
        return f(user, *args, **kwargs)
    
    return decorated_function


def create_user_session():
    """
    Create a new user session and return the user object.
    This is used by the /api/init route.
    """
    try:
        # Generate new session ID
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        
        # Create user record
        user = User(session_id=session_id)
        db.session.add(user)
        db.session.commit()
        
        logging.info(f"Created new user with session_id: {session_id}")
        return user
        
    except Exception as e:
        logging.error(f"Error creating user session: {e}")
        db.session.rollback()
        raise


def get_current_user():
    """
    Get the current user from session without raising errors.
    Returns None if no user is found.
    """
    session_id = session.get('session_id')
    if not session_id:
        return None
    
    return User.query.filter_by(session_id=session_id).first()


def is_session_valid():
    """
    Check if the current session is valid (session exists and user exists).
    """
    session_id = session.get('session_id')
    if not session_id:
        return False
    
    user = User.query.filter_by(session_id=session_id).first()
    return user is not None