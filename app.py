from flask import Flask, render_template, request, redirect, url_for, flash, session
import firebase_admin
from firebase_admin import credentials, firestore
from functools import wraps
from datetime import datetime, timedelta
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
app.permanent_session_lifetime = timedelta(minutes=5)

@app.before_request
def make_session_permanent():
    session.permanent = True
    session.modified = True

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash("Access denied: Admins only!", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Function to log audit actions
def log_audit_action(action, details):
    admin_name = session.get('admin_name', 'Unknown Admin')
    audit_ref = db.collection('audit_logs')
    log_data = {
        'admin_name': admin_name,
        'action': action,
        'details': details,
        'timestamp': datetime.utcnow()
    }
    audit_ref.add(log_data)

# Discord Webhook Integration
def send_discord_notification(message):
    webhook_url = 'https://discord.com/api/webhooks/1338542484036386969/16kfW53a89Nu-a-MWf5Q8Rmfog8iS_My6PQkeVY8kRNf01Amt3n6-JAtWIE-XgnK7tGL'
    data = {"content": message}
    requests.post(webhook_url, json=data)

@app.route("/")    
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')

        # Check Students Collection
        students_ref = db.collection('students')
        student_query = students_ref.where('Email', '==', email).where('Password', '==', password).stream()

        student = None
        for doc in student_query:
            student = doc.to_dict()
            student['id'] = doc.id
            break

        if student:
            session['user_id'] = student['id']
            session['role'] = 'student'
            return redirect(url_for('student_dashboard', student_id=student['id']))

        # Check Admins Collection if student not found
        admins_ref = db.collection('admins')
        admin_query = admins_ref.where('Email', '==', email).where('Password', '==', password).stream()

        admin = None
        for doc in admin_query:
            admin = doc.to_dict()
            admin['id'] = doc.id
            break

        if admin:
            session['user_id'] = admin['id']
            session['admin_name'] = admin['Name']
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))

        flash("Invalid email or password.", "danger")

    return render_template('login.html')


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


@app.route('/admin')
@admin_required
def admin_dashboard():
    students = [{**doc.to_dict(), 'id': doc.id} for doc in db.collection('students').stream()]
    items = [{**doc.to_dict(), 'id': doc.id} for doc in db.collection('redeemable_items').stream()]
    audit_logs = [{**doc.to_dict(), 'id': doc.id} for doc in db.collection('audit_logs').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()]
    
    return render_template('admin.html', students=students, items=items, audit_logs=audit_logs)


@app.route('/admin/create-student', methods=['GET', 'POST'])
@admin_required
def create_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        student_data = {
            'StudentName': request.form.get('student_name'),
            'Email': request.form.get('email'),
            'Password': request.form.get('password'),
            'Points': int(request.form.get('points')),
            'DiplomaStudy': request.form.get('diploma_study'),  # Added
            'EntryYear': int(request.form.get('entry_year'))
        }
        db.collection('students').document(student_id).set(student_data)
        
        send_discord_notification(f'📝 New student created: {student_data["StudentName"]}')
        log_audit_action('create_student', f'Created student {student_data["StudentName"]}')
        
        flash('Student account created successfully!', 'success')
        return redirect(url_for('list_students'))

    return render_template('create_student.html')


@app.route('/admin/delete-student/<student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student_ref = db.collection('students').document(student_id)
    student = student_ref.get()

    if student.exists:
        student_name = student.to_dict().get('StudentName', 'Unknown')
        student_ref.delete()

        # Send Discord notification
        send_discord_notification(f'❌ Student {student_id} ({student_name}) deleted.')

        # Log the action
        admin_id = session.get('user_id')
        log_audit_action('delete_student', f'Deleted student {student_name}')

        flash('Student account deleted successfully!', 'success')
    else:
        flash('Student not found!', 'danger')

    return redirect(url_for('list_students'))

@app.route('/admin/modify-student/<student_id>', methods=['GET', 'POST'])
@admin_required
def modify_student(student_id):
    student_ref = db.collection('students').document(student_id)
    student = student_ref.get()

    if not student.exists:
        flash('Student not found!', 'danger')
        return redirect(url_for('list_students'))

    if request.method == 'POST':
        updated_data = {
            'StudentName': request.form.get('student_name'),
            'Email': request.form.get('email'),
            'Password': request.form.get('password'),
            'Points': int(request.form.get('points')),
            'DiplomaStudy': request.form.get('diploma_study'),  # Added
            'EntryYear': int(request.form.get('entry_year'))
        }
        student_ref.update(updated_data)

        send_discord_notification(f'✏️ Student {updated_data["StudentName"]} modified.')
        log_audit_action('modify_student', f'Modified student {updated_data["StudentName"]}')

        flash('Student account updated successfully!', 'success')
        return redirect(url_for('list_students'))

    return render_template('modify_student.html', student={**student.to_dict(), 'id': student_id}, student_id=student_id)

@app.route("/student/<student_id>")
def student_dashboard(student_id):
    student_ref = db.collection("students").document(student_id)
    student_doc = student_ref.get()

    if student_doc.exists:
        student = student_doc.to_dict()
        student["id"] = student_id  

        items_ref = db.collection("redeemable_items").stream()
        redeemable_items = [{"id": doc.id, **doc.to_dict()} for doc in items_ref]  

        return render_template("student.html", student=student, items=redeemable_items)
    else:
        return "Student not found", 404
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
@admin_required
def manage_items():
    items_ref = db.collection('redeemable_items')

    if request.method == 'POST':
        item_id = request.form.get('item_id')
        value = request.form.get('value')
        quantity = request.form.get('quantity')

        # Handle NoneType and invalid input for PointsCost and Stock
        item_data = {
            'Name': request.form.get('item_name'),
            'Value': int(value) if value and value.isdigit() else 0,
            'Quantity': int(quantity) if quantity and quantity.isdigit() else 0
        }

        items_ref.document(item_id).set(item_data)

        # Send Discord notification
        send_discord_notification(f'📦 New item created: {item_data["Name"]} (Cost: {item_data["Value"]} points, Quantity: {item_data["Quantity"]})')

        # Log the action
        admin_id = session.get('user_id')
        log_audit_action('create_item', f'Created item {item_data["Name"]}')

        flash('Item created successfully! ✔️', 'success')
        return redirect(url_for('manage_items'))

    items = [{**doc.to_dict(), 'id': doc.id} for doc in items_ref.stream()]
    return render_template('manage_items.html', items=items)

@app.route('/admin/modify-item/<item_id>', methods=['GET', 'POST'])
@admin_required
def modify_item(item_id):
    item_ref = db.collection('redeemable_items').document(item_id)
    item = item_ref.get()

    if not item.exists:
        flash('Item not found!', 'danger')
        return redirect(url_for('manage_items'))

    if request.method == 'POST':
        updated_data = {
            'Name': request.form.get('item_name'),
            'Quantity': int(request.form.get('quantity')),
            'Value': int(request.form.get('value'))
        }
        item_ref.update(updated_data)

        # Send Discord notification
        send_discord_notification(f'✏️ Item {updated_data["Name"]} modified.')

        # Log the action
        admin_id = session.get('user_id')
        log_audit_action('modify_item', f'Modified item {updated_data["Name"]}')

        flash('Item updated successfully!', 'success')
        return redirect(url_for('manage_items'))

    return render_template('modify_item.html', item={**item.to_dict(), 'id': item_id})


@app.route('/admin/delete-item/<item_id>', methods=['POST'])
@admin_required
def delete_item(item_id):
    item_ref = db.collection('redeemable_items').document(item_id)
    item = item_ref.get()

    if item.exists:
        item_name = item.to_dict().get('Name', 'Unknown')
        item_ref.delete()

        # Send Discord notification
        send_discord_notification(f'🗑️ Item `{item_id}` ({item_name}) deleted.')

        # Log the action
        admin_id = session.get('user_id')
        log_audit_action(action='delete_item', details=f'Deleted item {item_name}')

        flash('Item deleted successfully!', 'success')
    else:
        flash('Item not found!', 'danger')

    return redirect(url_for('manage_items'))

@app.route("/student/<student_id>", endpoint='student_dashboard_view')
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

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
