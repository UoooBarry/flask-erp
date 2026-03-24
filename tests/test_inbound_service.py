import pytest
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from app.services import InboundService
from app.models import InboundOrder, PurchaseOrder, PurchaseOrderItem, Product, Warehouse
from app.extensions import db


class TestInboundService:
    def test_process_inbound_with_sku(self, purchase_order_setup):
        warehouse, product, po, po_item = purchase_order_setup

        inbound_order = InboundOrder(
            purchase_order_id=po.id,
            received_date=datetime.now(timezone.utc),
            notes="Test inbound"
        )
        inbound_order.version = 0
        db.session.add(inbound_order)
        db.session.commit()

        items_to_receive = [
            {"sku": product.sku, "received_qty": 50}
        ]

        InboundService.process_inbound(inbound_order.id, items_to_receive)

        db.session.refresh(inbound_order)
        assert inbound_order.status.value == "completed"

        db.session.refresh(po_item)
        assert po_item.received_quantity == 50

        from app.models import Stock
        stock = Stock.query.filter_by(
            product_id=product.id,
            warehouse_id=warehouse.id
        ).first()
        assert stock is not None
        assert stock.quantity == 50

    def test_process_inbound_invalid_sku(self, purchase_order_setup):
        warehouse, product, po, po_item = purchase_order_setup

        inbound_order = InboundOrder(
            purchase_order_id=po.id,
            received_date=datetime.now(timezone.utc),
            notes="Test inbound"
        )
        inbound_order.version = 0
        db.session.add(inbound_order)
        db.session.commit()

        items_to_receive = [
            {"sku": "INVALID-SKU", "received_qty": 50}
        ]

        with pytest.raises(ValueError) as exc_info:
            InboundService.process_inbound(inbound_order.id, items_to_receive)

        assert "not found" in str(exc_info.value)

    def test_process_inbound_over_receive(self, purchase_order_setup):
        warehouse, product, po, po_item = purchase_order_setup

        inbound_order = InboundOrder(
            purchase_order_id=po.id,
            received_date=datetime.now(timezone.utc),
            notes="Test inbound"
        )
        inbound_order.version = 0
        db.session.add(inbound_order)
        db.session.commit()

        items_to_receive = [
            {"sku": product.sku, "received_qty": 150}
        ]

        with pytest.raises(ValueError) as exc_info:
            InboundService.process_inbound(inbound_order.id, items_to_receive)

        assert "Over-receiving" in str(exc_info.value)


@pytest.mark.skip(reason="SQLite has limited concurrent write support")
class TestInboundServiceRaceConditions:
    def test_concurrent_same_inbound_order(self, app, purchase_order_setup):
        warehouse, product, po, po_item = purchase_order_setup

        from app.models import Stock
        stock = Stock(product_id=product.id, warehouse_id=warehouse.id, quantity=0)
        stock.version = 0
        db.session.add(stock)
        db.session.commit()

        inbound_order = InboundOrder(
            purchase_order_id=po.id,
            received_date=datetime.now(timezone.utc),
            notes="Test inbound"
        )
        inbound_order.version = 0
        db.session.add(inbound_order)
        db.session.commit()

        items_to_receive = [
            {"sku": product.sku, "received_qty": 30}
        ]

        num_threads = 2
        barrier = threading.Barrier(num_threads)
        success_count = [0]
        error_count = [0]

        def process_inbound(thread_id):
            with app.app_context():
                barrier.wait()
                try:
                    InboundService.process_inbound(inbound_order.id, items_to_receive)
                    success_count[0] += 1
                except ValueError as e:
                    error_count[0] += 1

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(process_inbound, i)
                for i in range(num_threads)
            ]
            for future in as_completed(futures):
                future.result()

        assert success_count[0] == 1
        assert error_count[0] == 1

        with app.app_context():
            db.session.refresh(po_item)
            assert po_item.received_quantity == 30

    def test_concurrent_different_inbound_orders(self, app, purchase_order_setup):
        warehouse, product, po, po_item = purchase_order_setup

        from app.models import Stock
        stock = Stock(product_id=product.id, warehouse_id=warehouse.id, quantity=0)
        stock.version = 0
        db.session.add(stock)
        db.session.commit()

        inbound_order1 = InboundOrder(
            purchase_order_id=po.id,
            received_date=datetime.now(timezone.utc),
            notes="Test inbound 1"
        )
        inbound_order1.version = 0
        db.session.add(inbound_order1)
        db.session.flush()

        inbound_order2 = InboundOrder(
            purchase_order_id=po.id,
            received_date=datetime.now(timezone.utc),
            notes="Test inbound 2"
        )
        inbound_order2.version = 0
        db.session.add(inbound_order2)
        db.session.commit()

        items1 = [{"sku": product.sku, "received_qty": 30}]
        items2 = [{"sku": product.sku, "received_qty": 20}]

        num_threads = 2
        barrier = threading.Barrier(num_threads)
        success_count = [0]

        def process_inbound(thread_id, inbound_id, items):
            with app.app_context():
                barrier.wait()
                InboundService.process_inbound(inbound_id, items)
                success_count[0] += 1

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(process_inbound, 0, inbound_order1.id, items1),
                executor.submit(process_inbound, 1, inbound_order2.id, items2),
            ]
            for future in as_completed(futures):
                future.result()

        assert success_count[0] == 2

        with app.app_context():
            db.session.refresh(po_item)
            assert po_item.received_quantity == 50