from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from pymongo import MongoClient
from functools import wraps
from datetime import datetime, timedelta
import smtplib  # Import the smtplib library for sending emails
from email.mime.text import MIMEText  # Import MIMEText for email content
from email.mime.multipart import MIMEMultipart  # Import MIMEMultipart for email structure
from email_sender import ViolationEmailSender  # Import the ViolationEmailSender class
import csv
import io
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management and flash messages

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['aonix_test']
users_collection = db['users']
violations_collection = db['violations']
violation_record_collection = db['violation_record']
vehicle_info_collection = db['vehicle_info']
settings_collection = db['settings']  # New collection for settings

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        if not session['user'].get('is_admin', False):
            flash('Admin access required')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user in MongoDB
        user = users_collection.find_one({
            'email': email,
            'password': password
        })
        
        if user:
            # Check if user is active
            if not user.get('status', True):  # Default to True if status not set
                flash('Your account is inactive. Please contact the administrator.', 'error')
                return render_template('login.html')
            
            # Store user info in session with username instead of email
            session['user'] = {
                'username': user.get('username', email),  # Use username if available, fallback to email
                'email': user['email'],
                'is_admin': user.get('is_admin', False),
                'role': user.get('role', 'user')
            }
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get total violations count from violations collection
    total_violations = violations_collection.count_documents({})
    
    # Get current month's violations from violation_record collection
    current_month = datetime.now().month
    current_year = datetime.now().year
    this_month = violation_record_collection.count_documents({
        "Violation Date": {
            "$gte": datetime(current_year, current_month, 1),
            "$lt": datetime(current_year, current_month + 1, 1) if current_month < 12 else datetime(current_year + 1, 1, 1)
        }
    })
    
    # Get violations by zone from violation_record collection
    violations_by_zone = len(violation_record_collection.distinct("Zone"))
    
    # Get speed violations count from violation_record collection
    speed_violations = violation_record_collection.count_documents({"Violation Type": "Speeding"})
    
    # Get monthly violations data for the chart
    monthly_violations = []
    for day in range(1, 32):  # For all days in a month
        try:
            count = violation_record_collection.count_documents({
                "Violation Date": {
                    "$gte": datetime(current_year, current_month, day),
                    "$lt": datetime(current_year, current_month, day + 1)
                }
            })
            monthly_violations.append(count)
        except ValueError:
            # Handle invalid dates (e.g., February 30th)
            monthly_violations.append(0)
    
    # Recent Violations from violation_record collection
    recent_violations = list(violation_record_collection.find(
        {},
        {
            "License Plate": 1,
            "Violation Type": 1,
            "Violation Date": 1,
            "_id": 0
        }
    ).sort("Violation Date", -1).limit(5))
    
    # Format recent violations for display
    for violation in recent_violations:
        violation['formatted_date'] = violation['Violation Date'].strftime('%Y-%m-%d %H:%M')
    
    stats = {
        'total_violations': total_violations,
        'violations_by_zone': violations_by_zone,
        'this_month': this_month,
        'speed_violations': speed_violations,
        'recent_violations': recent_violations,
        'monthly_violations': monthly_violations  # Add monthly violations data
    }
    
    return render_template('dash.html', user=session['user'], stats=stats)

@app.route('/management')
@login_required
def management():
    user = session.get('user')
    # Get all vehicles from vehicle_info collection
    vehicles = list(vehicle_info_collection.find({}, {
        '_id': 0,
        'Name': 1,
        'Licence Plate': 1,
        'Email': 1,
        'Mobile Number': 1
    }))
    
    # Get all violations from violations collection
    violations = list(violations_collection.find({}, {
        '_id': 0,
        'License Plate': 1,
        'Name': 1,
        'Violation Date': 1,
        'Violation Type': 1,
        'Action Taken': 1,
        'Frequency': 1
    }).sort('Violation Date', -1))
    
    # Format dates for violations
    for violation in violations:
        if 'Violation Date' in violation:
            violation['Violation Date'] = violation['Violation Date'].strftime('%Y-%m-%d')
    
    # Check user role and render appropriate template
    if user.get('role') == 'admin':
        return render_template('management.html', user=user, vehicles=vehicles, violations=violations)
    else:
        return render_template('usermanage.html', user=user, vehicles=vehicles, violations=violations)

@app.route('/settings')
@login_required
def settings():
    user = session.get('user')
    
    # Get notification template from database, default if not found
    settings = settings_collection.find_one({}) or {}
    notification_template = settings.get('notification_template', 
                                        "Your vehicle with license plate {license_plate} has a violation.")
    
    # Get user statistics from 'users' collection in aonix_test database
    total_users = db.users.count_documents({})
    active_users = db.users.count_documents({'status': "Active"})  # Count users with status = "Active"
    admin_users = db.users.count_documents({'role': "admin"})  # Count users with role = "admin"
    
    # Get all users for the table
    users = list(db.users.find({}, {
        'username': 1,
        'email': 1,
        'role': 1,
        'status': 1,
        '_id': 0
    }))
    
    user_stats = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users
    }
    
    return render_template('setting.html', 
                         user=user, 
                         notification_template=notification_template, 
                         user_stats=user_stats,
                         users=users)

@app.route('/save_speed_threshold', methods=['POST'])
@login_required
def save_speed_threshold():
    max_speed = request.form.get('maxSpeed')
    
    # Save the max speed to the database
    settings_collection.update_one({}, {'$set': {'max_speed': max_speed}}, upsert=True)

    return jsonify({'message': 'Speed threshold saved successfully'}), 200

@app.route('/save_notification_template', methods=['POST'])
@login_required
def save_notification_template():
    data = request.get_json()
    template = data.get('template', '')
    
    # Save the template to the database
    settings_collection.update_one({}, {'$set': {'notification_template': template}}, upsert=True)

    return jsonify({'message': 'Notification template saved successfully'}), 200

@app.route('/api/send_violation_emails', methods=['POST'])
@login_required
def send_violation_emails():
    try:
        # Fetch all violations from the violations collection
        violations = list(db.violations.find())
        
        # Get the notification template from settings
        settings = settings_collection.find_one({}) or {}
        notification_template = settings.get('notification_template')
        
        # If no template is set, use a default template
        if not notification_template:
            notification_template = """Dear {owner_name},

Your vehicle with license plate {license_plate} has been involved in a {violation_type} violation on {violation_date} at {violation_time}.

Location: {location}
Frequency: {frequency}

Please drive safely.

Regards,
Traffic Management System"""
        
        # Log the template being used
        app.logger.info(f"Using notification template: {notification_template}")
        
        # Prepare email data
        email_data = []
        for violation in violations:
            # Find vehicle owner info based on license plate
            vehicle_info = db.vehicle_info.find_one({
                'Licence Plate': violation['License Plate']
            })
            
            if vehicle_info and 'Email' in vehicle_info:
                # Convert MongoDB date to string format
                violation_date = violation.get('Violation Date')
                date_str = violation_date.strftime('%Y-%m-%d') if violation_date else 'Unknown date'
                time_str = violation_date.strftime('%H:%M') if violation_date else 'Unknown time'
                
                violation_data = {
                    'owner_email': vehicle_info['Email'],
                    'owner_name': vehicle_info.get('Name', 'Vehicle Owner'),
                    'license_plate': violation.get('License Plate', 'Unknown'),
                    'speed_limit': violation.get('Speed Limit', 60),
                    'recorded_speed': violation.get('Recorded Speed', 75),
                    'violation_date': date_str,
                    'violation_time': time_str,
                    'location': violation.get('Location', 'Not specified'),
                    'violation_type': violation.get('Violation Type', 'Traffic'),
                    'frequency': violation.get('Frequency', '1'),
                    'action_taken': violation.get('Action Taken', 'Warning')
                }
                email_data.append(violation_data)
        
        if not email_data:
            return jsonify({
                'success': False,
                'message': "No valid email recipients found",
                'successful': [],
                'failed': []
            })
        
        # Log the email data
        app.logger.info(f"Prepared {len(email_data)} emails to send")
        
        # Initialize the email sender with your SMTP settings and the template
        email_sender = ViolationEmailSender(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            sender_email='shuklamayank015@gmail.com',
            sender_password='wtro mydp ojlv pibm',  # Consider using environment variables
            email_template=notification_template,
            email_subject="Traffic Violation Notification"
        )
        
        # Send emails using the email sender
        result = email_sender.send_bulk_violations(email_data)
        
        # Update violations to mark them as notified
        if result['successful']:
            for email in result['successful']:
                # Find all violations for this email
                for violation_data in email_data:
                    if violation_data['owner_email'] == email:
                        # Update the violation record to mark it as notified
                        db.violations.update_one(
                            {'License Plate': violation_data['license_plate']},
                            {'$set': {'Notified': True, 'Notification Date': datetime.now()}}
                        )
        
        return jsonify({
            'success': True,
            'message': f"Sent {len(result['successful'])} emails successfully. Failed: {len(result['failed'])}",
            'successful': result['successful'],
            'failed': result['failed']
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        app.logger.error(f"Email sending error: {str(e)}\n{error_details}")
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}",
            'details': error_details
        })

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/api/vehicles', methods=['GET'])
@login_required
def get_vehicles():
    search_term = request.args.get('search', '').lower()
    
    # Build the search query
    query = {}
    if search_term:
        query = {
            '$or': [
                {'Licence Plate': {'$regex': search_term, '$options': 'i'}},
                {'Name': {'$regex': search_term, '$options': 'i'}},
                {'Email': {'$regex': search_term, '$options': 'i'}},
                {'Mobile Number': {'$regex': search_term, '$options': 'i'}}
            ]
        }
    
    vehicles = list(vehicle_info_collection.find(query, {
        '_id': 0,
        'Name': 1,
        'Licence Plate': 1,
        'Email': 1,
        'Mobile Number': 1
    }))
    return jsonify(vehicles)

@app.route('/api/violations', methods=['GET'])
@login_required
def get_violations():
    search_term = request.args.get('search', '').lower()
    violation_type = request.args.get('type', '')
    
    # Build the search query
    query = {}
    if search_term:
        query['$or'] = [
            {'License Plate': {'$regex': search_term, '$options': 'i'}},
            {'Name': {'$regex': search_term, '$options': 'i'}}
        ]
    if violation_type:
        query['Violation Type'] = violation_type
    
    violations = list(violations_collection.find(query, {
        '_id': 0,
        'License Plate': 1,
        'Name': 1,
        'Violation Date': 1,
        'Violation Type': 1,
        'Action Taken': 1,
        'Frequency': 1
    }).sort('Violation Date', -1))
    
    # Format dates for violations
    for violation in violations:
        if 'Violation Date' in violation:
            violation['Violation Date'] = violation['Violation Date'].strftime('%Y-%m-%d')
    
    return jsonify(violations)

@app.route('/api/vehicles', methods=['POST'])
@login_required
def add_vehicle():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['Name', 'Licence Plate', 'Email', 'Mobile Number']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if license plate already exists
    if vehicle_info_collection.find_one({'Licence Plate': data['Licence Plate']}):
        return jsonify({'error': 'License plate already registered'}), 400
    
    # Insert new vehicle
    try:
        vehicle_info_collection.insert_one(data)
        return jsonify({'message': 'Vehicle added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/violations')
@login_required
def violations():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of violations per page
    
    # Get all violations from the violation_record collection
    total_violations = violation_record_collection.count_documents({})
    total_pages = (total_violations + per_page - 1) // per_page
    
    # Get violations for the current page
    violations = list(violation_record_collection.find({})
                     .sort('Violation Date', -1)  # Sort by date in descending order
                     .skip((page - 1) * per_page)
                     .limit(per_page))
    
    # Get unique zones for the filter dropdown
    zones = sorted(violation_record_collection.distinct('Zone'))
    
    return render_template('violations.html',
                         violations=violations,
                         zones=zones,
                         page=page,
                         total_pages=total_pages,
                         user=session.get('user'))

@app.route('/api/vehicles/import', methods=['POST'])
@login_required
def import_vehicles():
    try:
        data = request.get_json()
        csv_data = data.get('csvData', '')
        
        # Debug log
        app.logger.info(f"Received CSV data: {csv_data[:100]}...")
        
        # Parse CSV data
        csv_file = io.StringIO(csv_data)
        csv_reader = csv.DictReader(csv_file)
        
        # Prepare vehicles for import
        vehicles_to_import = []
        existing_plates = set()
        skipped_count = 0
        
        # Get existing license plates
        for vehicle in vehicle_info_collection.find({}, {'Licence Plate': 1}):
            existing_plates.add(vehicle['Licence Plate'])
        
        # Process each row in the CSV
        for row in csv_reader:
            # Debug log
            app.logger.info(f"Processing row: {row}")
            
            # Skip if required fields are missing
            if not all(field in row for field in ['Name', 'Licence Plate', 'Email', 'Mobile Number']):
                app.logger.warning(f"Skipping row due to missing fields: {row}")
                skipped_count += 1
                continue
                
            # Skip if license plate already exists
            if row['Licence Plate'] in existing_plates:
                app.logger.warning(f"Skipping row due to duplicate license plate: {row['Licence Plate']}")
                skipped_count += 1
                continue
                
            # Add to import list
            vehicles_to_import.append(row)
            existing_plates.add(row['Licence Plate'])
        
        # Insert vehicles into database
        imported_count = 0
        if vehicles_to_import:
            result = vehicle_info_collection.insert_many(vehicles_to_import)
            imported_count = len(result.inserted_ids)
            app.logger.info(f"Imported {imported_count} vehicles")
        
        return jsonify({
            'success': True,
            'imported': imported_count,
            'skipped': skipped_count,
            'message': f'Successfully imported {imported_count} vehicles ({skipped_count} skipped)'
        })
        
    except Exception as e:
        app.logger.error(f"Error importing vehicles: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Get system statistics
    total_users = users_collection.count_documents({})
    total_vehicles = vehicle_info_collection.count_documents({})
    total_violations = violations_collection.count_documents({})
    
    # Get recent system activities
    recent_violations = list(violation_record_collection.find()
                           .sort("Violation Date", -1)
                           .limit(10))
    
    # Get violation statistics
    violation_types = violation_record_collection.aggregate([
        {"$group": {"_id": "$Violation Type", "count": {"$sum": 1}}}
    ])
    
    stats = {
        'total_users': total_users,
        'total_vehicles': total_vehicles,
        'total_violations': total_violations,
        'recent_violations': recent_violations,
        'violation_types': list(violation_types)
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/users')
@admin_required
def manage_users():
    users = list(users_collection.find({}, {'password': 0}))
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
@admin_required
def add_user():
    data = request.form
    new_user = {
        'email': data['email'],
        'fullname': data['fullname'],
        'password': data['password'],  # In production, hash this password
        'is_admin': data.get('is_admin') == 'true',
        'created_at': datetime.now()
    }
    
    try:
        users_collection.insert_one(new_user)
        flash('User added successfully')
    except Exception as e:
        flash('Error adding user: ' + str(e))
    
    return redirect(url_for('manage_users'))

@app.route('/admin/users/<email>/delete', methods=['POST'])
@admin_required
def delete_user(email):
    if session['user']['email'] == email:
        flash('Cannot delete your own account')
        return redirect(url_for('manage_users'))
    
    users_collection.delete_one({'email': email})
    flash('User deleted successfully')
    return redirect(url_for('manage_users'))

@app.route('/admin/settings')
@admin_required
def admin_settings():
    # Get all system settings
    settings = settings_collection.find_one({}) or {}
    return render_template('admin/settings.html', settings=settings)

@app.route('/admin/settings/update', methods=['POST'])
@admin_required
def update_settings():
    data = request.form
    settings = {
        'max_speed': float(data.get('max_speed', 0)),
        'notification_template': data.get('notification_template', ''),
        'email_settings': {
            'smtp_server': data.get('smtp_server'),
            'smtp_port': int(data.get('smtp_port', 587)),
            'smtp_username': data.get('smtp_username'),
            'smtp_password': data.get('smtp_password')
        },
        'updated_at': datetime.now()
    }
    
    settings_collection.update_one({}, {'$set': settings}, upsert=True)
    flash('Settings updated successfully')
    return redirect(url_for('admin_settings'))

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit

        # Get total count of users
        total_users = db.users.count_documents({})

        # Get paginated users
        users = list(db.users.find({}, {
            'username': 1,
            'email': 1,
            'role': 1,
            'status': 1,
            'lastLogin': 1,
            '_id': 1
        }).skip(skip).limit(limit))

        # Format the response
        formatted_users = []
        for user in users:
            formatted_users.append({
                'id': str(user['_id']),
                'username': user.get('username', ''),
                'email': user.get('email', ''),
                'role': user.get('role', 'user'),
                'status': user.get('status', False),
                'lastLogin': user.get('lastLogin', None)
            })

        return jsonify({
            'users': formatted_users,
            'total': total_users,
            'page': page,
            'pages': (total_users + limit - 1) // limit
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    try:
        user = db.users.find_one({'_id': ObjectId(user_id)}, {
            'username': 1,
            'email': 1,
            'role': 1,
            'status': 1,
            '_id': 1
        })
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'id': str(user['_id']),
            'username': user.get('username', ''),
            'email': user.get('email', ''),
            'role': user.get('role', 'user'),
            'status': user.get('status', False)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>/status', methods=['PUT'])
@login_required
def update_user_status(user_id):
    try:
        data = request.get_json()
        status = data.get('status', False)
        
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'status': status}}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({'message': 'User status updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['DELETE'])
@login_required
def delete_user_api(user_id):
    try:
        result = db.users.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
@login_required
def create_user():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Check if user with same email already exists
        if db.users.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already registered'}), 400
            
        # Prepare user document
        user_doc = {
            'username': data['username'],
            'email': data['email'],
            'password': data['password'] if data.get('password') else None,
            'role': data['role'],
            'status': data.get('status', True),
            'createdAt': datetime.now()
        }
        
        # Insert the user
        result = db.users.insert_one(user_doc)
        
        return jsonify({
            'message': 'User created successfully',
            'userId': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Check if user exists
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Check if email is being changed and if new email already exists
        if data['email'] != user['email'] and db.users.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already registered'}), 400
            
        # Prepare update document
        update_doc = {
            'username': data['username'],
            'email': data['email'],
            'role': data['role'],
            'status': data.get('status', True)
        }
        
        # Only update password if provided
        if data.get('password'):
            update_doc['password'] = data['password']
            
        # Update the user
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_doc}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'No changes made'}), 400
            
        return jsonify({
            'message': 'User updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/export', methods=['GET'])
@login_required
def export_users():
    try:
        # Get all users from the database
        users = list(db.users.find({}, {
            'username': 1,
            'email': 1,
            'role': 1,
            'status': 1,
            'createdAt': 1,
            'lastLogin': 1,
            '_id': 0
        }))

        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Username', 'Email', 'Role', 'Status', 'Created At', 'Last Login'])
        
        # Write data
        for user in users:
            writer.writerow([
                user.get('username', ''),
                user.get('email', ''),
                user.get('role', ''),
                'Active' if user.get('status', True) else 'Inactive',
                user.get('createdAt', '').strftime('%Y-%m-%d %H:%M:%S') if user.get('createdAt') else '',
                user.get('lastLogin', '').strftime('%Y-%m-%d %H:%M:%S') if user.get('lastLogin') else 'Never'
            ])

        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=users_export_{datetime.now().strftime("%Y%m%d")}.csv'
            }
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/import', methods=['POST'])
@login_required
def import_users():
    try:
        data = request.get_json()
        csv_data = data.get('csvData', '')
        
        # Parse CSV data
        csv_file = io.StringIO(csv_data)
        csv_reader = csv.DictReader(csv_file)
        
        # Prepare users for import
        users_to_import = []
        existing_emails = set()
        skipped_count = 0
        
        # Get existing emails
        for user in db.users.find({}, {'email': 1}):
            existing_emails.add(user['email'])
        
        # Process each row in the CSV
        for row in csv_reader:
            # Skip if required fields are missing
            if not all(field in row for field in ['username', 'email', 'role']):
                skipped_count += 1
                continue
                
            # Skip if email already exists
            if row['email'] in existing_emails:
                skipped_count += 1
                continue
                
            # Prepare user document
            user_doc = {
                'username': row['username'],
                'email': row['email'],
                'password': row.get('password'),
                'role': row['role'],
                'status': row.get('status', 'true').lower() == 'true',
                'createdAt': datetime.now()
            }
            
            # Add to import list
            users_to_import.append(user_doc)
            existing_emails.add(row['email'])
        
        # Insert users into database
        imported_count = 0
        if users_to_import:
            result = db.users.insert_many(users_to_import)
            imported_count = len(result.inserted_ids)
        
        return jsonify({
            'success': True,
            'imported': imported_count,
            'skipped': skipped_count,
            'message': f'Successfully imported {imported_count} users ({skipped_count} skipped)'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users/template', methods=['GET'])
@login_required
def download_user_template():
    try:
        # Create CSV data with example row
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['username', 'email', 'password', 'role', 'status'])
        
        # Write example row
        writer.writerow([
            'john_doe',
            'john@example.com',
            'password123',
            'admin',
            'true'
        ])

        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=user_import_template.csv'
            }
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles/<license_plate>', methods=['DELETE'])
@login_required
def delete_vehicle(license_plate):
    try:
        result = vehicle_info_collection.delete_one({'Licence Plate': license_plate})
        if result.deleted_count == 0:
            return jsonify({'error': 'Vehicle not found'}), 404
        return jsonify({'message': 'Vehicle deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/violations/<license_plate>/<violation_date>', methods=['DELETE'])
@login_required
def delete_violation(license_plate, violation_date):
    try:
        # Convert the date string back to datetime for comparison
        violation_date = datetime.strptime(violation_date, '%Y-%m-%d')
        result = violations_collection.delete_one({
            'License Plate': license_plate,
            'Violation Date': violation_date
        })
        if result.deleted_count == 0:
            return jsonify({'error': 'Violation not found'}), 404
        return jsonify({'message': 'Violation deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles/<license_plate>', methods=['GET'])
@login_required
def get_vehicle(license_plate):
    try:
        vehicle = vehicle_info_collection.find_one({'Licence Plate': license_plate}, {'_id': 0})
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        return jsonify(vehicle)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles/<license_plate>', methods=['PUT'])
@login_required
def update_vehicle(license_plate):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['Name', 'Email', 'Mobile Number']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if new license plate already exists (if it's being changed)
        if 'Licence Plate' in data and data['Licence Plate'] != license_plate:
            if vehicle_info_collection.find_one({'Licence Plate': data['Licence Plate']}):
                return jsonify({'error': 'New license plate already registered'}), 400
        
        # Update vehicle
        result = vehicle_info_collection.update_one(
            {'Licence Plate': license_plate},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Vehicle not found'}), 404
            
        return jsonify({'message': 'Vehicle updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/violations/<license_plate>/<violation_date>', methods=['GET'])
@login_required
def get_violation(license_plate, violation_date):
    try:
        violation_date = datetime.strptime(violation_date, '%Y-%m-%d')
        violation = violations_collection.find_one({
            'License Plate': license_plate,
            'Violation Date': violation_date
        }, {'_id': 0})
        
        if not violation:
            return jsonify({'error': 'Violation not found'}), 404
            
        # Convert datetime to string for JSON serialization
        violation['Violation Date'] = violation['Violation Date'].strftime('%Y-%m-%d')
        return jsonify(violation)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/violations/<license_plate>/<violation_date>', methods=['PUT'])
@login_required
def update_violation(license_plate, violation_date):
    try:
        data = request.get_json()
        violation_date = datetime.strptime(violation_date, '%Y-%m-%d')
        
        # Validate required fields
        required_fields = ['Violation Type', 'Action Taken']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Update violation
        result = violations_collection.update_one(
            {
                'License Plate': license_plate,
                'Violation Date': violation_date
            },
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Violation not found'}), 404
            
        return jsonify({'message': 'Violation updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 