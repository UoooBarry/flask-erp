import pytest
from datetime import datetime, timezone
from app import create_app
from app.extensions import db as _db

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app

@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def new_user(db):
    from app.models.user import User
    user = User(username='test_admin')
    user.password = 'secure_password'
    return user

@pytest.fixture
def warehouse_with_stock(db):
    from app.models import Warehouse, Stock, Product

    warehouse = Warehouse(name="Test Warehouse", location="Test Location")
    db.session.add(warehouse)
    db.session.flush()

    product = Product(name="Test Product", sku="TEST001", price=100.00, description="Test description")
    db.session.add(product)
    db.session.flush()

    stock = Stock(product_id=product.id, warehouse_id=warehouse.id, quantity=100)
    db.session.add(stock)
    db.session.commit()

    return warehouse, product, stock

@pytest.fixture
def purchase_order_setup(db):
    from app.models import Warehouse, Product, PurchaseOrder, PurchaseOrderItem

    warehouse = Warehouse(name="Test Warehouse", location="Test Location")
    db.session.add(warehouse)
    db.session.flush()

    product = Product(name="Test Product", sku="TEST001", price=100.00, description="Test description")
    db.session.add(product)
    db.session.flush()

    po = PurchaseOrder(
        po_number="PO-001",
        eta=datetime.now(timezone.utc),
        warehouse_id=warehouse.id
    )
    po.version = 0
    db.session.add(po)
    db.session.flush()

    po_item = PurchaseOrderItem(
        purchase_order_id=po.id,
        product_id=product.id,
        quantity=100,
        unit_price=50.00
    )
    po_item.version = 0
    db.session.add(po_item)
    db.session.commit()

    return warehouse, product, po, po_item

@pytest.fixture
def empty_stock(db):
    from app.models import Stock, Product, Warehouse

    product = Product(name="Empty Product", sku="EMPTY001", price=50.00, description="Empty description")
    db.session.add(product)
    db.session.flush()

    warehouse = Warehouse(name="Empty Warehouse", location="Empty Location")
    db.session.add(warehouse)
    db.session.flush()

    return product, warehouse
