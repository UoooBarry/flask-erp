from flask import Blueprint, request
from app.models import Warehouse, Stock
from app.extensions import db
from app.utils.response import render_success
from app.utils.exceptions import ValidationError, NotFoundError
from app.schemas import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from sqlalchemy.exc import IntegrityError


warehouses_bp = Blueprint("warehouses", __name__)


@warehouses_bp.route("/", methods=["GET"])
def get_warehouses():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Warehouse.query

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    warehouses_data = [WarehouseResponse.model_validate(w).model_dump() for w in pagination.items]

    return render_success(
        warehouses_data,
        meta_data={
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "per_page": per_page,
        },
    )


@warehouses_bp.route("/<int:warehouse_id>", methods=["GET"])
def get_warehouse(warehouse_id):
    warehouse = db.session.get(Warehouse, warehouse_id)
    if not warehouse:
        raise NotFoundError(f"Warehouse with id {warehouse_id} not found")

    warehouse_data = WarehouseResponse.model_validate(warehouse).model_dump()

    return render_success(warehouse_data)


@warehouses_bp.route("/", methods=["POST"])
def create_warehouse():
    data = request.get_json()

    if not data:
        raise ValidationError("Request body is required")

    validated_data = WarehouseCreate(**data)

    warehouse = Warehouse(
        name=validated_data.name,
        location=validated_data.location
    )

    try:
        db.session.add(warehouse)
        db.session.commit()

        return render_success(
            WarehouseResponse.model_validate(warehouse).model_dump(),
            201
        )
    except IntegrityError as e:
        db.session.rollback()
        if "unique" in str(e).lower():
            raise ValidationError("Warehouse name already exists")
        raise


@warehouses_bp.route("/<int:warehouse_id>", methods=["PUT"])
def update_warehouse(warehouse_id):
    warehouse = db.session.get(Warehouse, warehouse_id)
    if not warehouse:
        raise NotFoundError(f"Warehouse with id {warehouse_id} not found")

    data = request.get_json()
    if not data:
        raise ValidationError("Request body is required")

    validated_data = WarehouseUpdate(**data)

    if validated_data.name is not None:
        warehouse.name = validated_data.name

    if validated_data.location is not None:
        warehouse.location = validated_data.location

    try:
        db.session.commit()

        return render_success(
            WarehouseResponse.model_validate(warehouse).model_dump()
        )
    except IntegrityError as e:
        db.session.rollback()
        if "unique" in str(e).lower():
            raise ValidationError("Warehouse name already exists")
        raise


@warehouses_bp.route("/<int:warehouse_id>", methods=["DELETE"])
def delete_warehouse(warehouse_id):
    warehouse = db.session.get(Warehouse, warehouse_id)
    if not warehouse:
        raise NotFoundError(f"Warehouse with id {warehouse_id} not found")

    if warehouse.stocks:
        raise ValidationError(
            f"Cannot delete warehouse with existing stock. "
            f"Please remove or relocate all products first."
        )

    db.session.delete(warehouse)
    db.session.commit()

    return render_success({"message": "Warehouse deleted successfully"})
