import pytest
from app import create_app
from app.models import Warehouse


@pytest.fixture
def app_with_warehouse_routes():
    app = create_app("testing")
    return app


class TestWarehouseRoutes:
    def test_get_warehouses_empty(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.test_client() as client:
            response = client.get("/warehouses/")
            data = response.get_json()

            assert response.status_code == 200
            assert data["success"] is True
            assert data["data"] == []
            assert data["meta"]["total"] == 0

    def test_get_warehouses_with_data(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.app_context():
            warehouse = Warehouse(name="Main Warehouse", location="New York")
            db.session.add(warehouse)
            db.session.commit()

        with app_with_warehouse_routes.test_client() as client:
            response = client.get("/warehouses/")
            data = response.get_json()

            assert response.status_code == 200
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["name"] == "Main Warehouse"
            assert data["data"][0]["location"] == "New York"

    def test_get_warehouse_by_id(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.app_context():
            warehouse = Warehouse(name="Main Warehouse", location="New York")
            db.session.add(warehouse)
            db.session.commit()
            warehouse_id = warehouse.id

        with app_with_warehouse_routes.test_client() as client:
            response = client.get(f"/warehouses/{warehouse_id}")
            data = response.get_json()

            assert response.status_code == 200
            assert data["success"] is True
            assert data["data"]["id"] == warehouse_id
            assert data["data"]["name"] == "Main Warehouse"

    def test_get_warehouse_not_found(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.test_client() as client:
            response = client.get("/warehouses/999")
            data = response.get_json()

            assert response.status_code == 404
            assert data["success"] is False
            assert "not found" in data["message"].lower()

    def test_create_warehouse_success(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.test_client() as client:
            response = client.post(
                "/warehouses/",
                json={
                    "name": "New Warehouse",
                    "location": "Los Angeles",
                },
            )
            data = response.get_json()

            assert response.status_code == 201
            assert data["success"] is True
            assert data["data"]["name"] == "New Warehouse"
            assert data["data"]["location"] == "Los Angeles"

    def test_create_warehouse_missing_name(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.test_client() as client:
            response = client.post(
                "/warehouses/",
                json={
                    "location": "Los Angeles",
                },
            )
            data = response.get_json()

            assert response.status_code == 422
            assert data["success"] is False
            assert "name" in data["message"].lower()

    def test_create_warehouse_no_body(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.test_client() as client:
            response = client.post("/warehouses/", json={})
            data = response.get_json()

            assert response.status_code == 422
            assert data["success"] is False
            assert "required" in data["message"].lower()

    def test_create_warehouse_duplicate_name(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.app_context():
            warehouse = Warehouse(name="Main Warehouse", location="New York")
            db.session.add(warehouse)
            db.session.commit()

        with app_with_warehouse_routes.test_client() as client:
            response = client.post(
                "/warehouses/",
                json={"name": "Main Warehouse", "location": "Los Angeles"},
            )
            data = response.get_json()

            assert response.status_code == 422
            assert data["success"] is False
            assert "already exists" in data["message"].lower()

    def test_update_warehouse_success(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.app_context():
            warehouse = Warehouse(name="Main Warehouse", location="New York")
            db.session.add(warehouse)
            db.session.commit()
            warehouse_id = warehouse.id

        with app_with_warehouse_routes.test_client() as client:
            response = client.put(
                f"/warehouses/{warehouse_id}",
                json={
                    "location": "Chicago",
                },
            )
            data = response.get_json()

            assert response.status_code == 200
            assert data["success"] is True
            assert data["data"]["location"] == "Chicago"

    def test_update_warehouse_not_found(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.test_client() as client:
            response = client.put("/warehouses/999", json={"location": "Chicago"})
            data = response.get_json()

            assert response.status_code == 404
            assert data["success"] is False

    def test_update_warehouse_empty_name(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.app_context():
            warehouse = Warehouse(name="Main Warehouse", location="New York")
            db.session.add(warehouse)
            db.session.commit()
            warehouse_id = warehouse.id

        with app_with_warehouse_routes.test_client() as client:
            response = client.put(f"/warehouses/{warehouse_id}", json={"name": ""})
            data = response.get_json()

            assert response.status_code == 422
            assert data["success"] is False
            assert "cannot be empty" in data["message"].lower()

    def test_delete_warehouse_success(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.app_context():
            warehouse = Warehouse(name="Main Warehouse", location="New York")
            db.session.add(warehouse)
            db.session.commit()
            warehouse_id = warehouse.id

        with app_with_warehouse_routes.test_client() as client:
            response = client.delete(f"/warehouses/{warehouse_id}")
            data = response.get_json()

            assert response.status_code == 200
            assert data["success"] is True
            assert "deleted" in data["data"]["message"].lower()

    def test_delete_warehouse_with_stock(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.app_context():
            from app.models import Stock, Product

            warehouse = Warehouse(name="Main Warehouse", location="New York")
            db.session.add(warehouse)
            db.session.commit()

            product = Product(name="Test Product", sku="TEST001", price=99.99, description= "Test product")
            db.session.add(product)
            db.session.commit()

            stock = Stock(
                product_id=product.id, warehouse_id=warehouse.id, quantity=100
            )
            db.session.add(stock)
            db.session.commit()
            warehouse_id = warehouse.id

        with app_with_warehouse_routes.test_client() as client:
            response = client.delete(f"/warehouses/{warehouse_id}")
            data = response.get_json()

            assert response.status_code == 422
            assert data["success"] is False
            assert "stock" in data["message"].lower()

    def test_delete_warehouse_not_found(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.test_client() as client:
            response = client.delete("/warehouses/999")
            data = response.get_json()

            assert response.status_code == 404
            assert data["success"] is False

    def test_pagination(self, app_with_warehouse_routes, db):
        with app_with_warehouse_routes.app_context():
            for i in range(5):
                warehouse = Warehouse(name=f"Warehouse {i}", location=f"Location {i}")
                db.session.add(warehouse)
            db.session.commit()

        with app_with_warehouse_routes.test_client() as client:
            response = client.get("/warehouses/?page=1&per_page=2")
            data = response.get_json()

            assert response.status_code == 200
            assert data["success"] is True
            assert len(data["data"]) == 2
            assert data["meta"]["total"] == 5
            assert data["meta"]["pages"] == 3
            assert data["meta"]["current_page"] == 1
            assert data["meta"]["per_page"] == 2
