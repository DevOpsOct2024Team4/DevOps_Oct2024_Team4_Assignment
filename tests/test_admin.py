import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestAdminRoute(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    @patch('app.db.collection')
    def test_admin(self, mock_db):
        """Test admin page access"""
        mock_admin = MagicMock()
        mock_admin.to_dict.return_value = {'role': 'admin'}
        mock_db.return_value.where.return_value.stream.return_value = [mock_admin]
        
        # Simulate admin login before accessing the admin dashboard
        with self.client.session_transaction() as session:
            session['user_role'] = 'admin'

        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
