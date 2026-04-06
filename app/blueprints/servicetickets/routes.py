from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import ServiceTicket, Mechanic, ServiceMechanic, db
from . import service_tickets_bp


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
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400
    
    for key, value in service_ticket_data.items():
        setattr(service_ticket, key, value)
        
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


#DELETE SPECIFIC Service Ticket
@service_tickets_bp.route("/<int:service_ticket_id>", methods=['DELETE'])
def delete_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    
    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404
    
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"message": f'Service Ticket id: {service_ticket_id}, successfully deleted.'}), 200