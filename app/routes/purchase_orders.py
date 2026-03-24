from app.schemas import PurchaseOrderResponse
from app.models.purchase_order import PurchaseOrder
from app.extensions import db
from flask import Blueprint
from app.utils.exceptions import NotFoundError
from app.utils.response import render_success

purchase_orders_bp = Blueprint("purchase_orders", __name__)


@purchase_orders_bp.route("/<int:purchase_order_id>", methods=["GET"])
def get_purchase_order(purchase_order_id):
    purchase_order = db.session.get(PurchaseOrder, purchase_order_id)
    if not purchase_order:
        raise NotFoundError(f"Purchase order #{purchase_order_id} not found.")

    data = PurchaseOrderResponse.model_validate(purchase_order).model_dump()

    return render_success(data)
