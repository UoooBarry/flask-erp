from app.models.stock import Stock
from app.extensions import db
from app.utils.decorator import retry_on_concurrency

class StockService:
    @staticmethod
    @retry_on_concurrency(max_retries=5)
    def update_inventory(product_id, warehouse_id, increment):
        item = Stock.query.filter_by(
            product_id=product_id, warehouse_id=warehouse_id
        ).first()

        if not item:
            item = Stock(product_id=product_id, warehouse_id=warehouse_id, quantity=increment)
            item.version = 0
            db.session.add(item)
            db.session.commit()
            return item

        new_quantity = item.quantity + increment
        if new_quantity < 0:
            raise ValueError(
                f"Insufficient stock for {item.product.sku}, current: {item.quantity}"
            )

        item.quantity = new_quantity
        db.session.commit()

        return item
