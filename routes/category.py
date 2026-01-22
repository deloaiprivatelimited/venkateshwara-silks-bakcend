from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import DoesNotExist, ValidationError
from datetime import datetime
import pytz

from models.category import Category, AdminMeta
from models.admin_user import AdminUser
from models.saree import Saree

IST = pytz.timezone("Asia/Kolkata")

category_bp = Blueprint("category_bp", __name__)

@category_bp.route("/admin/category", methods=["POST"])
@jwt_required()
def add_category():
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"message": "Name is required"}), 400

    admin = AdminUser.objects(id=get_jwt_identity()).first()
    if not admin:
        return jsonify({"message": "Invalid admin"}), 401

    category = Category(
        name=name,
        admin=AdminMeta(
            username=admin.username,
            full_name=admin.full_name,
            last_edited_date=datetime.now(IST)
        )
    )
    category.save()

    return jsonify({"message": "Category created"}), 201


@category_bp.route("/admin/category/<category_id>", methods=["PUT"])
@jwt_required()
def edit_category(category_id):
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"message": "Name is required"}), 400

    try:
        category = Category.objects.get(id=category_id)
    except DoesNotExist:
        abort(404, "Category not found")

    admin = AdminUser.objects(id=get_jwt_identity()).first()

    category.name = name
    category.admin.username = admin.username
    category.admin.full_name = admin.full_name
    category.admin.last_edited_date = datetime.now(IST)
    category.save()

    return jsonify({"message": "Category updated"}), 200


@category_bp.route("/admin/category/<category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id):
    try:
        category = Category.objects.get(id=category_id)
    except DoesNotExist:
        abort(404, "Category not found")

    category.delete()
    return jsonify({"message": "Category deleted"}), 200


@category_bp.route("/admin/category/<category_id>/sarees", methods=["PUT"])
@jwt_required()
def update_category_sarees(category_id):
    data = request.json
    saree_ids = data.get("saree_ids", [])

    if not isinstance(saree_ids, list):
        return jsonify({"message": "saree_ids must be a list"}), 400

    try:
        category = Category.objects.get(id=category_id)
    except DoesNotExist:
        abort(404, "Category not found")

    sarees = Saree.objects(id__in=saree_ids)
    category.sarees = list(sarees)
    category.save()

    return jsonify({"message": "Sarees updated"}), 200


@category_bp.route("/admin/category/<category_id>/saree/<saree_id>", methods=["DELETE"])
@jwt_required()
def remove_saree_from_category(category_id, saree_id):
    try:
        category = Category.objects.get(id=category_id)
    except DoesNotExist:
        abort(404, "Category not found")

    try:
        saree = Saree.objects.get(id=saree_id)
    except DoesNotExist:
        abort(404, "Saree not found")

    if saree not in category.sarees:
        return jsonify({"message": "Saree not in category"}), 400

    category.sarees.remove(saree)
    category.save()

    return jsonify({"message": "Saree removed from category"}), 200



from flask import Blueprint, jsonify, abort, request
from flask_jwt_extended import jwt_required
from mongoengine.errors import DoesNotExist

from models.category import Category
from models.saree import Saree

@category_bp.route("/admin/category/<category_id>/sarees", methods=["GET"])
@jwt_required()
def fetch_sarees_by_category(category_id):
    try:
        category = Category.objects.get(id=category_id)
    except DoesNotExist:
        abort(404, "Category not found")

    sarees = category.sarees  # this is already a list of Saree objects

    data = [
       s.to_json()
        for s in sarees
    ]

    return jsonify({
        "category_id": str(category.id),
        "category_name": category.name,
        "total": len(data),
        "data": data
    }), 200
