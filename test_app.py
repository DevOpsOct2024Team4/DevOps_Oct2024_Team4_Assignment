import unittest
from flask import Flask, session, jsonify
from unittest.mock import patch, MagicMock
from app import app, db

class FlaskAppTests(unittest.TestCase):
    
    def setUp(self):
        """Setup test client"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = app.test_client()

    @patch('app.db.collection')  # Mocking Firestore collection method
    def test_login_success(self, mock_db):
        """Test login with correct credentials"""
        mock_student = MagicMock()
        mock_student.to_dict.return_value = {'Email': 'test@example.com', 'Password': 'password123'}
        mock_db.return_value.where.return_value.stream.return_value = [mock_student]
        
        response = self.client.post('/login', data={'Email': 'test@example.com', 'Password': 'password123'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in successfully!', response.data)

    @patch('app.db.collection')
    def test_login_fail_wrong_password(self, mock_db):
        """Test login failure due to incorrect password"""
        mock_student = MagicMock()
        mock_student.to_dict.return_value = {'Email': 'test@example.com', 'Password': 'password123'}
        mock_db.return_value.where.return_value.stream.return_value = [mock_student]
        
        response = self.client.post('/login', data={'Email': 'test@example.com', 'Password': 'wrongpass'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid password.', response.data)

    @patch('app.db.collection')
    def test_login_fail_email_not_found(self, mock_db):
        """Test login failure due to email not found"""
        mock_db.return_value.where.return_value.stream.return_value = []
        
        response = self.client.post('/login', data={'Email': 'notfound@example.com', 'Password': 'password123'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email not found.', response.data)

    @patch('app.db.collection')
    def test_recover_password_success(self, mock_db):
        """Test password recovery success"""
        mock_student = MagicMock()
        mock_student.id = '123'
        mock_student.to_dict.return_value = {'Email': 'test@example.com'}
        mock_db.return_value.where.return_value.stream.return_value = [mock_student]
        
        response = self.client.post('/recover_password', data={'email': 'test@example.com', 'new_password': 'newpass'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password has been successfully updated!', response.data)

    @patch('app.db.collection')
    def test_recover_password_fail_email_not_found(self, mock_db):
        """Test password recovery failure due to email not found"""
        mock_db.return_value.where.return_value.stream.return_value = []
        
        response = self.client.post('/recover_password', data={'email': 'notfound@example.com', 'new_password': 'newpass'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No student found with the provided email.', response.data)
    
    @patch('app.db.collection')
    def test_check_firebase_connection(self, mock_db):
        """Test Firebase connection"""
        mock_db.return_value = True
        response = self.client.get('/check_firebase')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Firebase is connected!', response.data)
    
    @patch('app.db.collection')
    def test_check_firebase_fail(self, mock_db):
        """Test Firebase connection failure"""
        mock_db.return_value = None
        response = self.client.get('/check_firebase')
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Firebase is NOT initialized!', response.data)

    @patch('app.db.collection')
    def test_redeem_success(self, mock_db):
        """Test redeeming an item successfully"""
        mock_student = MagicMock()
        mock_student.id = "student123"
        mock_student.to_dict.return_value = {"Points": 50, "StudentName": "John Doe"}

        mock_item = MagicMock()
        mock_item.id = "item123"
        mock_item.to_dict.return_value = {"Value": 25, "Quantity": 10, "Name": "Book"}

        mock_db.return_value.document.return_value.get.side_effect = [mock_student, mock_item]

        response = self.client.post('/redeem', data={'student_id': "student123", 'item_name': "item123"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Redemption Successful!', response.data)

    @patch('app.db.collection')
    def test_redeem_fail_insufficient_points(self, mock_db):
        """Test redeeming an item with insufficient points"""
        mock_student = MagicMock()
        mock_student.id = "student123"
        mock_student.to_dict.return_value = {"Points": 10, "StudentName": "John Doe"}

        mock_item = MagicMock()
        mock_item.id = "item123"
        mock_item.to_dict.return_value = {"Value": 25, "Quantity": 10, "Name": "Book"}

        mock_db.return_value.document.return_value.get.side_effect = [mock_student, mock_item]

        response = self.client.post('/redeem', data={'student_id': "student123", 'item_name': "item123"}, follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Insufficient points or item out of stock!', response.data)

    @patch('app.db.collection')
    def test_redeem_fail_item_out_of_stock(self, mock_db):
        """Test redeeming an item that is out of stock"""
        mock_student = MagicMock()
        mock_student.id = "student123"
        mock_student.to_dict.return_value = {"Points": 50, "StudentName": "John Doe"}

        mock_item = MagicMock()
        mock_item.id = "item123"
        mock_item.to_dict.return_value = {"Value": 25, "Quantity": 0, "Name": "Book"}

        mock_db.return_value.document.return_value.get.side_effect = [mock_student, mock_item]

        response = self.client.post('/redeem', data={'student_id': "student123", 'item_name': "item123"}, follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Insufficient points or item out of stock!', response.data)

if __name__ == '__main__':
    unittest.main()
