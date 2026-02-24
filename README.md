# CPU Temperature Monitor for Ubuntu/Mint

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Simple script that logs CPU temperatures every second to daily CSV files, detects high temps (>70°C) and logs the top CPU-consuming process.

## Requirements

Python 3.8+

## Installation

This is still hazy on how to install. For now, you may need to fiddle with dependencies,
but the main thing is that psutils is required for the main script. And we are using venv.
venv stands for virtual evnironment. That way, the reqs are not installed system-wide.
You can try this at your own peril:
```bash
# Recommended: virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

## Installation of Service (in case you want it to always run)

Change the content of the .service file to point at real folder paths to files that actually exist.

Create a service file: sudo nano /etc/systemd/system/cpu-monitor.service with the content from the .service file

Reload systemd: sudo systemctl daemon-reload

Start: sudo systemctl start cpu-monitor

Enable on boot: sudo systemctl enable cpu-monitor

Check logs: journalctl -u cpu-monitor -f

Stop: sudo systemctl stop cpu-monitor
