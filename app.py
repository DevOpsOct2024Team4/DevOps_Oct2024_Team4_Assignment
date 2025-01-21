from flask import Flask, render_template, request, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore

# Path to Firebase service account key JSON file
service_account_path = "path/to/serviceAccountKey.json"

# Initialize Firebase Admin SDK
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://devops-team4-default-rtdb.firebaseio.com"
})

# Firestore client
db = firestore.client()

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = "DevOps_key_Team4"  # For session and flash messages

# Sample Matriculation List (Case Study)
students = [
    {"id": "A1234567X", "name": "John Tan", "points": 50},
    {"id": "A1234568Y", "name": "Sarah Lim", "points": 80}
]
redeemable_items = [
    {"name": "Item1", "quantity": 10, "value": 100},
    {"name": "Item2", "quantity": 5, "value": 200}
]

# Page Routes

@app.route("/")
def home():
    """Landing page."""
    return render_template("index.html")
