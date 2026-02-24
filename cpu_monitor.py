#!/usr/bin/env python3
import psutil          # For accessing system sensors (CPU temperatures) and processes (CPU usage, top consumers)
import time            # For sleep() and timing
import datetime        # For current date/time formatting
import os              # For file operations (open, remove, listdir, path checks)
import csv             # For proper CSV writing (handles quoting, commas in fields)
import sys             # For sys.exit() in shutdown
import signal          # For handling signals like SIGTERM (for background service)

# ================= CONFIGURATION =================
LOG_DIR = "."          # Directory where log files will be saved.
                       # Use "." for current folder, or e.g. "/home/user/cpu_logs"

MAX_DAYS = 5           # Keep logs for this many days (files older than this are deleted)

TEMP_LOG_THRESHOLD = 60.0 # °C threshold before we log a reading.
TEMP_THRESHOLD = 70.0  # °C threshold for high temp alert; append top CPU process if exceeded

# Dictionary mapping raw sensor labels → human-readable descriptions
# Keys are lowercase-normalized to make matching case-insensitive
VERBOSE_LABELS = {
    # AMD Ryzen sensors (from k10temp or zenpower drivers)
    "tctl":                 "Tctl (Control/Hotspot Temp)",
    "tdie":                 "Tdie (Die Temp)",
    "tccd1":                "Tccd1 (Core Complex Die 1 Temp)",
    "tccd2":                "Tccd2 (Core Complex Die 2 Temp)",
    "composite":            "Composite (Overall Package Temp)",
    
    # Intel sensors (from coretemp driver)
    "package id 0":         "Package id 0 (CPU Package / Overall Temp)",
    "physical id 0":        "Physical id 0 (CPU Package Temp)",
    
    # Fallback / group names when no specific label is provided
    "coretemp":             "Core Temp Group",
    "k10temp":              "AMD K10 Temp Sensor",
    "zenpower":             "AMD Zen Power Sensor",
}

# ================= HELPER FUNCTIONS =================

def get_verbose_label(raw_label: str) -> str:
    """
    Convert a raw sensor label (e.g. "Tctl", "Package id 0") into a more
    descriptive name if it matches our known list. Otherwise return cleaned original.
    """
    # Normalize for case-insensitive lookup
    key = raw_label.lower().strip()
    return VERBOSE_LABELS.get(key, raw_label.strip())


def get_cpu_temps_detailed() -> list[tuple[str, float]]:
    """
    Read all available CPU-related temperature sensors using psutil.
    Returns a list of (verbose_label, temperature) tuples.
    Works on both AMD (k10temp/zenpower) and Intel (coretemp) systems.
    """
    temps_dict = psutil.sensors_temperatures()
    cpu_entries = []
    
    # These are the hwmon group names we consider CPU-related
    cpu_keys = ['coretemp', 'k10temp', 'zenpower', 'cpu_thermal', 'cpu-thermal', 'acpitz']
    
    for group_name, sensors in temps_dict.items():
        # Only process groups that look like CPU temperature sensors
        if any(k in group_name.lower() for k in cpu_keys):
            for sensor in sensors:
                if sensor.current is not None:  # Skip if no valid reading
                    # Use sensor's own label if it has one, otherwise fall back to group name
                    raw_label = (
                        sensor.label.strip()
                        if sensor.label and sensor.label.strip()
                        else group_name
                    )
                    verbose = get_verbose_label(raw_label)
                    cpu_entries.append((verbose, sensor.current))
    
    return cpu_entries


def get_top_cpu_process() -> str:
    """
    Find the process using the most CPU at this moment.
    Returns a string like "IntelliJ IDEA (pid:12345, cpu:45.2%)"
    or "None found" if no processes are using CPU.
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            # Get CPU percent (non-blocking, but may be 0 if just started)
            cpu = proc.info['cpu_percent']
            if cpu > 0:
                processes.append((proc.info['name'], proc.info['pid'], cpu))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass  # Skip inaccessible processes
    
    if processes:
        # Sort by CPU descending, take top one
        top = sorted(processes, key=lambda x: x[2], reverse=True)[0]
        return f"{top[0]} (pid:{top[1]}, cpu:{top[2]:.1f}%)"
    return "None found"


def cleanup_old_logs(now: datetime.datetime):
    """
    Delete log files older than MAX_DAYS.
    Runs only around midnight to minimize I/O.
    """
    cutoff_date = (now - datetime.timedelta(days=MAX_DAYS)).strftime("%Y-%m-%d")
    deleted_count = 0

    for fname in os.listdir(LOG_DIR):
        if fname.startswith("cpu_temps_") and fname.endswith(".csv"):  # Updated to .csv
            # Extract date part: cpu_temps_YYYY-MM-DD.csv → YYYY-MM-DD
            file_date = fname[10:20]
            if file_date < cutoff_date:
                full_path = os.path.join(LOG_DIR, fname)
                try:
                    os.remove(full_path)
                    print(f"Deleted old log: {fname}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {fname}: {e}")

    if deleted_count > 0:
        print(f"Cleanup complete: {deleted_count} old log file(s) removed")


# ================= GRACEFUL SHUTDOWN HANDLING =================

def shutdown_handler(signum=None, frame=None):
    """
    Called on Ctrl+C (SIGINT) or service stop (SIGTERM).
    Closes the log file cleanly and exits.
    """
    print("\nShutting down monitor...")
    if log_file:
        log_file.close()
        print("Log file closed.")
    sys.exit(0)

# Register handlers for clean shutdown
signal.signal(signal.SIGINT, shutdown_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, shutdown_handler)  # systemd stop

# ================= MAIN MONITORING LOOP =================

current_date = None      # Tracks the date of the currently open log file
log_file = None          # File handle for the active daily log (CSV writer wraps this)
csv_writer = None        # CSV writer for proper quoting/escaping
no_sensors_warned = False  # Flag to warn only once if no sensors found

print("CPU temperature monitor started. Press Ctrl+C to stop.")

while True:
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")   # e.g. "2026-02-23"

    # === Handle daily log file rotation ===
    if today_str != current_date:
        # Close previous day's file if it was open
        if log_file:
            log_file.close()
            print(f"Closed previous log file for {current_date}")

        # Open (or create) new file for today with .csv extension
        filename = os.path.join(LOG_DIR, f"cpu_temps_{today_str}.csv")
        
        # Check if file already exists (to avoid rewriting header)
        file_exists = os.path.exists(filename)
        
        log_file = open(filename, 'a', newline='', buffering=1)  # CSV mode, line buffering
        csv_writer = csv.writer(log_file, quoting=csv.QUOTE_MINIMAL)  # Quote only if needed
        
        current_date = today_str
        print(f"Started logging to: {filename}")

        # Write header row if this is a new file
        if not file_exists or os.path.getsize(filename) == 0:
            # Placeholder header - will be updated with actual sensors on first write
            # But for simplicity, we write a generic one; real sensors vary per machine
            header = [
                "Timestamp",
                "CPU Load %",
                "Max °C",
                "Sensors (Label: Value °C)...",
                "Culprit Process (if > threshold)"
            ]
            csv_writer.writerow(header)
            log_file.flush()  # Ensure header is written immediately

    # === Read temperatures ===
    entries = get_cpu_temps_detailed()

    if entries:
        no_sensors_warned = False  # Reset warning if sensors appear later
        
        # Extract just the numeric values to find the maximum
        temps_values = [temp for _, temp in entries]
        max_temp = max(temps_values)

        if max_temp > TEMP_LOG_THRESHOLD:
            # Get overall CPU load % (average over all cores, quick non-blocking sample)
            cpu_load = psutil.cpu_percent(interval=0.1)  # Short interval for near-instant read

            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

            # Format each sensor reading with its verbose label
            sensor_parts = [f"{label}: {temp:.1f}°C" for label, temp in entries]
            sensors_str = ", ".join(sensor_parts)  # Join into one field for CSV

            # Check threshold and get culprit if exceeded
            culprit = ""
            if max_temp > TEMP_THRESHOLD:
                culprit = f"Culprit: {get_top_cpu_process()}"

            # Build the row for CSV
            row = [
                timestamp,                   # Col 1: Timestamp
                f"{cpu_load:.1f}%",          # Col 2: CPU Load %
                f"{max_temp:.1f}",           # Col 3: Max °C (numeric for easy parsing)
                sensors_str,                 # Col 4: All sensors in one field (quoted if commas)
                culprit                      # Col 5: Culprit if high temp
            ]

            # Write to CSV
            csv_writer.writerow(row)
            log_file.flush()   # Ensure data is on disk immediately (good for 1/sec rate)

    else:
        # Error handling: No sensors found
        if not no_sensors_warned:
            print("Warning: No CPU temperature sensors detected. Check if lm-sensors is installed and configured.")
            no_sensors_warned = True  # Warn only once to avoid spam

    # Sleep for ~1 second between readings
    time.sleep(1)

    # === Optional daily cleanup of old log files ===
    # Runs roughly in the first 5 minutes of each new day
    if now.hour == 0 and now.minute < 5:
        cleanup_old_logs(now)
