import unittest
from unittest.mock import patch
from app import app, db

@app.route('/check_firebase')
def check_firebase():
    try:
        if db:
            return b"Firebase is connected!", 200
        else:
            return b"Firebase is NOT initialized!", 500
    except Exception:
        return b"Firebase connection error!", 500

@app.route('/admin')
def admin():
    # Example HTML Response
    return "<h1>Admin Dashboard</h1>", 200

if __name__ == "__main__":
    unittest.main()