from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import ServiceTicket, Mechanic, ServiceMechanic, Inventory, db
from . import service_tickets_bp
from app.utils.util import token_required


# CREATE Service Ticket 
@service_tickets_bp.route("/", methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    
    new_service_ticket = service_ticket_data
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201


# GET MY Service Tickets
@service_tickets_bp.route("/my-tickets", methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    query = select(ServiceTicket).where(ServiceTicket.customer_id == customer_id)
    tickets = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(tickets), 200


#GET ALL Service Tickets
@service_tickets_bp.route("/", methods=['GET'])
def get_service_tickets():
    query = select(ServiceTicket)
    service_ticket = db.session.execute(query).scalars().all()
    
    return service_tickets_schema.jsonify(service_ticket)

#GET SINGLE Service Ticket
@service_tickets_bp.route("/<int:service_ticket_id>", methods=['GET'])
def get_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    
    if service_ticket:
        return service_ticket_schema.jsonify(service_ticket), 200
    return jsonify({"error": "Service Ticket not found."}), 404


#UPDATE Service Ticket
@service_tickets_bp.route("/<int:service_ticket_id>", methods=['PUT'])
def update_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    
    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404
    
    try:
        service_ticket_data = service_ticket_schema.load(request.json, instance=service_ticket)
    except ValidationError as e: 
        return jsonify(e.messages), 400
    
        
    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200
    
# ASSIGN MECHANICS TO Service Ticket
@service_tickets_bp.route("/<int:service_ticket_id>/mechanics", methods=['PUT'])
def assign_mechanics(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404

    mechanic_ids = request.json.get("mechanic_ids", [])

    mechanics = []
    for mechanic_id in mechanic_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({"error": f"Mechanic with id {mechanic_id} not found."}), 400
        mechanics.append(mechanic)

    service_ticket.mechanic_assignments.clear()

    for mechanic in mechanics:
        assignment = ServiceMechanic(ticket_id=service_ticket_id, mechanic_id=mechanic.id)
        db.session.add(assignment)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200


# DELETE SPECIFIC MECHANIC FROM Service Ticket
@service_tickets_bp.route("/<int:service_ticket_id>/mechanics/<int:mechanic_id>", methods=['DELETE'])
def remove_mechanic(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404

    assignment = db.session.get(ServiceMechanic, (service_ticket_id, mechanic_id))

    if not assignment:
        return jsonify({"error": f"Mechanic {mechanic_id} is not assigned to ticket {service_ticket_id}."}), 400

    db.session.delete(assignment)
    db.session.commit()
    return jsonify({"message": f"Mechanic {mechanic_id} removed from service ticket {service_ticket_id}."}), 200


# ADD/REMOVE MECHANICS FROM Service Ticket
@service_tickets_bp.route("/<int:ticket_id>/edit", methods=['PUT'])
def edit_ticket_mechanics(ticket_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404

    add_ids = request.json.get("add_ids", [])
    remove_ids = request.json.get("remove_ids", [])

    for mechanic_id in remove_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({"error": f"Mechanic with id {mechanic_id} not found."}), 400
        assignment = db.session.get(ServiceMechanic, (ticket_id, mechanic_id))
        if assignment:
            db.session.delete(assignment)

    for mechanic_id in add_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({"error": f"Mechanic with id {mechanic_id} not found."}), 400
        existing = db.session.get(ServiceMechanic, (ticket_id, mechanic_id))
        if not existing:
            assignment = ServiceMechanic(ticket_id=ticket_id, mechanic_id=mechanic_id)
            db.session.add(assignment)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200


# ADD PART TO Service Ticket
@service_tickets_bp.route("/<int:ticket_id>/add-part", methods=['POST'])
def add_part_to_ticket(ticket_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404

    inventory_id = request.json.get("inventory_id")
    item = db.session.get(Inventory, inventory_id)
    if not item:
        return jsonify({"error": "Inventory item not found."}), 404

    service_ticket.parts.append(item)
    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200


#DELETE SPECIFIC Service Ticket
@service_tickets_bp.route("/<int:service_ticket_id>", methods=['DELETE'])
def delete_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    
    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404
    
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"message": f'Service Ticket id: {service_ticket_id}, successfully deleted.'}), 200