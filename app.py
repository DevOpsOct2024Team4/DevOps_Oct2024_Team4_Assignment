from flask import Flask, render_template, request, redirect, url_for, flash

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
