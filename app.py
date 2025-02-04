from flask import Flask, render_template, request, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore

# Use the new JSON credentials file
cred = credentials.Certificate("firebase_credentials.json")
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
    """Handle item redemption by students."""
    student_id = request.form.get("student_id")
    item_id = request.form.get("item_name")  # Use Firestore doc ID

    print(f"🔍 Debug: Attempting to redeem {item_id} for student {student_id}")

    if not student_id or not item_id:
        print("❌ ERROR: Missing student ID or item ID")
        return "Invalid request!", 400

    # Fetch student and item from Firestore
    student_ref = db.collection("students").document(student_id)
    student_doc = student_ref.get()

    item_ref = db.collection("redeemable_items").document(item_id)
    item_doc = item_ref.get()

    if not student_doc.exists:
        print("❌ ERROR: Student not found!")
        return "Student not found!", 404

    if not item_doc.exists:
        print("❌ ERROR: Item not found!")
        return "Item not found!", 404

    student = student_doc.to_dict()
    item = item_doc.to_dict()

    print(f"🎯 Before Redemption: Student Points = {student['Points']}, Item Stock = {item['Quantity']}")

    if student["Points"] >= item["Value"] and item["Quantity"] > 0:
        # Deduct points and reduce stock
        student_ref.update({"Points": student["Points"] - item["Value"]})
        item_ref.update({"Quantity": item["Quantity"] - 1})

        print(f"✅ Redemption Successful! New Points = {student['Points'] - item['Value']}, New Stock = {item['Quantity'] - 1}")
        return "Redemption Successful!", 200
    else:
        print("❌ ERROR: Insufficient points or item out of stock!")
        return "Insufficient points or item out of stock!", 400


    return redirect(url_for("student_dashboard", student_id=student_id))

if __name__ == "__main__":
    app.run(debug=True)