import unittest
from unittest.mock import patch
from app import app, send_discord_notification

class TestDiscord(unittest.TestCase):
    @patch('requests.post')
    def test_send_discord_notification(self, mock_post):
        # Mock the requests.post method
        mock_post.return_value.status_code = 204

        # Call the function
        send_discord_notification("Test message")

        # Verify the function was called correctly
        mock_post.assert_called_once()

if __name__ == "__main__":
    unittest.main()