from auth import login_prompt
from threat_Detection import (load_model, generate_sample_events, analyze_events)


def main():
    # Step 1: Authenticate the user.
    employee = None
    while employee is None:
        employee = login_prompt()

    # Step 2: Load the ML model for threat detection.
    model = load_model()
    if model is None:
        print("Failed to load threat detection model. Exiting.")
        return

    # Step 3: Simulate event logging and insider threat monitoring.
    print("Starting Insider Threat Monitoring...\n")
    events = generate_sample_events()

    print("\nAnalyzing events for suspicious activity...\n")
    analyze_events(events, employee)

    print("Threat detection analysis complete.")


if __name__ == "__main__":
    main()
