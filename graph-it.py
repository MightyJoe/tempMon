#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Optional: force interactive backend if you want pop-up
# import matplotlib
# matplotlib.use('Qt5Agg')  # uncomment if you installed pyqt5 and want window

today = datetime.datetime.now().strftime("%Y-%m-%d")
filename = f"cpu_temps_{today}.csv"  # adjust if extension/path different

try:
    df = pd.read_csv(filename)
except FileNotFoundError:
    print(f"Error: {filename} not found. Run the monitor first!")
    exit(1)

df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Max °C'] = df['Max °C'].astype(float)
df['CPU Load %'] = df['CPU Load %'].str.rstrip('%').astype(float)

fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.plot(df['Timestamp'], df['Max °C'], color='red', label='Max Temp °C')
ax1.set_xlabel('Time')
ax1.set_ylabel('Temperature °C', color='red')
ax1.tick_params(axis='y', labelcolor='red')
ax1.axhline(y=70, color='orange', linestyle='--', label='Threshold 70°C')

ax2 = ax1.twinx()
ax2.plot(df['Timestamp'], df['CPU Load %'], color='blue', label='CPU Load %')
ax2.set_ylabel('CPU Load %', color='blue')
ax2.tick_params(axis='y', labelcolor='blue')

high_temps = df[df['Max °C'] > 70]
ax1.scatter(high_temps['Timestamp'], high_temps['Max °C'], color='black', s=20, label='High Temp (>70°C)')

fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)

plt.title(f'CPU Temps and Load for {today}')
plt.tight_layout()

# Save always, show optionally
plt.savefig('cpu_temp_graph.png', dpi=150, bbox_inches='tight')
print("Graph saved as cpu_temp_graph.png")

# plt.show()  # Uncomment only if you set an interactive backend above
