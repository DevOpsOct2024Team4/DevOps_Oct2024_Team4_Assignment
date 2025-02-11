# tests/test_routes.py
import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app

class TestRoutes(unittest.TestCase):
    def setUp(self):
        # Set up the Flask test client
        self.app = app.test_client()
        self.app.testing = True

# Login Failing Test Case for Login

@patch('app.db')
def test_login_failure(self, mock_db):
    # Mock Firebase query to return no student (invalid email)
    mock_db.collection.return_value.where.return_value.stream.return_value = []

    # Simulate a POST request with invalid credentials
    response = self.app.post("/login", data={
        "Email": "wrong@example.com",
        "Password": "wrongpassword"
    }, follow_redirects=True)

    self.assertEqual(response.status_code, 200)
    self.assertIn(b"Email not found.", response.data)

# Test Cases for Login
    # --------------------------
    @patch('app.db')
    def test_login_success(self, mock_db):
        # Test case for successful login
        pass

    @patch('app.db')
    def test_login_failure(self, mock_db):
        # Test case for failed login (invalid credentials)
        pass

if __name__ == "__main__":
    unittest.main()