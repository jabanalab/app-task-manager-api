import sqlite3

DATABASE = 'database.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()

def add_user(username, password):
    # Intentional vulnerability: Plain text password storage
    with get_db() as db:
        db.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
        db.commit()

def get_user(username, password):
    # Intentional vulnerability: SQL Injection via string concatenation
    with get_db() as db:
        cursor = db.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
        user = cursor.fetchone()
        return user

def add_task(user_id, description):
    # Intentional vulnerability: No input sanitization for description
    with get_db() as db:
        db.execute(f"INSERT INTO tasks (user_id, description, completed) VALUES ({user_id}, '{description}', 0)")
        db.commit()

def get_tasks(user_id):
    with get_db() as db:
        cursor = db.execute(f"SELECT * FROM tasks WHERE user_id = {user_id}")
        tasks = cursor.fetchall()
        return tasks

def mark_task_complete(task_id):
    # Intentional vulnerability: No authorization check (IDOR)
    with get_db() as db:
        db.execute(f"UPDATE tasks SET completed = 1 WHERE id = {task_id}")
        db.commit()

def delete_task(task_id):
    # Intentional vulnerability: No authorization check (IDOR)
    with get_db() as db:
        db.execute(f"DELETE FROM tasks WHERE id = {task_id}")
        db.commit()
