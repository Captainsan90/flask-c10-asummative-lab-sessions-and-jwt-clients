from flask import Blueprint, g, jsonify, request, session
from flask_jwt_extended import create_access_token

from extensions import db
from models import User
from utils import auth_required, get_authenticated_user

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    password_confirmation = data.get("password_confirmation") or ""

    if not username or not password or not password_confirmation:
        return jsonify({"error": "username, password, and password_confirmation are required"}), 400

    if password != password_confirmation:
        return jsonify({"error": "passwords do not match"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already exists"}), 409

    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    token = create_access_token(identity=user.id)

    return (
        jsonify(
            {
                "id": user.id,
                "username": user.username,
                "token": token,
                "user": user.to_dict(),
            }
        ),
        201,
    )


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    session["user_id"] = user.id
    token = create_access_token(identity=user.id)

    return (
        jsonify(
            {
                "id": user.id,
                "username": user.username,
                "token": token,
                "user": user.to_dict(),
            }
        ),
        200,
    )


@auth_bp.get("/me")
@auth_required
def me():
    user = g.current_user
    return jsonify(user.to_dict()), 200


@auth_bp.get("/check_session")
def check_session():
    user = get_authenticated_user()
    if not user:
        return jsonify({}), 200
    return jsonify(user.to_dict()), 200


@auth_bp.delete("/logout")
def logout():
    session.clear()
    return jsonify({}), 200