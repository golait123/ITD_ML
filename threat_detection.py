# threat_detection.py
import os
import time
import threading
import subprocess
import pandas as pd
import pickle

# File paths and configuration
EVENT_LOG = "event_data.csv"
SECURITY_ALERT_LOG = "security_alerts.csv"
MODEL_FILE = "threat_model.pkl"

# For flagging every 2nd USB insertion event (flagging by our logging mechanism)
INSERT_ALERT_INTERVAL = 2
usb_insert_counts = {}


def flag_insert_event(device, count):
    threat_time = time.strftime("%Y-%m-%d %H:%M:%S")
    flag_message = f"FLAG: Device [{device}] inserted {count} times at {threat_time}."
    print(flag_message)
    alert_df = pd.DataFrame(
        [[device, count, threat_time, flag_message]],
        columns=["device", "insert_count", "threat_time", "flag_message"]
    )
    if os.path.exists(SECURITY_ALERT_LOG):
        alert_df.to_csv(SECURITY_ALERT_LOG, mode='a', header=False, index=False)
    else:
        alert_df.to_csv(SECURITY_ALERT_LOG, mode='w', index=False)


def update_insert_count(device):
    """
    Increment the insertion count for a device. If the count is a multiple of
    INSERT_ALERT_INTERVAL, flag the event.
    """
    global usb_insert_counts
    usb_insert_counts[device] = usb_insert_counts.get(device, 0) + 1
    count = usb_insert_counts[device]
    print(f"Insert count for device [{device}]: {count}")
    if count % INSERT_ALERT_INTERVAL == 0:
        flag_insert_event(device, count)


def log_usb_event(device, event_type, extra_info=""):
    """
    Log a USB event (insertion or removal) with a timestamp and extra info.
    For an insertion event, update the insertion count.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # Each row will have exactly 4 fields.
    row = [[device, event_type, timestamp, extra_info]]
    df = pd.DataFrame(row, columns=["device", "event_type", "timestamp", "extra_info"])
    if os.path.exists(EVENT_LOG):
        df.to_csv(EVENT_LOG, mode='a', header=False, index=False)
    else:
        df.to_csv(EVENT_LOG, mode='w', index=False)
    print(f"Logged USB {event_type} event for device [{device}] at {timestamp}. {extra_info}")

    if event_type == "inserted":
        update_insert_count(device)


# ----------------------------
# Platform-Specific USB Monitoring
# ----------------------------
if os.name != 'nt':
    # Linux implementation using pyudev.
    try:
        import pyudev
    except ImportError:
        print("pyudev module not found. Please install using: pip install pyudev")
        exit(1)


    def monitor_usb():
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb')
        print("Monitoring USB events on Linux using pyudev.")
        try:
            for device in iter(monitor.poll, None):
                if device.action == 'add':
                    event_type = "inserted"
                    extra_info = f"Device node: {getattr(device, 'device_node', 'N/A')}"
                    device_id = device.get('ID_SERIAL') or str(device)
                    log_usb_event(device_id, event_type, extra_info)
                elif device.action == 'remove':
                    event_type = "removed"
                    extra_info = f"Device node: {getattr(device, 'device_node', 'N/A')}"
                    device_id = device.get('ID_SERIAL') or str(device)
                    log_usb_event(device_id, event_type, extra_info)
        except KeyboardInterrupt:
            print("USB monitoring interrupted.")

else:
    # Windows implementation using WMI.
    try:
        import wmi
        import pythoncom
    except ImportError:
        print("Required modules not found. Please install using: pip install wmi pywin32")
        exit(1)


    def monitor_usb():
        pythoncom.CoInitialize()  # Initialize COM for this thread.
        c = wmi.WMI()
        print("Monitoring USB events on Windows using WMI.")
        watcher = c.Win32_VolumeChangeEvent.watch_for()
        try:
            while True:
                try:
                    event = watcher()
                    if event.EventType == 2:
                        event_type = "inserted"
                    elif event.EventType == 3:
                        event_type = "removed"
                    else:
                        event_type = f"unknown (EventType: {event.EventType})"
                    extra_info = f"Drive: {getattr(event, 'DriveName', 'N/A')}"
                    device_id = getattr(event, 'DriveName', str(event))
                    log_usb_event(device_id, event_type, extra_info)
                except Exception as e:
                    print("Error processing USB event:", e)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("USB monitoring interrupted.")


def start_monitoring(duration=10):
    """
    Start USB event monitoring in a daemon thread for a specified duration (in seconds).
    """
    monitor_thread = threading.Thread(target=monitor_usb, daemon=True)
    monitor_thread.start()
    print(f"Monitoring USB events for {duration} seconds...")
    time.sleep(duration)
    print("Finished monitoring USB events.")


# ----------------------------
# Machine Learning Integration
# ----------------------------
def load_model():
    """Load the trained threat detection model from disk."""
    try:
        with open(MODEL_FILE, 'rb') as f:
            vectorizer, model = pickle.load(f)
        print("Threat detection model loaded successfully.")
        return vectorizer, model
    except FileNotFoundError:
        print("Error: Model file not found. Run train_model.py first.")
        return None, None


def analyze_threats():
    """
    Use the machine learning model to analyze the logged USB events.
    For every event predicted as a threat, add the following columns:
      - insert_count (set to 1 for this event)
      - threat_time (taken from the event's timestamp)
      - flag_message (a message indicating an ML-predicted threat)
    Returns a DataFrame containing only the threat events.
    """
    vectorizer, model = load_model()
    if model is None:
        return pd.DataFrame()
    try:
        # Use on_bad_lines='skip' to bypass rows with an unexpected number of fields.
        df = pd.read_csv(EVENT_LOG, on_bad_lines='skip')
    except FileNotFoundError:
        print("Error: event_data.csv not found.")
        return pd.DataFrame()

    if 'device' not in df.columns:
        print("Error: 'device' column not found in the event log.")
        return pd.DataFrame()

    # Transform the 'device' field and make predictions.
    X = vectorizer.transform(df['device'].astype(str))
    df['prediction'] = model.predict(X)
    df['predicted_threat'] = df['prediction'].apply(lambda x: "Threat" if x == 1 else "Safe")

    # Filter for events predicted as a threat.
    df_threats = df[df['predicted_threat'] == "Threat"].copy()
    # Add columns to match the expected format.
    df_threats['insert_count'] = 1  # Set to 1 for each threat event.
    df_threats['threat_time'] = df_threats['timestamp']
    df_threats['flag_message'] = "ML predicted threat based on USB insertion"

    return df_threats


# ----------------------------
# Retrieve User Activity Details
# ----------------------------
def get_user_activity_details(employee):
    """
    Return the USB activity log appended with the logged employee's details (except the unique key).
    """
    try:
        df = pd.read_csv(EVENT_LOG, on_bad_lines='skip')
    except FileNotFoundError:
        print("No activity logged yet.")
        return pd.DataFrame()
    # Exclude the unique key (e.g. password) from employee details.
    user_details = {k: v for k, v in employee.items() if k.lower() != 'password'}
    df['employee'] = str(user_details)
    return df


# Allow standalone testing.
if __name__ == "__main__":
    start_monitoring(duration=10)
    threats = analyze_threats()
    if not threats.empty:
        print("Machine Learning Threat Analysis Results:")
        print(threats)
    else:
        print("No threats detected by ML analysis.")
