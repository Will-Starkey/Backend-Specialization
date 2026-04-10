from .schemas import inventory_schema, inventories_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Inventory, db
from . import inventory_bp


# CREATE INVENTORY ITEM
@inventory_bp.route("/", methods=['POST'])
def create_inventory():
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_item = Inventory(**inventory_data)
    db.session.add(new_item)
    db.session.commit()
    return inventory_schema.jsonify(new_item), 201


# GET ALL INVENTORY ITEMS
@inventory_bp.route("/", methods=['GET'])
def get_inventory():
    query = select(Inventory)
    items = db.session.execute(query).scalars().all()
    return inventories_schema.jsonify(items), 200


# GET SINGLE INVENTORY ITEM
@inventory_bp.route("/<int:inventory_id>", methods=['GET'])
def get_inventory_item(inventory_id):
    item = db.session.get(Inventory, inventory_id)
    if item:
        return inventory_schema.jsonify(item), 200
    return jsonify({"error": "Inventory item not found."}), 404


# UPDATE INVENTORY ITEM
@inventory_bp.route("/<int:inventory_id>", methods=['PUT'])
def update_inventory(inventory_id):
    item = db.session.get(Inventory, inventory_id)
    if not item:
        return jsonify({"error": "Inventory item not found."}), 404

    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in inventory_data.items():
        setattr(item, key, value)

    db.session.commit()
    return inventory_schema.jsonify(item), 200


# DELETE INVENTORY ITEM
@inventory_bp.route("/<int:inventory_id>", methods=['DELETE'])
def delete_inventory(inventory_id):
    item = db.session.get(Inventory, inventory_id)
    if not item:
        return jsonify({"error": "Inventory item not found."}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Inventory item {inventory_id} successfully deleted."}), 200
