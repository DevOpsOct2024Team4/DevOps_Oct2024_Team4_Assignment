import unittest
from unittest.mock import patch
from app import app, db

class TestFirebase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.db')
    def test_firebase_connection(self, mock_db):
        # Mock Firebase connection
        mock_db.return_value = True

        response = self.app.get("/check_firebase")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Firebase is connected!", response.data)

if __name__ == "__main__":
    unittest.main()