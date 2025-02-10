from flask import Flask, render_template, request, redirect, url_for, flash, session
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os

# Load Firebase credentials from the secure folder
cred_path = os.path.join(os.path.dirname(__file__), 'config', 'firebase_credentials.json')

# Initialize Firebase only if it's not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Initialize the Flask app (Keep only one instance)
app = Flask(__name__, template_folder="templates")
app.secret_key = "DevOps_key_Team4"

@app.route("/test_firebase")
def test_firebase():
    try:
        print("Fetching students from Firestore...")
        students_ref = db.collection("students").stream()
        students = [doc.to_dict() for doc in students_ref]
        print("Students Retrieved:", students)  # Debug log
        return {"students": students}, 200
    except Exception as e:
        print("🔥 Firebase Error:", str(e))  # Debug log
        return {"error": str(e)}, 500


# Page Routes

@app.route("/check_firebase")
def check_firebase():
    try:
        if db:
            return {"message": "Firebase is connected!"}, 200
        else:
            return {"error": "Firebase is NOT initialized!"}, 500
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/")    # Landing Page
def home():
    """Landing page."""
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("Email")
        password = request.form.get("Password")

        # Debugging
        print(f"DEBUG: Email - {email}, Password - {password}")

        # Dummy validation for now (replace with Firebase auth later)
        if email == "john.tan.2024@example.edu" and password == "Johntan111":
            session["user_id"] = "A1234567X"
            return redirect(url_for("student_dashboard", student_id="A1234567X"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")

@app.route("/admin")    # Admin Page
def admin_dashboard():
    """Admin dashboard to manage students and items."""
    return render_template("admin.html", students=students, items=redeemable_items)

@app.route("/student/<student_id>")
def student_dashboard(student_id):
    student_ref = db.collection("students").document(student_id)
    student_doc = student_ref.get()

    if student_doc.exists:
        student = student_doc.to_dict()
        student["id"] = student_id  # Ensure student ID is passed

        # Fetch redeemable items correctly
        items_ref = db.collection("redeemable_items").stream()
        redeemable_items = [{"id": doc.id, **doc.to_dict()} for doc in items_ref]  # Include Firestore doc ID

        return render_template("student.html", student=student, items=redeemable_items)
    else:
        return "Student not found", 404

@app.route("/redeem", methods=["POST"])
def redeem():
    student_id = request.form.get("student_id")
    item_id = request.form.get("item_name")

    student_ref = db.collection("students").document(student_id)
    student_doc = student_ref.get()

    item_ref = db.collection("redeemable_items").document(item_id)
    item_doc = item_ref.get()

    if not student_doc.exists or not item_doc.exists:
        return "Invalid request!", 400

    student = student_doc.to_dict()
    item = item_doc.to_dict()

    if student["Points"] >= item["Value"] and item["Quantity"] > 0:
        # Deduct points and reduce stock
        new_points = student["Points"] - item["Value"]
        new_stock = item["Quantity"] - 1

        student_ref.update({"Points": new_points})
        item_ref.update({"Quantity": new_stock})

        # Send Discord Webhook
        webhook_url = "https://discord.com/api/webhooks/1337845678264549458/gqSqmxx9dQ44faBRttjkSgtawhWW2ChCq6hLTBwnqOudvKhcOtCRoeG5BdWvhVNBGaDG"
        discord_message = {
            "content": f"🎯 **Redemption Alert!**\nStudent **{student['StudentName']}** redeemed **{item['Name']}** for **{item['Value']} points**.\nPoints Left: **{new_points}**, Stock Remaining: **{new_stock}**."
        }
        try:
            response = requests.post(webhook_url, json=discord_message)
            if response.status_code == 204:
                print("Discord notification sent!")
            else:
                print(f"Failed to send Discord notification. Status code: {response.status_code}")
        except Exception as e:
            print(f"Discord Webhook Error: {e}")

        return "Redemption Successful!", 200
    else:
        return "Insufficient points or item out of stock!", 400



if __name__ == "__main__":
    app.run(debug=True)
