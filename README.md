# Mechanics Shop API

A Flask REST API for managing customers, mechanics, and service tickets at an auto mechanics shop.

## Setup

### Prerequisites
- Python 3.14+
- MySQL running locally with a database named `mechanics_db`

### Install dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install flask flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy mysql-connector-python
```

### Configure the database
Update the connection string in `config.py` to match your MySQL credentials:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://<user>:<password>@localhost/mechanics_db'
```

### Run the app
```bash
python app.py
```
The server starts at `http://127.0.0.1:5000`. Tables are created automatically on startup.

---

## API Endpoints

### Customers — `/customers/`

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/customers/` | Create a customer |
| GET | `/customers/` | Get all customers |
| GET | `/customers/<id>` | Get a single customer |
| PUT | `/customers/<id>` | Update a customer |
| DELETE | `/customers/<id>` | Delete a customer |

**Request body (POST/PUT):**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234"
}
```

---

### Mechanics — `/mechanics/`

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/mechanics/` | Create a mechanic |
| GET | `/mechanics/` | Get all mechanics |
| GET | `/mechanics/<id>` | Get a single mechanic |
| PUT | `/mechanics/<id>` | Update a mechanic |
| DELETE | `/mechanics/<id>` | Delete a mechanic |

**Request body (POST/PUT):**
```json
{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "555-5678",
    "salary": "55000.00"
}
```

---

### Service Tickets — `/service_tickets/`

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/service_tickets/` | Create a service ticket |
| GET | `/service_tickets/` | Get all service tickets |
| GET | `/service_tickets/<id>` | Get a single service ticket |
| PUT | `/service_tickets/<id>` | Update a service ticket |
| DELETE | `/service_tickets/<id>` | Delete a service ticket |

**Request body (POST/PUT):**
```json
{
    "vin": "1HGBH41JXMN109186",
    "service_date": "2026-04-05",
    "service_desc": "Oil change",
    "customer_id": 1
}
```

> `service_date` must be in `YYYY-MM-DD` format.
> `customer_id` must reference an existing customer.
