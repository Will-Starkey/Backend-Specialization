from app import create_app
from app.models import db, Customer, Mechanic, ServiceTicket, Inventory
from app.utils.util import encode_token
import unittest
import datetime


class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(name="test_customer", email="test@email.com", phone="123 456 7890", password="test")
        self.mechanic = Mechanic(name="test_mechanic", email="mechanic@email.com", phone="123 456 7890", salary=50000, password="test")
        self.service_ticket = ServiceTicket(vin="1HGCM82633A123456", service_date=datetime.date(2024, 1, 15), service_desc="Oil change", customer_id=1)
        self.inventory_item = Inventory(name="Oil Filter", price=12.99)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.add(self.mechanic)
            db.session.commit()
            db.session.add(self.service_ticket)
            db.session.add(self.inventory_item)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    def test_login_customer(self):
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['token']

    def test_create_service_ticket(self):
        ticket_payload = {
            "vin": "2T1BURHE0JC123456",
            "service_date": "2024-02-20",
            "service_desc": "Tire rotation",
            "customer_id": 1
        }
        response = self.client.post('/service_tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['vin'], '2T1BURHE0JC123456')

    def test_invalid_create_service_ticket(self):
        ticket_payload = {
            "service_desc": "Missing required fields"
        }
        response = self.client.post('/service_tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 400)

    def test_get_service_tickets(self):
        response = self.client.get('/service_tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_service_ticket(self):
        response = self.client.get('/service_tickets/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['vin'], '1HGCM82633A123456')

    def test_get_service_ticket_not_found(self):
        response = self.client.get('/service_tickets/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Service Ticket not found.')

    def test_get_my_tickets(self):
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        response = self.client.get('/service_tickets/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_update_service_ticket(self):
        update_payload = {
            "vin": "1HGCM82633A123456",
            "service_date": "2024-03-10",
            "service_desc": "Updated - oil change and tire rotation",
            "customer_id": 1
        }
        response = self.client.put('/service_tickets/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_desc'], 'Updated - oil change and tire rotation')

    def test_update_service_ticket_not_found(self):
        update_payload = {
            "vin": "1HGCM82633A123456",
            "service_date": "2024-03-10",
            "service_desc": "Does not exist",
            "customer_id": 1
        }
        response = self.client.put('/service_tickets/999', json=update_payload)
        self.assertEqual(response.status_code, 404)

    def test_assign_mechanics(self):
        payload = {"mechanic_ids": [1]}
        response = self.client.put('/service_tickets/1/mechanics', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_assign_mechanic_not_found(self):
        payload = {"mechanic_ids": [999]}
        response = self.client.put('/service_tickets/1/mechanics', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('not found', response.json['error'])

    def test_edit_ticket_mechanics(self):
        payload = {
            "add_ids": [1],
            "remove_ids": []
        }
        response = self.client.put('/service_tickets/1/edit', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_remove_mechanic_from_ticket(self):
        self.client.put('/service_tickets/1/mechanics', json={"mechanic_ids": [1]})
        response = self.client.delete('/service_tickets/1/mechanics/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('removed', response.json['message'])

    def test_remove_mechanic_not_assigned(self):
        response = self.client.delete('/service_tickets/1/mechanics/1')
        self.assertEqual(response.status_code, 400)

    def test_add_part_to_ticket(self):
        payload = {"inventory_id": 1}
        response = self.client.post('/service_tickets/1/add-part', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_add_part_not_found(self):
        payload = {"inventory_id": 999}
        response = self.client.post('/service_tickets/1/add-part', json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Inventory item not found.')

    def test_delete_service_ticket(self):
        response = self.client.delete('/service_tickets/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('successfully deleted', response.json['message'])

    def test_delete_service_ticket_not_found(self):
        response = self.client.delete('/service_tickets/999')
        self.assertEqual(response.status_code, 404)
