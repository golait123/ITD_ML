import sqlite3
import pandas as pd

# -----------------------------
# Configuration: File Paths
# -----------------------------
csv_file = r"C:\Users\kapil\PycharmProjects\ITD_ML\employee_dataset.csv"
db_path = r"C:\Users\kapil\PycharmProjects\ITD_ML\employee.db"

# -----------------------------
# Step 1: Read Data from CSV
# -----------------------------
df = pd.read_csv(csv_file)

# Convert all relevant columns to string to avoid datatype mismatches
df["Employee ID"] = df["Employee ID"].astype(str)
df["Password"] = df["Password"].astype(str)
df["Employee Name"] = df["Employee Name"].astype(str)
df["Role"] = df["Role"].astype(str)

print("CSV Data Preview:")
print(df.head())
print("Total rows read from CSV:", len(df))

# -----------------------------
# Step 2: Connect to SQLite and Update the Database
# -----------------------------
# Connect to (or create) the SQLite database using an absolute path
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the employees table if it exists (to start fresh with correct schema)
cursor.execute("DROP TABLE IF EXISTS employees")

# Create the employees table with the appropriate schema.
cursor.execute('''
    CREATE TABLE employees (
        employee_id TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')
print("Employees table created successfully.")

# Insert each record from the CSV into the database.
for _, row in df.iterrows():
    try:
        cursor.execute(
            "INSERT INTO employees (employee_id, password, name, role) VALUES (?, ?, ?, ?)",
            (row["Employee ID"], row["Password"], row["Employee Name"], row["Role"])
        )
        print(f"Inserted Employee ID: {row['Employee ID']}")
    except sqlite3.IntegrityError as e:
        # Although we dropped the table, this block helps catch unexpected duplicates
        print(f"Skipping duplicate or invalid Employee ID: {row['Employee ID']}. Error: {e}")

# Commit changes and check number of rows inserted.
conn.commit()
cursor.execute("SELECT COUNT(*) FROM employees")
count = cursor.fetchone()[0]
print(f"Number of rows inserted: {count}")

# -----------------------------
# Step 3: Fetch Data from the Database
# -----------------------------
query = '''
SELECT 
    employee_id AS "Employee ID",
    password AS "Password",
    name AS "Employee Name",
    role AS "Role"
FROM employees
'''
df_db = pd.read_sql_query(query, conn)

# Close the connection
conn.close()

# -----------------------------
# Step 4: Display the Fetched Data
# -----------------------------
print("\nEmployee Data from Database:")
print(df_db.to_string(index=False))
