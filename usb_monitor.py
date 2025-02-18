import os
import time
import pandas as pd

# Log file paths
EVENT_LOG = "event_data.csv"
SECURITY_ALERT_LOG = "security_alerts.csv"

# Configuration: generate a flag for every 2nd insert event.
INSERT_ALERT_INTERVAL = 2

# Dictionary to track insert event counts for each device.
usb_insert_counts = {}

def flag_insert_event(device, count):
    """
    Generate a flag for the device when its insert count reaches a multiple of INSERT_ALERT_INTERVAL.
    This prints a flag message and logs it to SECURITY_ALERT_LOG.
    """
    flag_message = f"FLAG: Device [{device}] has been inserted {count} times."
    print(flag_message)
    alert_df = pd.DataFrame(
        [[device, count, time.strftime("%Y-%m-%d %H:%M:%S"), flag_message]],
        columns=["device", "insert_count", "timestamp", "flag_message"]
    )
    if os.path.exists(SECURITY_ALERT_LOG):
        alert_df.to_csv(SECURITY_ALERT_LOG, mode='a', header=False, index=False)
    else:
        alert_df.to_csv(SECURITY_ALERT_LOG, mode='w', index=False)

def update_insert_count(device):
    """
    Update the insert event count for the given device.
    If the count is a multiple of INSERT_ALERT_INTERVAL, a flag is generated.
    """
    usb_insert_counts[device] = usb_insert_counts.get(device, 0) + 1
    count = usb_insert_counts[device]
    print(f"Insert count for device [{device}]: {count}")
    if count % INSERT_ALERT_INTERVAL == 0:
        flag_insert_event(device, count)

def log_usb_event(device, event_type, extra_info=""):
    """
    Log a USB event (insertion or removal) with a timestamp and extra information.
    For an 'inserted' event, update the insert count.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame(
        [[device, event_type, timestamp, extra_info]],
        columns=["device", "event_type", "timestamp", "extra_info"]
    )
    if os.path.exists(EVENT_LOG):
        df.to_csv(EVENT_LOG, mode='a', header=False, index=False)
    else:
        df.to_csv(EVENT_LOG, mode='w', index=False)
    print(f"Logged USB {event_type} event for device [{device}] at {timestamp} {extra_info}")

    # For insert events, update the insert count and possibly flag.
    if event_type == "inserted":
        update_insert_count(device)

# -------------------------------
# Platform-Specific Implementations
# -------------------------------

if os.name != 'nt':
    # Linux Implementation Using pyudev
    try:
        import pyudev
    except ImportError:
        print("pyudev module not found. Please install using: pip install pyudev")
        exit(1)

    def monitor_usb():
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        # Filter events for the USB subsystem.
        monitor.filter_by(subsystem='usb')
        print("Monitoring USB events on Linux using pyudev. Press Ctrl+C to stop.")
        try:
            for device in iter(monitor.poll, None):
                # Process 'add' events as insertions.
                if device.action == 'add':
                    event_type = "inserted"
                    extra_info = f"Device node: {getattr(device, 'device_node', 'N/A')}"
                    # Attempt to use a unique identifier (e.g., ID_SERIAL) if available.
                    device_id = device.get('ID_SERIAL') or str(device)
                    log_usb_event(device_id, event_type, extra_info)
                elif device.action == 'remove':
                    event_type = "removed"
                    extra_info = f"Device node: {getattr(device, 'device_node', 'N/A')}"
                    device_id = device.get('ID_SERIAL') or str(device)
                    log_usb_event(device_id, event_type, extra_info)
        except KeyboardInterrupt:
            print("Monitoring stopped.")

    if __name__ == "__main__":
        monitor_usb()

else:
    # Windows Implementation Using WMI
    try:
        import wmi
        import pythoncom
    except ImportError:
        print("Required modules not found. Please install using: pip install wmi pywin32")
        exit(1)

    def monitor_usb():
        pythoncom.CoInitialize()  # Initialize COM library for the current thread.
        c = wmi.WMI()
        print("Monitoring USB events on Windows using WMI. Press Ctrl+C to stop.")
        # Watch for volume change events (USB insertion/removal).
        watcher = c.Win32_VolumeChangeEvent.watch_for()
        try:
            while True:
                try:
                    event = watcher()
                    # On Windows, EventType 2 is typically insertion, and 3 is removal.
                    if event.EventType == 2:
                        event_type = "inserted"
                    elif event.EventType == 3:
                        event_type = "removed"
                    else:
                        event_type = f"unknown (EventType: {event.EventType})"
                    extra_info = f"Drive: {getattr(event, 'DriveName', 'N/A')}"
                    # Use the drive name as the device identifier, or fallback to string representation.
                    device_id = getattr(event, 'DriveName', str(event))
                    log_usb_event(device_id, event_type, extra_info)
                except Exception as inner_error:
                    print("Error while processing event:", inner_error)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Monitoring stopped.")

    if __name__ == "__main__":
        monitor_usb()
