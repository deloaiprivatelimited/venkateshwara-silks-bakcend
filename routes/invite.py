from flask import Blueprint, request, jsonify
import secrets
import os
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.invite_token import InviteToken

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
