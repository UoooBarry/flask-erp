from flask import Blueprint, request
from app.models import Product, Stock
from app.extensions import db
from app.utils.response import render_success
from app.utils.exceptions import ValidationError, NotFoundError
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    StockAdd,
    StockUpdate,
    StockRemove,
)
from sqlalchemy.exc import IntegrityError
from app.services import StockService


products_bp = Blueprint("products", __name__)


@products_bp.route("/", methods=["GET"])
def get_products():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search", "")
    warehouse_id = request.args.get("warehouse_id", type=int)

    query = Product.query

    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) | (Product.sku.ilike(f"%{search}%"))
        )

    if warehouse_id:
        query = query.join(Stock).filter(Stock.warehouse_id == warehouse_id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    products_data = [
        ProductListResponse.model_validate(p).model_dump() for p in pagination.items
    ]

    return render_success(
        products_data,
        meta_data={
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "per_page": per_page,
        },
    )


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        raise NotFoundError(f"Product with id {product_id} not found")

    product_data = ProductResponse.model_validate(product).model_dump()

    return render_success(product_data)


@products_bp.route("/", methods=["POST"])
def create_product():
    data = request.get_json()

    if not data:
        raise ValidationError("Request body is required")

    validated_data = ProductCreate(**data)

    product = Product(
        name=validated_data.name,
        description=validated_data.description,
        sku=validated_data.sku,
        price=validated_data.price,
    )

    try:
        db.session.add(product)
        db.session.commit()

        return render_success(
            ProductResponse.model_validate(product).model_dump(), status_code=201
        )
    except IntegrityError as e:
        db.session.rollback()
        if "unique" in str(e).lower():
            if "sku" in str(e).lower():
                raise ValidationError("Product SKU already exists")
            if "name" in str(e).lower():
                raise ValidationError("Product name already exists")
        raise


@products_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        raise NotFoundError(f"Product with id {product_id} not found")

    data = request.get_json()
    if not data:
        raise ValidationError("Request body is required")

    validated_data = ProductUpdate(**data)

    if validated_data.name is not None:
        product.name = validated_data.name

    if validated_data.description is not None:
        product.description = validated_data.description

    if validated_data.sku is not None:
        product.sku = validated_data.sku

    if validated_data.price is not None:
        product.price = validated_data.price

    try:
        db.session.commit()

        return render_success(ProductResponse.model_validate(product).model_dump())
    except IntegrityError as e:
        db.session.rollback()
        if "unique" in str(e).lower():
            if "sku" in str(e).lower():
                raise ValidationError("Product SKU already exists")
            if "name" in str(e).lower():
                raise ValidationError("Product name already exists")
        raise


@products_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        raise NotFoundError(f"Product with id {product_id} not found")

    if product.stocks:
        raise ValidationError(
            "Cannot delete product with existing stock. Please remove stock first."
        )

    db.session.delete(product)
    db.session.commit()

    return render_success({"message": "Product deleted successfully"})


@products_bp.route("/<int:product_id>/stock", methods=["POST"])
def add_stock(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        raise NotFoundError(f"Product with id {product_id} not found")

    data = request.get_json()
    if not data:
        raise ValidationError("Request body is required")

    validated_data = StockAdd(**data)

    from app.models import Warehouse

    warehouse = db.session.get(Warehouse, validated_data.warehouse_id)
    if not warehouse:
        raise NotFoundError(
            f"Warehouse with id {validated_data.warehouse_id} not found"
        )

    existing_stock = Stock.query.filter_by(
        product_id=product_id, warehouse_id=validated_data.warehouse_id
    ).first()

    if existing_stock:
        existing_stock.quantity += validated_data.quantity
    else:
        stock = Stock(
            product_id=product_id,
            warehouse_id=validated_data.warehouse_id,
            quantity=validated_data.quantity,
        )
        db.session.add(stock)

    db.session.commit()

    return render_success({"message": "Stock added successfully"})


# @products_bp.route("/<int:product_id>/stock", methods=["PUT"])
# def update_stock(product_id):
#     product = db.session.get(Product, product_id)
#     if not product:
#         raise NotFoundError(f"Product with id {product_id} not found")
#
#     data = request.get_json()
#     if not data:
#         raise ValidationError("Request body is required")
#
#     validated_data = StockUpdate(**data)
#
#     try:
#         StockService.update_inventory(product_id, validated_data.warehouse_id, validated_data.quantity)
#     except ValueError as e:
#         raise ValidationError(str(e))
#
#     db.session.commit()
#
#     return render_success({"message": "Stock updated successfully"})
