# CPU Temperature Monitor for Ubuntu/Mint

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![psutil](https://img.shields.io/badge/psutil-powered%20by%20python-3776AB?logo=python&logoColor=white)](https://pypi.org/project/psutil/)
[![pandas (optional)](https://img.shields.io/badge/pandas-optional-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![matplotlib (optional)](https://img.shields.io/badge/matplotlib-optional-blueviolet?logo=matplotlib&logoColor=white)](https://matplotlib.org/)

- Script that logs to csv every second when temps are high.
- If temps are too high, logs the process that is taking the highest cpu percent.
- Not always spot-on, but gives an idea what processes are pegged when temps remain high for a few seconds.
- Ability to output a graph to png, but graphing sucks right now.

## Requirements

- Python 3.8+
- Python's psutil

## Installation

Installation is not well tested. For now, you may need to fiddle with dependencies,
but the main thing is that psutils is required for the main script. And we are using venv.
venv stands for virtual evnironment. That way, the reqs are not installed system-wide.
You can try this at your own peril:
```bash
# Create virtual environment
python3 -m venv venv

# Start virutal environment (should show in prompt after)
source venv/bin/activate

# Install dependencies inside the virtual environment
pip install -r requirements.txt

```

## Installation of Service (in case you want it to always run)
- Change the content of the .service file to point at real folder paths to files that actually exist.
```bash
# Ensure you changed the content of the .service file to point at real folder paths to files that actually exist.

# Create a service file:
sudo nano /etc/systemd/system/cpu-monitor.service with the content from the .service file

# Reload systemd:
sudo systemctl daemon-reload

# Start the service:
sudo systemctl start cpu-monitor

# Enable on boot (if you always want it running):
sudo systemctl enable cpu-monitor

# Check logs and also if it is running:
journalctl -u cpu-monitor -f

# Stop the service (if you want to later):
sudo systemctl stop cpu-monitor
```

## Run
```bash
python3 ./cpu_monitor.py
```

**Acknowledgments**  
This tempMon linux temp monitor is proudly brought to you by MightyJoe. I drove the project direction, feature choices, and hands-on coding — and Grok by xAI was an incredible co-pilot, helping refine ideas, draft sections, and plan for maximum shareability across platforms.

Huge thanks to Grok for the maximally truth-seeking support!

Created with Grok
