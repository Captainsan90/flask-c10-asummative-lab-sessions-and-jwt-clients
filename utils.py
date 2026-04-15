from functools import wraps

from flask import g, jsonify, request, session
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from extensions import db
from models import User


def get_authenticated_user():
    """
    Supports either:
    - Flask session auth via session['user_id']
    - JWT auth via Authorization: Bearer <token>
    """
    session_user_id = session.get("user_id")
    if session_user_id:
        user = db.session.get(User, session_user_id)
        if user:
            return user

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            if user_id is not None:
                return db.session.get(User, user_id)
        except Exception:
            return None

    return None


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_authenticated_user()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper