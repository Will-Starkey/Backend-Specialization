from .schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, db
from . import customers_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required


@customers_bp.route("/login", methods=['POST'])
def login():
    
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()

    if customer and customer.password == password:
        token = encode_token(customer.id)
        
        response = {
            "status": "success",
            "message": "successfully logged in.",
            "token": token
        }
        
        return jsonify(response), 200
    else:
        return jsonify({"message": "Invalid email or password!"}), 400
    
    

# CREATE CUSTOMER 
@customers_bp.route("/", methods=['POST'])
@limiter.limit("4 per hour") 
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Email already associated with account"}), 400
    
    new_customer = Customer (**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


#GET ALL CUSTOMERS
@customers_bp.route("/", methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = select(Customer).limit(per_page).offset((page - 1) * per_page)
    customer = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customer)

#GET SINGLE CUSTOMER
@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404


#UPDATE CUSTOMER
@customers_bp.route("/", methods=['PUT'])
@token_required
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400
    
    for key, value in customer_data.items():
        if value:
            setattr(customer, key, value)
        
    db.session.commit()
    return customer_schema.jsonify(customer), 200
    
#DELETE SPECIFIC CUSTOMER
@customers_bp.route("/", methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer id: {customer_id}, successfully deleted.'}), 200