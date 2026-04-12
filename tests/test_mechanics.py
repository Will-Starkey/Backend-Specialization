from app import create_app
from app.models import db, Mechanic
from app.utils.util import encode_token
import unittest


class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.mechanic = Mechanic(name="test_mechanic", email="mechanic@email.com", phone="123 456 7890", salary=50000, password="test")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "Jane Smith",
            "email": "jane@email.com",
            "phone": "987 654 3210",
            "salary": 60000,
            "password": "abc123"
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Jane Smith")

    def test_invalid_creation(self):
        mechanic_payload = {
            "name": "Jane Smith",
            "phone": "987 654 3210",
            "salary": 60000,
            "password": "abc123"
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])

    def test_login_mechanic(self):
        credentials = {
            "email": "mechanic@email.com",
            "password": "test"
        }
        response = self.client.post('/mechanics/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['token']

    def test_invalid_login(self):
        credentials = {
            "email": "bad@email.com",
            "password": "wrongpass"
        }
        response = self.client.post('/mechanics/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'invalid email or password!')

    def test_get_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_mechanic(self):
        response = self.client.get('/mechanics/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], 'mechanic@email.com')

    def test_get_mechanic_not_found(self):
        response = self.client.get('/mechanics/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Mechanic not found.')

    def test_get_most_tickets(self):
        response = self.client.get('/mechanics/most-tickets')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_update_mechanic(self):
        update_payload = {
            "name": "Updated Mechanic",
            "email": "mechanic@email.com",
            "phone": "123 456 7890",
            "salary": 55000,
            "password": "test"
        }
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated Mechanic')

    def test_delete_mechanic(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}
        response = self.client.delete('/mechanics/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('successfully deleted', response.json['message'])
