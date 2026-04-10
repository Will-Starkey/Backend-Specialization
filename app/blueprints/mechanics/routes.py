from .schemas import mechanic_schema, mechanics_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, func
from app.models import Mechanic, ServiceMechanic, db
from . import mechanics_bp
from app.utils.util import mechanic_token_required, encode_token


# LOGIN MECHANIC
@mechanics_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic and mechanic.password == password:
        token = encode_token(mechanic.id)

        response = {
            "status": "success",
            "message": "successfully logged in.",
            "token": token
        }

        return jsonify(response), 200
    else:
        return jsonify({"message": "invalid email or password!"}), 401


# CREATE Mechanic
@mechanics_bp.route("/", methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalars().all()
    if existing_mechanic:
        return jsonify({"error": "Email already associated with Mechanic"}), 400

    new_mechanic = Mechanic (**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201


#GET ALL MECHANICS
@mechanics_bp.route("/", methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    mechanic = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanic)

#GET SINGLE MECHANIC
@mechanics_bp.route("/<int:mechanic_id>", methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Mechanic not found."}), 404


# GET MECHANICS BY MOST TICKETS
@mechanics_bp.route("/most-tickets", methods=['GET'])
def get_mechanics_by_tickets():
    query = (
        select(Mechanic)
        .outerjoin(Mechanic.ticket_assignments)
        .group_by(Mechanic.id)
        .order_by(func.count(ServiceMechanic.ticket_id).desc())
    )
    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200


#UPDATE MECHANIC
@mechanics_bp.route("/", methods=['PUT'])
@mechanic_token_required
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

#DELETE SPECIFIC MECHANIC
@mechanics_bp.route("/", methods=['DELETE'])
@mechanic_token_required
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f'Mechanic id: {mechanic_id}, successfully deleted.'}), 200
