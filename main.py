# main.py
from auth import login_prompt
import threat_detection


def main():
    # Step 1: Authenticate the employee.
    print("=== Employee Authentication ===")
    employee = None
    while employee is None:
        employee = login_prompt()

    # Display employee details (excluding the unique key such as password).
    print("\nEmployee details:")
    for key, value in employee.items():
        if key.lower() != "password":
            print(f"{key}: {value}")

    # Step 2: Start USB threat detection monitoring.
    print("\nStarting USB threat detection monitoring...")
    threat_detection.start_monitoring(duration=10)

    # Step 3: Analyze and display any threat events with their threat times.
    print("\nThreat events detected during monitoring:")
    threats = threat_detection.analyze_threats()
    if not threats.empty:
        expected_cols = ['device', 'insert_count', 'threat_time', 'flag_message']
        if all(col in threats.columns for col in expected_cols):
            print(threats[expected_cols])
        else:
            print("Threat alerts logged (columns may differ):")
            print(threats)
    else:
        print("No threat events detected.")


if __name__ == "__main__":
    main()
