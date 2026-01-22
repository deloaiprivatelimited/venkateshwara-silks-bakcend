from flask import Blueprint, request, jsonify
from models.saree import Saree
from models.variety import Variety
from mongoengine.queryset.visitor import Q

saree_bp = Blueprint("saree", __name__)

@saree_bp.route("/saree", methods=["POST"])
def add_saree():
    data = request.json

    # mandatory checks
    if not data.get("image_urls") or not data.get("variety"):
        return jsonify({"message": "image_urls and variety are mandatory"}), 400

    if data.get("min_price") is None or data.get("max_price") is None:
        return jsonify({"message": "min_price and max_price are mandatory"}), 400

    variety = Variety.objects(name=data["variety"]).first()
    if not variety:
        return jsonify({"message": "Variety not found"}), 400

    saree = Saree(
        name=data.get("name"),
        image_urls=data["image_urls"],
        variety=data["variety"],
        remarks=data.get("remarks"),
        min_price=data["min_price"],
        max_price=data["max_price"],
        status=data.get("status", "unpublished")
    )
    saree.save()

    variety.total_saree_count += 1
    variety.save()

    return jsonify(saree.to_json()), 201


@saree_bp.route("/saree/<string:saree_id>", methods=["PUT"])
def edit_saree(saree_id):
    data = request.json
    saree = Saree.objects(id=saree_id).first()

    if not saree:
        return jsonify({"message": "Saree not found"}), 404

    # variety change handling
    if "variety" in data and data["variety"] != saree.variety:
        new_variety = Variety.objects(name=data["variety"]).first()
        if not new_variety:
            return jsonify({"message": "Variety not found"}), 400

        old_variety = Variety.objects(name=saree.variety).first()
        if old_variety:
            old_variety.total_saree_count -= 1
            old_variety.save()

        new_variety.total_saree_count += 1
        new_variety.save()

        saree.variety = data["variety"]

    # updates
    for field in [
        "name", "image_urls", "remarks",
        "min_price", "max_price", "status"
    ]:
        if field in data:
            setattr(saree, field, data[field])

    saree.save()
    return jsonify(saree.to_json()), 200


@saree_bp.route("/saree/<string:saree_id>", methods=["DELETE"])
def delete_saree(saree_id):
    saree = Saree.objects(id=saree_id).first()
    if not saree:
        return jsonify({"message": "Saree not found"}), 404

    variety = Variety.objects(name=saree.variety).first()
    if variety:
        variety.total_saree_count -= 1
        variety.save()

    saree.delete()
    return jsonify({"message": "Saree deleted"}), 200


@saree_bp.route("/sarees", methods=["GET"])
def list_sarees():
    variety = request.args.get("variety")
    search = request.args.get("search")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    query = Q()

    if variety:
        query &= Q(variety=variety)

    if search:
        query &= Q(name__icontains=search)

    qs = Saree.objects(query).order_by("name")

    total = qs.count()
    sarees = qs.skip((page - 1) * per_page).limit(per_page)

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "data": [s.to_json() for s in sarees]
    }), 200
