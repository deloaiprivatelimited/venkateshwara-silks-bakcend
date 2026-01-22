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

import math

@category_bp.route("/admin/categories", methods=["GET"])
@jwt_required()
def get_categories():
    # --- Auth Admin ---
    admin = AdminUser.objects(id=get_jwt_identity()).first()
    if not admin:
        return jsonify({"message": "Invalid admin"}), 401

    # --- Query Params ---
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    search = request.args.get("search", "").strip()

    sort_by = request.args.get("sort_by", "name")  # name | total_saree_count
    order = request.args.get("order", "asc")       # asc | desc

    # Safety checks
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10
    if per_page > 100:
        per_page = 100

    # --- Base Query ---
    query = Category.objects()

    # --- Search Filter ---
    if search:
        query = query.filter(name__icontains=search)

    # --- Total Count (before pagination) ---
    total = query.count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1

    # --- Sorting ---
    # MongoEngine sorting supports fields only.
    # "total_saree_count" is derived, so we will sort manually after fetching a page.
    if sort_by == "name":
        mongo_sort = "name" if order == "asc" else "-name"
        query = query.order_by(mongo_sort)

        # Apply Pagination
        categories = query.skip((page - 1) * per_page).limit(per_page)

        data = []
        for c in categories:
            saree_count = len(c.sarees) if c.sarees else 0

            data.append({
                "id": str(c.id),
                "name": c.name,
                "total_saree_count": saree_count
            })

        return jsonify({
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "data": data
        }), 200

    # --- Sorting by total_saree_count (manual sorting) ---
    # For this, we fetch ALL (search filtered), compute counts, then sort in Python.
    # This is okay for small-medium datasets.
    if sort_by == "total_saree_count":
        categories_all = query  # filtered by search already

        data_all = []
        for c in categories_all:
            saree_count = len(c.sarees) if c.sarees else 0

            data_all.append({
                "id": str(c.id),
                "name": c.name,
                "total_saree_count": saree_count
            })

        reverse = True if order == "desc" else False
        data_all.sort(key=lambda x: x["total_saree_count"], reverse=reverse)

        # Manual pagination
        start = (page - 1) * per_page
        end = start + per_page
        data_page = data_all[start:end]

        return jsonify({
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "data": data_page
        }), 200

    # --- Invalid sort_by fallback ---
    return jsonify({
        "message": "Invalid sort_by. Allowed: name, total_saree_count"
    }), 400



import math
from flask import request, jsonify, abort
from flask_jwt_extended import jwt_required
from mongoengine.queryset.visitor import Q
from mongoengine.errors import DoesNotExist

from models.saree import Saree
from models.category import Category

@category_bp.route("/admin/category/<category_id>", methods=["GET"])
@jwt_required()
def get_category_details(category_id):
    try:
        category = Category.objects.get(id=category_id)
    except DoesNotExist:
        abort(404, "Category not found")

    return jsonify({
        "id": str(category.id),
        "name": category.name,
        "saree_ids": [str(s.id) for s in (category.sarees or [])]
    }), 200

@category_bp.route("/admin/category/<category_id>/sarees/picker", methods=["GET"])
@jwt_required()
def category_saree_picker(category_id):
    search = (request.args.get("search") or "").strip()
    variety = (request.args.get("variety") or "").strip()

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    # Safety
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10
    if per_page > 100:
        per_page = 100

    # --- Fetch Category ---
    try:
        category = Category.objects.get(id=category_id)
    except DoesNotExist:
        abort(404, "Category not found")

    selected_ids = [str(s.id) for s in (category.sarees or [])]

    # --- Base Query ---
    query = Q()
    if search:
        query &= Q(name__icontains=search)
    if variety:
        query &= Q(variety=variety)

    # --- Selected Sarees First ---
    selected_sarees = []
    if selected_ids:
        selected_sarees = list(Saree.objects(query & Q(id__in=selected_ids)))
        selected_map = {str(s.id): s for s in selected_sarees}
        selected_sarees = [selected_map[i] for i in selected_ids if i in selected_map]

    # --- Remaining Sarees (excluding selected) ---
    remaining_query = query
    if selected_ids:
        remaining_query &= Q(id__nin=selected_ids)

    remaining_qs = Saree.objects(remaining_query).order_by("name")

    # --- Counts ---
    total_selected = len(selected_sarees)
    total_remaining = remaining_qs.count()
    total = total_selected + total_remaining
    total_pages = math.ceil(total / per_page) if total > 0 else 1

    # --- Pagination ---
    skip = (page - 1) * per_page
    limit = per_page
    page_items = []

    # take from selected first
    if skip < total_selected:
        selected_slice = selected_sarees[skip: skip + limit]
        page_items.extend(selected_slice)
        limit -= len(selected_slice)
        skip = 0
    else:
        skip -= total_selected

    # take rest from remaining
    if limit > 0:
        remaining_slice = remaining_qs.skip(skip).limit(limit)
        page_items.extend(list(remaining_slice))

    return jsonify({
        "category_id": str(category.id),
        "category_name": category.name,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "selected_count": total_selected,
        "data": [s.to_json() for s in page_items]
    }), 200
