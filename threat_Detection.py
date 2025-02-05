from database import fetch_employee


def authenticate(employee_id, password):
    """
    Authenticate the user by comparing the provided password with the database record.
    Returns the employee details if authentication is successful; otherwise, returns None.
    """
    employee = fetch_employee(employee_id)
    if employee and employee['password'] == password:
        return employee
    return None


def login_prompt():
    """
    Prompt the user to enter their credentials.
    Returns the employee details if the login is successful.
    """
    print("=== Employee Login ===")
    employee_id = input("Enter your employee ID (username): ").strip()
    password = input("Enter your unique key (password): ").strip()

    employee = authenticate(employee_id, password)
    if employee:
        print(f"\nWelcome, {employee['name']}! Access granted.\n")
        return employee
    else:
        print("\nAuthentication failed. Please check your credentials.\n")
        return None
