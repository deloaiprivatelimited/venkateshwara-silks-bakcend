from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models.category import Category
from models.saree import Saree
from models.variety import Variety

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route(
    "/admin/dashboard/stats",
    methods=["GET", "OPTIONS"]
)
@jwt_required()
def dashboard_stats():
    category_count = Category.objects.count()
    saree_count = Saree.objects.count()
    variety_count = Variety.objects.count()

    return jsonify({
        "categories": category_count,
        "sarees": saree_count,
        "varieties": variety_count
    }), 200
