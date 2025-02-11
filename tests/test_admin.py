import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestAdminRoute(unittest.TestCase):

    def setUp(self):
        """Setup test client"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    @patch('app.db.collection')
    def test_admin(self, mock_db):
        """Test admin page access"""
        mock_admin = MagicMock()
        mock_admin.to_dict.return_value = {'role': 'admin'}
        mock_db.return_value.where.return_value.stream.return_value = [mock_admin]
        
        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)

if __name__ == '__main__':
    unittest.main()
