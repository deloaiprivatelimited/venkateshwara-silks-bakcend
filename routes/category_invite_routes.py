from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import secrets
import os

from models.invite_token import CategoryInviteToken
from models.category import Category

category_invite_bp = Blueprint("category_invite_bp", __name__)
@category_invite_bp.route("/invite/category/create", methods=["POST"])
@jwt_required()
def create_category_invite():
    data = request.get_json() or {}
    category_id = data.get("category_id")

    if not category_id:
        return jsonify({"msg": "category_id required"}), 400

    category = Category.objects(id=category_id).first()
    if not category:
        return jsonify({"msg": "Category not found"}), 404

    token = secrets.token_urlsafe(16)

    CategoryInviteToken(
        token=token,
        category=category,
        is_active=True
    ).save()

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

    return jsonify({
        "token": token,
        "category_id": str(category.id),
        "category_name": category.name,
        "link": f"{frontend_url}/catalog/{category.id}?token={token}"
    }), 201


@category_invite_bp.route("/api/category-invite/verify", methods=["POST"])
def verify_category_invite():
    data = request.get_json() or {}
    token = data.get("token")
    device_id = data.get("device_id")
    category_id = data.get("category_id")

    if not token or not device_id or not category_id:
        return jsonify({"allowed": False, "msg": "Missing required fields"}), 400

    invite = CategoryInviteToken.objects(
        token=token,
        is_active=True,
        category=category_id
    ).first()

    if not invite:
        return jsonify({"allowed": False, "msg": "Invalid / Expired link"}), 403

    # Lock first time
    if not invite.locked_device_id:
        invite.locked_device_id = device_id
        invite.save()
        return jsonify({"allowed": True}), 200

    if invite.locked_device_id != device_id:
        return jsonify({
            "allowed": False,
            "msg": "Link already used on another device"
        }), 403

    return jsonify({"allowed": True}), 200


@category_invite_bp.route("/api/category-invite/disable", methods=["POST"])
@jwt_required()
def disable_category_invite():
    data = request.get_json() or {}
    token = data.get("token")

    if not token:
        return jsonify({"msg": "token required"}), 400

    invite = CategoryInviteToken.objects(token=token).first()
    if not invite:
        return jsonify({"msg": "Token not found"}), 404

    invite.is_active = False
    invite.save()

    return jsonify({"msg": "Category token disabled"}), 200
