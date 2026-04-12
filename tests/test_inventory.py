from app import create_app
from app.models import db, Inventory
import unittest


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.inventory_item = Inventory(name="Oil Filter", price=12.99)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.inventory_item)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_inventory(self):
        inventory_payload = {
            "name": "Brake Pad",
            "price": 29.99
        }
        response = self.client.post('/inventory/', json=inventory_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Brake Pad")

    def test_invalid_creation(self):
        inventory_payload = {
            "name": "Missing Price"
        }
        response = self.client.post('/inventory/', json=inventory_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['price'], ['Missing data for required field.'])

    def test_get_inventory(self):
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_inventory_item(self):
        response = self.client.get('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Oil Filter')

    def test_get_inventory_item_not_found(self):
        response = self.client.get('/inventory/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Inventory item not found.')

    def test_update_inventory(self):
        update_payload = {
            "name": "Premium Oil Filter",
            "price": 19.99
        }
        response = self.client.put('/inventory/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Premium Oil Filter')
        self.assertEqual(response.json['price'], 19.99)

    def test_update_inventory_not_found(self):
        update_payload = {
            "name": "Does Not Exist",
            "price": 9.99
        }
        response = self.client.put('/inventory/999', json=update_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Inventory item not found.')

    def test_delete_inventory(self):
        response = self.client.delete('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('successfully deleted', response.json['message'])

    def test_delete_inventory_not_found(self):
        response = self.client.delete('/inventory/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Inventory item not found.')
