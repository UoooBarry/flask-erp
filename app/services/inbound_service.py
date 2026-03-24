from sqlalchemy import func
from app.models.inbound_order import InboundStatus
from app.models.purchase_order import POStatus
from app.extensions import db
from app.services import StockService
from app.models import (
    InboundOrder,
    PurchaseOrderItem,
    InboundItem,
)
from app.utils.decorator import retry_on_concurrency

class InboundService:
    @staticmethod
    @retry_on_concurrency(max_retries=5)
    def process_inbound(inbound_order_id, items_to_receive):
        """
        items_to_receive: [{'sku': 'SKU001', 'received_qty': 10}, ...]
        """
        from app.models import Product

        inbound_order = db.session.get(InboundOrder, inbound_order_id)
        if not inbound_order:
            raise ValueError("Inbound order not found")

        if inbound_order.status == InboundStatus.COMPLETED:
            raise ValueError("Inbound order already completed")

        po = inbound_order.purchase_order

        skus = [data["sku"] for data in items_to_receive]
        products = Product.query.filter(Product.sku.in_(skus)).all()
        products_map = {product.sku: product for product in products}

        for data in items_to_receive:
            product = products_map.get(data["sku"])
            if not product:
                raise ValueError(f"Product with SKU {data['sku']} not found")

            qty = data["received_qty"]

            po_item = PurchaseOrderItem.query.filter_by(
                purchase_order_id=po.id,
                product_id=product.id
            ).first()

            if not po_item:
                raise ValueError(f"Product {product.sku} not in purchase order")

            if po_item.received_quantity + qty > po_item.quantity:
                raise ValueError(f"Over-receiving for product {product.sku}")

            StockService.update_inventory(product.id, po.warehouse_id, qty)

            inbound_item = InboundItem(
                inbound_order_id=inbound_order.id, quantity=qty, purchase_order_item_id=po_item.id
            )
            po_item.received_quantity += qty

            db.session.add(inbound_item)

        inbound_order.status = InboundStatus.COMPLETED
        InboundService._update_po_status(po)

        db.session.commit()

    @staticmethod
    def _update_po_status(po):
        db.session.flush()
        po_items = PurchaseOrderItem.query.filter_by(purchase_order_id=po.id).all()
        all_done = all(item.received_quantity >= item.quantity for item in po_items)
        any_done = any(item.received_quantity > 0 for item in po_items)

        if all_done:
            po.status = POStatus.COMPLETED
        elif any_done:
            po.status = POStatus.PARTIAL
