# threat_events.py
import pandas as pd
import os

SECURITY_ALERT_LOG = "security_alerts.csv"


def display_threat_events():
    if os.path.exists(SECURITY_ALERT_LOG):
        try:
            df = pd.read_csv(SECURITY_ALERT_LOG)
            print("Threat Events Logged:")
            print(df)
        except Exception as e:
            print("Error reading threat event file:", e)
    else:
        print("No threat event file found. No threat events have been logged yet.")


if __name__ == "__main__":
    display_threat_events()
