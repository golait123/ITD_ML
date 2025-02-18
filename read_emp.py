import sqlite3
import pandas as pd

# Define file paths
csv_file = r"C:\Users\kapil\PycharmProjects\ITD_ML\employee_dataset.csv"
db_path = r"C:\Users\kapil\PycharmProjects\ITD_ML\employee.db"

# Read data from CSV file
df = pd.read_csv(csv_file)
print("CSV Data Preview:")
print(df.head())
print("Total rows to insert:", len(df))

# Connect to (or create) the SQLite database using the absolute path
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the employees table with the appropriate schema
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        employee_id TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

# Clear existing data to avoid duplicates (if this is desired)
cursor.execute("DELETE FROM employees")
print("Existing data deleted.")

# Insert each record from the DataFrame into the database
for _, row in df.iterrows():
    try:
        cursor.execute(
            "INSERT INTO employees (employee_id, password, name, role) VALUES (?, ?, ?, ?)",
            (row["Employee ID"], row["Password"], row["Employee Name"], row["Role"])
        )
        print(f"Inserted Employee ID: {row['Employee ID']}")
    except sqlite3.IntegrityError as e:
        print(f"Skipping duplicate Employee ID: {row['Employee ID']}. Error: {e}")

# Commit changes and print the number of rows inserted
conn.commit()
cursor.execute("SELECT COUNT(*) FROM employees")
count = cursor.fetchone()[0]
print(f"Number of rows inserted: {count}")

# Close the connection
conn.close()

print("Data inserted into employee.db successfully!")
