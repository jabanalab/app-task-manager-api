from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from db import init_db, add_user, get_user, add_task, get_tasks, mark_task_complete, delete_task
from functools import wraps

app = Flask(__name__, static_folder=\'static\', static_url_path=\'/\')
CORS(app)
app.secret_key = \'super_secret_key\' # Intentional vulnerability: hardcoded secret key

@app.before_request
def before_request():
    init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if \'user_id\' not in session:
            return jsonify({\'message\': \'Unauthorized\'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route(\'/\')
def index():
    return send_from_directory(app.static_folder, \'index.html\')

@app.route(\'/api/register\', methods=[\'POST\'])
def register():
    data = request.get_json()
    username = data.get(\'username\')
    password = data.get(\'password\')
    if not username or not password:
        return jsonify({\'message\': \'Username and password are required\'}), 400
    try:
        add_user(username, password) # Intentional vulnerability: no password hashing
        return jsonify({\'message\': \'User registered successfully\'}), 201
    except Exception as e:
        return jsonify({\'message\': str(e)}), 400

@app.route(\'/api/login\', methods=[\'POST\'])
def login():
    data = request.get_json()
    username = data.get(\'username\')
    password = data.get(\'password\')
    user = get_user(username, password) # Intentional vulnerability: SQL injection in get_user
    if user:
        session[\'user_id\'] = user[\'id\']
        session[\'username\'] = user[\'username\']
        return jsonify({\'message\': \'Login successful\', \'username\': user[\'username\']}), 200
    else:
        return jsonify({\'message\': \'Invalid credentials\'}), 401

@app.route(\'/api/logout\', methods=[\'POST\'])
@login_required
def logout():
    session.pop(\'user_id\', None)
    session.pop(\'username\', None)
    return jsonify({\'message\': \'Logged out successfully\'}), 200

@app.route(\'/api/tasks\', methods=[\'POST\'])
@login_required
def add_task_api():
    data = request.get_json()
    description = data.get(\'description\')
    if not description:
        return jsonify({\'message\': \'Task description is required\'}), 400
    add_task(session[\'user_id\'], description) # Intentional vulnerability: XSS in description
    return jsonify({\'message\': \'Task added successfully\'}), 201

@app.route(\'/api/tasks\', methods=[\'GET\'])
@login_required
def get_tasks_api():
    tasks = get_tasks(session[\'user_id\'])
    return jsonify([dict(task) for task in tasks]), 200

@app.route(\'/api/tasks/<int:task_id>/complete\', methods=[\'PUT\'])
@login_required
def complete_task_api(task_id):
    mark_task_complete(task_id) # Intentional vulnerability: IDOR, no authorization check
    return jsonify({\'message\': \'Task marked as complete\'}), 200

@app.route(\'/api/tasks/<int:task_id>\', methods=[\'DELETE\'])
@login_required
def delete_task_api(task_id):
    delete_task(task_id) # Intentional vulnerability: IDOR, no authorization check
    return jsonify({\'message\': \'Task deleted\'}), 200

if __name__ == \'__main__\':
    app.run(debug=True) # Intentional vulnerability: debug mode enabled in production-like environment
