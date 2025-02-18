import sqlite3
import pandas as pd

db_path = r"C:\Users\kapil\PycharmProjects\ITD_ML\employee.db"

conn = sqlite3.connect(db_path)
query = '''
SELECT 
    employee_id AS "Employee ID",
    password AS "Password",
    name AS "Employee Name",
    role AS "Role"
FROM employees
'''
df = pd.read_sql_query(query, conn)
conn.close()

print("Employee Data from Database:")
print(df.to_string(index=False))
