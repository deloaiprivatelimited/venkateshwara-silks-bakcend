from flask import Blueprint, request, jsonify
from models.admin_user import AdminUser
from flask_jwt_extended import create_access_token
import os

admin_auth_bp = Blueprint("admin_auth", __name__)

SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")


@admin_auth_bp.route("/admin/login", methods=["POST"])
def admin_login():

    data = request.json
    username = data.get("username")
    password = data.get("password")

    admin = AdminUser.objects(username=username, password=password).first()

    if not admin:
        return jsonify({"message": "Invalid username or password"}), 401

    token = create_access_token(identity=str(admin.id))

    return jsonify({
        "token": token,
        "admin": admin.to_json()
    }), 200
