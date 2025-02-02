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

# Sample Matriculation List (Case Study) [Replace with firebase data when ready]
students = [
    {"id": "A1234567X", "name": "John Tan", "points": 50},
    {"id": "A1234568Y", "name": "Sarah Lim", "points": 80}
]
redeemable_items = [
    {"name": "Item1", "quantity": 10, "value": 100},
    {"name": "Item2", "quantity": 5, "value": 200}
]

# Page Routes

@app.route("/")    # Landing Page
def home():
    """Landing page."""
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])    # Login Page
def login():
    """Login page for both admin and students."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # To be replaced with authentication logic later on
        if username and password:
            # Redirect to different pages based on user type (Improve later on if neccessary)
            if username == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("student_dashboard", student_id=username))
        else:
            flash("Invalid username or password")
    return render_template("login.html")

@app.route("/admin")    # Admin Page
def admin_dashboard():
    """Admin dashboard to manage students and items."""
    return render_template("admin.html", students=students, items=redeemable_items)

@app.route("/student/<student_id>")    # Student Page
def student_dashboard(student_id):
    """Student dashboard to view and redeem items."""
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return "Student ID not found!", 404
    return render_template("student.html", student=student, items=redeemable_items)

@app.route("/redeem", methods=["POST"])    # Redeem Page
def redeem():
    """Handle item redemption by students."""
    student_id = request.form["student_id"]
    item_name = request.form["item_name"]

    # Find student and item
    student = next((s for s in students if s["id"] == student_id), None)
    item = next((i for i in redeemable_items if i["name"] == item_name), None)

    # Points Redemption Logic
    if student and item:
        if student["points"] >= item["value"] and item["quantity"] > 0:
            student["points"] -= item["value"]
            item["quantity"] -= 1
            flash(f"Successfully redeemed {item_name}!")
        else:
            flash("You have insufficient points or the item out of stock.")
    else:
        flash("Invalid student or item.")
    return redirect(url_for("student_dashboard", student_id=student_id))

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/test_firebase")    # Test firebase connection
def test_firebase():
    try:
        # Trying to fetch documents from Firestore
        students_ref = db.collection("students")
        students = [doc.to_dict() for doc in students_ref.stream()]
        return {"students": students}, 200
    except Exception as e:
        return {"error": str(e)}, 500
