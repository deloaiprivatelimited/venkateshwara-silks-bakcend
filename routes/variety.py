from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.variety import Variety, AdminMeta
from models.admin_user import AdminUser
from datetime import datetime
import pytz
from models.saree import Saree


IST = pytz.timezone("Asia/Kolkata")

variety_bp = Blueprint("variety_bp", __name__)

@variety_bp.route("/admin/variety", methods=["POST"])
@jwt_required()
def add_variety():
    data = request.json
    name = data.get("name")

    admin = AdminUser.objects(id=get_jwt_identity()).first()

    variety = Variety(
        name=name,
        admin=AdminMeta(
            username=admin.username,
            full_name=admin.full_name,
            last_edited_date=datetime.now(IST)
        )
    )
    variety.save()

    return jsonify({"message": "Variety added"}), 201

@variety_bp.route("/admin/variety/<variety_id>", methods=["PUT"])
@jwt_required()
def edit_variety(variety_id):
    data = request.json
    name = data.get("name")

    admin = AdminUser.objects(id=get_jwt_identity()).first()
    variety = Variety.objects(id=variety_id).first()
    if not variety:
        return jsonify({"message": "Variety not found"}), 404

    variety.name = name
    variety.admin.username = admin.username
    variety.admin.full_name = admin.full_name
    variety.admin.last_edited_date = datetime.now(IST)

    variety.save()
    Saree.objects(variety=variety.name).update(set__variety=name)


    return jsonify({"message": "Variety updated"}), 200


@variety_bp.route("/admin/varieties", methods=["GET"])
@jwt_required()
def list_varieties():
    search = request.args.get("search", "")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    sort_by = request.args.get("sort_by", "name")  # name | total_saree_count
    order = request.args.get("order", "asc")       # asc | desc

    query = Variety.objects(name__icontains=search)

    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    query = query.order_by(sort_field)

    total = query.count()
    varieties = query.skip((page - 1) * per_page).limit(per_page)

    data = [
        {
            "id": str(v.id),
            "name": v.name,
            "total_saree_count": v.total_saree_count
        }
        for v in varieties
    ]

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "data": data
    }), 200
