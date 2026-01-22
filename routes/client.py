from flask import Blueprint, request, jsonify
from models.saree import Saree
from models.variety import Variety
from mongoengine.errors import DoesNotExist, ValidationError

client_bp = Blueprint("client", __name__)

@client_bp.route("/client/sarees", methods=["GET", "OPTIONS"])
def list_sarees():
    # Pagination
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 12))

    # ✅ Filters
    # Old: ?variety=Silk
    variety = request.args.get("variety")

    # ✅ New: ?varieties=Silk,Cotton or ?varieties=Silk&varieties=Cotton
    varieties = request.args.getlist("varieties")

    # If sent as comma-separated in a single param
    if len(varieties) == 1 and "," in varieties[0]:
        varieties = [v.strip() for v in varieties[0].split(",") if v.strip()]

    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    query = Saree.objects(status="published")

    # ✅ Multiple varieties filter (OR)
    if varieties:
        query = query.filter(variety__in=varieties)

    # ✅ Backward compatibility (single variety)
    elif variety:
        query = query.filter(variety=variety)

    if min_price:
        query = query.filter(min_price__gte=float(min_price))

    if max_price:
        query = query.filter(max_price__lte=float(max_price))

    total = query.count()

    sarees = (
        query
        .skip((page - 1) * per_page)
        .limit(per_page)
        .order_by("-last_edited_at")
    )

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": total,
        "items": [s.to_json() for s in sarees]
    }), 200


@client_bp.route("/client/varieties", methods=["GET", "OPTIONS"])
def list_varieties():
    varieties = Variety.objects.only("name")

    return jsonify([
        {"id": str(v.id), "name": v.name}
        for v in varieties
    ]), 200


@client_bp.route("/client/sarees/<string:saree_id>", methods=["GET", "OPTIONS"])
def get_saree_by_id(saree_id):
    try:
        saree = Saree.objects.get(id=saree_id, status="published")
    except (DoesNotExist, ValidationError):
        return jsonify({"message": "Saree not found"}), 404

    return jsonify(saree.to_json()), 200
