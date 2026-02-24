# CPU Temperature Monitor for Ubuntu/Mint

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![psutil](https://img.shields.io/badge/psutil-powered%20by%20python-3776AB?logo=python&logoColor=white)](https://pypi.org/project/psutil/)
[![pandas (optional)](https://img.shields.io/badge/pandas-optional-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![matplotlib (optional)](https://img.shields.io/badge/matplotlib-optional-blueviolet?logo=matplotlib&logoColor=white)](https://matplotlib.org/)

Simple script that logs CPU temperatures every second to daily CSV files, detects high temps (>70°C) and logs the top CPU-consuming process.

## Requirements

Python 3.8+

## Installation

This is still hazy on how to install. For now, you may need to fiddle with dependencies,
but the main thing is that psutils is required for the main script. And we are using venv.
venv stands for virtual evnironment. That way, the reqs are not installed system-wide.
You can try this at your own peril:
```bash
# Recommended: create virtual environment
python3 -m venv venv
# start virutal environment (should show in prompt after)
source venv/bin/activate
# install these dependencies inside the virtual environment
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
