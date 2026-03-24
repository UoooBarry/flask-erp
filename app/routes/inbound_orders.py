from app.extensions import db
from pydantic import ValidationError
from app.schemas import InboundOrderCreate, InboundOrderResponse, InboundOrderReceive
from app.models import InboundOrder, InboundItem
from app.services import InboundService
from flask import Blueprint, request
from app.utils.response import render_success

inbound_orders_bp = Blueprint("inbound_orders", __name__)

@inbound_orders_bp.route("/", methods=["POST"])
def create_inbound_order():
    data = request.get_json()

    if not data:
        raise ValidationError("Request body is required")

    validated_data = InboundOrderCreate(**data)
    inbound_order = InboundOrder(
        purchase_order_id=validated_data.purchase_order_id,
        notes=validated_data.notes,
        received_date=validated_data.received_date,
    )

    db.session.add(inbound_order)
    db.session.commit()

    return render_success(
        InboundOrderResponse.model_validate(inbound_order).model_dump(), status_code=201
    )

@inbound_orders_bp.route("/receive", methods=["POST"])
def receive_goods():
    data = request.get_json()

    if not data:
        raise ValidationError("Request body is required")

    validated_data = InboundOrderReceive(**data)
    items_to_receive = [{"sku": item.sku, "received_qty": item.received_qty} for item in validated_data.items]

    InboundService.process_inbound(validated_data.inbound_order_id, items_to_receive)

    inbound_order = db.session.get(InboundOrder, validated_data.inbound_order_id)

    return render_success(
        InboundOrderResponse.model_validate(inbound_order).model_dump()
    )
