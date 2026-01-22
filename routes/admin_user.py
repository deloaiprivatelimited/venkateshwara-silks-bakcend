from flask import Blueprint, request, jsonify
from models.admin_user import AdminUser
import os

admin_bp = Blueprint("admin_user", __name__)

SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")
@admin_bp.route("/admin-user", methods=["POST"])
def create_admin_user():
    if request.args.get("secret") != SECRET_KEY:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json

    admin = AdminUser(
        username=data["username"],
        full_name=data["full_name"],
        password=data["password"]
    )
    admin.save()

    return jsonify(admin.to_json()), 201


@admin_bp.route("/admin-user", methods=["GET"])
def list_admin_users():
    if request.args.get("secret") != SECRET_KEY:
        return jsonify({"message": "Unauthorized"}), 401

    users = AdminUser.objects()
    return jsonify([u.to_json() for u in users]), 200


@admin_bp.route("/admin-user/<string:user_id>", methods=["DELETE"])
def delete_admin_user(user_id):
    if request.args.get("secret") != SECRET_KEY:
        return jsonify({"message": "Unauthorized"}), 401

    user = AdminUser.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    user.delete()
    return jsonify({"message": "User deleted"}), 200
