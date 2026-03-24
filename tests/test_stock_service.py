import pytest
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm.exc import StaleDataError
from app.services import StockService
from app.models import Stock, Product, Warehouse
from app.extensions import db


class TestStockServiceFunctionality:
    def test_create_new_stock_when_not_exists(self, empty_stock):
        product, warehouse = empty_stock

        result = StockService.update_inventory(
            product_id=product.id,
            warehouse_id=warehouse.id,
            increment=50
        )

        assert result is not None
        assert result.product_id == product.id
        assert result.warehouse_id == warehouse.id
        assert result.quantity == 50

        stock = Stock.query.filter_by(
            product_id=product.id,
            warehouse_id=warehouse.id
        ).first()
        assert stock is not None
        assert stock.quantity == 50

    def test_update_existing_stock(self, warehouse_with_stock):
        warehouse, product, stock = warehouse_with_stock

        initial_quantity = stock.quantity
        result = StockService.update_inventory(
            product_id=product.id,
            warehouse_id=warehouse.id,
            increment=25
        )

        assert result.quantity == initial_quantity + 25

        db.session.refresh(stock)
        assert stock.quantity == initial_quantity + 25

    def test_decrement_existing_stock(self, warehouse_with_stock):
        warehouse, product, stock = warehouse_with_stock

        initial_quantity = stock.quantity
        result = StockService.update_inventory(
            product_id=product.id,
            warehouse_id=warehouse.id,
            increment=-30
        )

        assert result.quantity == initial_quantity - 30

        db.session.refresh(stock)
        assert stock.quantity == initial_quantity - 30

    def test_invalid_decrement_insufficient_stock(self, warehouse_with_stock):
        warehouse, product, stock = warehouse_with_stock

        initial_quantity = stock.quantity

        with pytest.raises(ValueError) as exc_info:
            StockService.update_inventory(
                product_id=product.id,
                warehouse_id=warehouse.id,
                increment=-(initial_quantity + 10)
            )

        assert "Insufficient stock" in str(exc_info.value)

        db.session.refresh(stock)
        assert stock.quantity == initial_quantity

    def test_zero_quantity_update(self, warehouse_with_stock):
        warehouse, product, stock = warehouse_with_stock

        initial_quantity = stock.quantity
        result = StockService.update_inventory(
            product_id=product.id,
            warehouse_id=warehouse.id,
            increment=0
        )

        assert result.quantity == initial_quantity

        db.session.refresh(stock)
        assert stock.quantity == initial_quantity

    def test_large_quantity_update(self, empty_stock):
        product, warehouse = empty_stock

        large_increment = 10000
        result = StockService.update_inventory(
            product_id=product.id,
            warehouse_id=warehouse.id,
            increment=large_increment
        )

        assert result.quantity == large_increment

    def test_negative_initial_quantity_creation(self, empty_stock):
        product, warehouse = empty_stock

        result = StockService.update_inventory(
            product_id=product.id,
            warehouse_id=warehouse.id,
            increment=-10
        )

        assert result.quantity == -10


class TestStockServiceRaceConditions:
    def test_concurrent_same_increment(self, app, warehouse_with_stock):
        warehouse, product, stock = warehouse_with_stock
        initial_quantity = stock.quantity
        num_threads = 10
        increment_per_thread = 1

        product_id = product.id
        warehouse_id = warehouse.id

        barrier = threading.Barrier(num_threads)

        def increment_stock(thread_id):
            with app.app_context():
                barrier.wait()
                StockService.update_inventory(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    increment=increment_per_thread
                )

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(increment_stock, i)
                for i in range(num_threads)
            ]
            for future in as_completed(futures):
                future.result()

        with app.app_context():
            updated_stock = Stock.query.filter_by(
                product_id=product.id,
                warehouse_id=warehouse.id
            ).first()
            assert updated_stock is not None
            expected_quantity = initial_quantity + (num_threads * increment_per_thread)
            assert updated_stock.quantity == expected_quantity

    def test_concurrent_different_increments(self, app, warehouse_with_stock):
        warehouse, product, stock = warehouse_with_stock
        initial_quantity = stock.quantity

        increments = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
        num_threads = len(increments)

        product_id = product.id
        warehouse_id = warehouse.id

        barrier = threading.Barrier(num_threads)

        def increment_stock(thread_id, inc):
            with app.app_context():
                barrier.wait()
                StockService.update_inventory(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    increment=inc
                )

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(increment_stock, i, inc)
                for i, inc in enumerate(increments)
            ]
            for future in as_completed(futures):
                future.result()

        with app.app_context():
            updated_stock = Stock.query.filter_by(
                product_id=product.id,
                warehouse_id=warehouse.id
            ).first()
            assert updated_stock is not None
            expected_quantity = initial_quantity + sum(increments)
            assert updated_stock.quantity == expected_quantity

    def test_concurrent_decrements(self, app, warehouse_with_stock):
        warehouse, product, stock = warehouse_with_stock
        initial_quantity = stock.quantity
        num_threads = 10
        decrement_per_thread = 5

        product_id = product.id
        warehouse_id = warehouse.id

        barrier = threading.Barrier(num_threads)

        def decrement_stock(thread_id):
            with app.app_context():
                barrier.wait()
                StockService.update_inventory(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    increment=-decrement_per_thread
                )

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(decrement_stock, i)
                for i in range(num_threads)
            ]
            for future in as_completed(futures):
                future.result()

        with app.app_context():
            updated_stock = Stock.query.filter_by(
                product_id=product.id,
                warehouse_id=warehouse.id
            ).first()
            assert updated_stock is not None
            expected_quantity = initial_quantity - (num_threads * decrement_per_thread)
            assert updated_stock.quantity == expected_quantity

    def test_mixed_concurrent_operations(self, app, warehouse_with_stock):
        warehouse, product, stock = warehouse_with_stock
        initial_quantity = stock.quantity

        increments = [10, 10, 10, 10, 10]
        decrements = [-5, -5, -5, -5, -5]
        all_operations = increments + decrements
        num_threads = len(all_operations)

        product_id = product.id
        warehouse_id = warehouse.id

        barrier = threading.Barrier(num_threads)

        def update_stock(thread_id, inc):
            with app.app_context():
                barrier.wait()
                StockService.update_inventory(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    increment=inc
                )

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(update_stock, i, inc)
                for i, inc in enumerate(all_operations)
            ]
            for future in as_completed(futures):
                future.result()

        with app.app_context():
            updated_stock = Stock.query.filter_by(
                product_id=product.id,
                warehouse_id=warehouse.id
            ).first()
            assert updated_stock is not None
            expected_quantity = initial_quantity + sum(all_operations)
            assert updated_stock.quantity == expected_quantity

    @pytest.mark.skip(reason="SQLite has limited concurrent write support")
    def test_concurrent_create_and_update(self, app, empty_stock):
        product, warehouse = empty_stock

        num_threads = 2
        increment_per_thread = 5

        product_id = product.id
        warehouse_id = warehouse.id

        barrier = threading.Barrier(num_threads)

        def increment_stock(thread_id):
            with app.app_context():
                barrier.wait()
                if thread_id > 0:
                    import time
                    time.sleep(0.01)  # Small delay to reduce SQLite lock contention
                StockService.update_inventory(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    increment=increment_per_thread
                )

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(increment_stock, i)
                for i in range(num_threads)
            ]
            for future in as_completed(futures):
                future.result()

        with app.app_context():
            stock = Stock.query.filter_by(
                product_id=product_id,
                warehouse_id=warehouse_id
            ).first()
            assert stock is not None
            expected_quantity = num_threads * increment_per_thread
            assert stock.quantity == expected_quantity

    def test_stale_data_error_and_retry(self, app, warehouse_with_stock, monkeypatch):
        warehouse, product, stock = warehouse_with_stock

        original_method = db.session.commit
        call_count = [0]

        def mock_commit_with_stale_error():
            call_count[0] += 1
            if call_count[0] == 1:
                raise StaleDataError("Simulated stale data", [], "UPDATE stocks")
            return original_method()

        monkeypatch.setattr(db.session, 'commit', mock_commit_with_stale_error)

        result = StockService.update_inventory(
            product_id=product.id,
            warehouse_id=warehouse.id,
            increment=10
        )

        assert result is not None
        db.session.refresh(stock)
        assert stock.quantity > 100

