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
    Fetch a single employee record from the database using the employee_id.
    Returns a dictionary with employee details if found; otherwise, returns None.
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        query = "SELECT employee_id, password, name, role FROM employees WHERE employee_id = ?"
        cursor.execute(query, (employee_id,))
        row = cursor.fetchone()
        if row:
            # Build and return the dictionary of employee data
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


def fetch_all_employees():
    """
    Fetch all employee records from the database.
    Returns a list of dictionaries, each containing employee details.
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        query = "SELECT employee_id, password, name, role FROM employees"
        cursor.execute(query)
        rows = cursor.fetchall()

        employees = []
        for row in rows:
            employees.append({
                'employee_id': row[0],
                'password': row[1],
                'name': row[2],
                'role': row[3]
            })
        return employees
    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        return []
    finally:
        conn.close()


# For testing purposes (optional)
if __name__ == "__main__":
    # Fetch a single employee record (change "EMP0001" to an ID present in your database)
    emp = fetch_employee("EMP0001")
    if emp:
        print("Fetched Employee:")
        print(emp)
    else:
        print("Employee not found.")

    # Fetch all employees
    all_emps = fetch_all_employees()
    print("\nAll Employees:")
    for emp in all_emps:
        print(emp)
