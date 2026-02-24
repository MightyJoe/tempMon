# CPU Temperature Monitor

Simple script that logs CPU temperatures every second to daily CSV files, detects high temps (>70°C) and logs the top CPU-consuming process.

## Requirements

Python 3.8+

## Installation

```bash
# Recommended: virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

## Isntallation of Service (in case you want it to always run)

Change the content of the .service file to point at real folder paths to files that actually exist.

Create a service file: sudo nano /etc/systemd/system/cpu-monitor.service with the content from the .service file

Reload systemd: sudo systemctl daemon-reload

Start: sudo systemctl start cpu-monitor

Enable on boot: sudo systemctl enable cpu-monitor

Check logs: journalctl -u cpu-monitor -f

Stop: sudo systemctl stop cpu-monitor
