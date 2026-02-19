from flask import Blueprint, request, jsonify
import secrets
import os
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.invite_token import InviteToken, CategoryInviteToken
from models.category import Category
from mongoengine.errors import DoesNotExist, ValidationError

invite_bp = Blueprint("invite_bp", __name__)


@invite_bp.route("/invite/create", methods=["POST"])
@jwt_required()
def create_invite():
    token = secrets.token_urlsafe(16)

    InviteToken(
        token=token,
        is_active=True
    ).save()

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

    return jsonify({
        "token": token,
        "link": f"{frontend_url}/catalog?token={token}"
    }), 201


@invite_bp.route("/api/invite/verify", methods=["POST"])
def verify_invite():
    data = request.get_json() or {}
    token = data.get("token")
    device_id = data.get("device_id")

    if not token or not device_id:
        return jsonify({"allowed": False, "msg": "token and device_id required"}), 400

    invite = InviteToken.objects(token=token, is_active=True).first()
    if not invite:
        return jsonify({"allowed": False, "msg": "Invalid / Expired link"}), 403

    # ✅ first time use => lock to device
    if not invite.locked_device_id:
        invite.locked_device_id = device_id
        invite.save()
        return jsonify({"allowed": True, "msg": "Link locked to this device"}), 200

    # ✅ already locked => allow only same device
    if invite.locked_device_id != device_id:
        return jsonify({
            "allowed": False,
            "msg": "This link is already used on another device"
        }), 403

    return jsonify({"allowed": True, "msg": "Access allowed"}), 200


@invite_bp.route("/api/invite/disable", methods=["POST"])
def disable_invite():
    data = request.get_json() or {}
    token = data.get("token")

    if not token:
        return jsonify({"msg": "token required"}), 400

    invite = InviteToken.objects(token=token).first()
    if not invite:
        return jsonify({"msg": "Token not found"}), 404

    invite.is_active = False
    invite.save()

    return jsonify({"msg": "Token disabled"}), 200


# ✅ CATEGORY-WISE INVITE ENDPOINTS

@invite_bp.route("/invite/category/create", methods=["POST"])
@jwt_required()
def create_category_invite():
    data = request.get_json() or {}
    category_ids = data.get("category_ids", [])  # List of category IDs

    if not category_ids:
        return jsonify({"msg": "category_ids required"}), 400

    # Validate all categories exist
    categories = Category.objects(id__in=category_ids)
    if len(categories) != len(category_ids):
        return jsonify({"msg": "One or more categories not found"}), 404

    token = secrets.token_urlsafe(16)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Create invite tokens for each category
    created_invites = []
    for category in categories:
        CategoryInviteToken(
            token=token,
            category=category,
            is_active=True
        ).save()
        created_invites.append({
            "category_id": str(category.id),
            "category_name": category.name
        })

    return jsonify({
        "token": token,
        "link": f"{frontend_url}/catalog?token={token}",
        "categories": created_invites
    }), 201


@invite_bp.route("/api/invite/category/verify", methods=["POST"])
def verify_category_invite():
    data = request.get_json() or {}
    token = data.get("token")
    device_id = data.get("device_id")

    if not token or not device_id:
        return jsonify({"allowed": False, "msg": "token and device_id required"}), 400

    # Get all category invites for this token
    invites = CategoryInviteToken.objects(token=token, is_active=True)
    if not invites:
        return jsonify({"allowed": False, "msg": "Invalid / Expired link"}), 403

    # First time use => lock to device
    if not invites[0].locked_device_id:
        for invite in invites:
            invite.locked_device_id = device_id
            invite.save()
        return jsonify({
            "allowed": True,
            "msg": "Link locked to this device",
            "token": token
        }), 200

    # Already locked => allow only same device
    if invites[0].locked_device_id != device_id:
        return jsonify({
            "allowed": False,
            "msg": "This link is already used on another device"
        }), 403

    return jsonify({
        "allowed": True,
        "msg": "Access allowed",
        "token": token
    }), 200


@invite_bp.route("/api/invite/category/disable", methods=["POST"])
def disable_category_invite():
    data = request.get_json() or {}
    token = data.get("token")

    if not token:
        return jsonify({"msg": "token required"}), 400

    invites = CategoryInviteToken.objects(token=token)
    if not invites:
        return jsonify({"msg": "Token not found"}), 404

    for invite in invites:
        invite.is_active = False
        invite.save()

    return jsonify({"msg": "Token disabled"}), 200
