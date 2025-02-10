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

# Discord Webhook Integration
def send_discord_notification(message):
    webhook_url = 'https://discord.com/api/webhooks/1338542484036386969/16kfW53a89Nu-a-MWf5Q8Rmfog8iS_My6PQkeVY8kRNf01Amt3n6-JAtWIE-XgnK7tGL'
    data = {"content": message}
    requests.post(webhook_url, json=data)

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

        try:
            # Fetch student record from Firestore
            students_ref = db.collection('students').where('Email', '==', email).stream()

            for doc in students_ref:
                student_data = doc.to_dict()

                # Check if the password matches
                if student_data.get("Password") == password:
                    session["user_id"] = doc.id
                    flash("Logged in successfully!", "success")
                    return redirect(url_for("student_dashboard", student_id=doc.id))
                else:
                    flash("Invalid password.", "danger")
                    return redirect(url_for("login"))

            flash("Email not found.", "danger")
            return redirect(url_for("login"))

        except Exception as e:
            print(f"Error: {e}")
            flash(f"An error occurred: {str(e)}", "danger")

    return render_template("login.html")


@app.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')

        try:
            print(f"🔍 Trying to reset password for: {email}")  # Debugging line
            students_ref = db.collection('students').where('Email', '==', email).stream()
            student_found = False

            for doc in students_ref:
                student_id = doc.id
                print(f"✅ Found student ID: {student_id}")  # Debugging line
                db.collection('students').document(student_id).update({'Password': new_password})
                student_found = True
                send_discord_notification(f'🔑 Password updated for {email}')
                flash('Password has been successfully updated!', 'success')
                return redirect(url_for('login'))

            if not student_found:
                flash('No student found with the provided email.', 'danger')

        except Exception as e:
            print(f"❌ Error: {e}")  # Debugging line
            flash(f"An error occurred: {str(e)}", 'danger')

    return render_template('recover_password.html')


@app.route("/admin")    # Admin Page
def admin_dashboard():
    """Admin dashboard to manage students and items."""
    try:
        # Fetch student data from Firestore
        students_ref = db.collection("students").stream()
        students = [{**doc.to_dict(), 'id': doc.id} for doc in students_ref]  # Add the document ID

        # Fetch redeemable items from Firestore
        items_ref = db.collection("redeemable_items").stream()
        redeemable_items = [{"id": doc.id, **doc.to_dict()} for doc in items_ref]  # Include Firestore doc ID

        return render_template("admin.html", students=students, items=redeemable_items)

    except Exception as e:
        print(f"🔥 Error fetching data for Admin Dashboard: {e}")
        return "Error loading admin dashboard", 500


@app.route('/admin/create-student', methods=['GET', 'POST'])
def create_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        student_data = {
            'StudentName': request.form.get('student_name'),
            'Email': request.form.get('email'),
            'Password': request.form.get('password'),
            'Points': int(request.form.get('points')),
            'DiplomaStudy': request.form.get('diploma_study'),
            'EntryYear': int(request.form.get('entry_year'))
        }
        db.collection('students').document(student_id).set(student_data)
        send_discord_notification(f'📝 New student created: {student_data["StudentName"]}')
        flash('Student account created successfully!', 'success')
        return redirect(url_for('list_students'))

    return render_template('create_student.html')

@app.route('/admin/modify-student/<student_id>', methods=['GET', 'POST'])
def modify_student(student_id):
    student_ref = db.collection('students').document(student_id)
    student_doc = student_ref.get()

    if not student_doc.exists:
        flash('Student not found!', 'danger')
        return redirect(url_for('list_students'))

    student = student_doc.to_dict()

    if request.method == 'POST':
        updated_data = {
            'StudentName': request.form.get('student_name'),
            'Email': request.form.get('email'),
            'EntryYear': int(request.form.get('entry_year')),
            'Points': int(request.form.get('points'))
        }
        student_ref.update(updated_data)
        send_discord_notification(f'✏️ Student {student_id} modified.')
        flash('Student account updated successfully!', 'success')
        return redirect(url_for('list_students'))

    return render_template('modify_student.html', student=student)

@app.route('/admin/delete-student/<student_id>', methods=['GET'])
def delete_student(student_id):
    student_ref = db.collection('students').document(student_id)
    student_doc = student_ref.get()

    if not student_doc.exists:
        flash('Student not found!', 'danger')
    else:
        student_ref.delete()
        send_discord_notification(f'❌ Student {student_id} deleted.')
        flash('Student account deleted successfully!', 'success')

    return redirect(url_for('list_students'))

@app.route('/admin/list-students', methods=['GET'])
def list_students():
    students_ref = db.collection('students').stream()
    students = [{**doc.to_dict(), 'id': doc.id} for doc in students_ref]
    return render_template('list_students.html', students=students)

@app.route('/admin/search-student', methods=['GET'])
def search_student():
    query = request.args.get('query')
    results = []
    students_ref = db.collection('students')

    # Search by Student ID
    doc = students_ref.document(query).get()
    if doc.exists:
        results.append({**doc.to_dict(), 'id': doc.id})

    # Search by Student Name
    query_ref = students_ref.where('StudentName', '==', query).stream()
    results.extend([{**doc.to_dict(), 'id': doc.id} for doc in query_ref])

    return render_template('list_students.html', students=results)

@app.route('/admin/manage-items', methods=['GET', 'POST'])
def manage_items():
    items_ref = db.collection('redeemable_items').stream()
    items = [{**doc.to_dict(), 'id': doc.id} for doc in items_ref]

    if request.method == 'POST':
        item_id = request.form.get('item_id')
        item_data = {
            'Name': request.form.get('item_name'),
            'Quantity': int(request.form.get('quantity')),
            'Value': int(request.form.get('value'))
        }

        if item_id:  # Update if item_id exists
            db.collection('redeemable_items').document(item_id).update(item_data)
            send_discord_notification(f'🔄 Item {item_id} updated.')
            flash('Item updated successfully!', 'success')
        else:  # Otherwise, create new item
            new_item_ref = db.collection('redeemable_items').document()
            new_item_ref.set(item_data)
            send_discord_notification(f'🎁 New item created: {item_data["Name"]}')
            flash('Item created successfully!', 'success')

        return redirect(url_for('manage_items'))

    return render_template('manage_items.html', items=items)

@app.route('/admin/delete-item/<item_id>', methods=['GET'])
def delete_item(item_id):
    item_ref = db.collection('redeemable_items').document(item_id)
    item_doc = item_ref.get()

    if not item_doc.exists:
        flash('Item not found!', 'danger')
    else:
        item_ref.delete()
        send_discord_notification(f'🗑️ Item {item_id} deleted.')
        flash('Item deleted successfully!', 'success')

    return redirect(url_for('manage_items'))

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
