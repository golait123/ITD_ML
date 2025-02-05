import sqlite3

DB_PATH = 'employee.db'  # Path to your SQLite database file

def get_connection():
    """Create and return a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def fetch_employee(employee_id):
    """
    Fetch an employee record from the database using employee_id (username).
    Returns a dictionary with employee details if found; otherwise, returns None.
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT employee_id, password, name, role FROM employees WHERE employee_id = ?", (employee_id,))
        row = cursor.fetchone()
        if row:
            # Assuming table columns: employee_id, password, name, role
            employee = {
                'employee_id': row[0],
                'password': row[1],
                'name': row[2],
                'role': row[3]
            }
            return employee
        else:
            return None
    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        return None
    finally:
        conn.close()
