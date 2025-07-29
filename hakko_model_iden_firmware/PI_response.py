import serial
import threading
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

# --- CONFIGURATION ---
SERIAL_PORT = 'COM7'  # Change this!
BAUDRATE = 115200
DURATION_SEC = 60
REFRESH_MS = 100

# --- Auto-named files ---
timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_FILE = f"rtd_log_{timestamp_str}.csv"
NPY_FILE = f"rtd_log_{timestamp_str}.npy"

# --- Globals ---
data = []
running = True
start_time = time.time()

# --- Serial Setup ---
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)
ser.write(b'start\n')  # Auto-start
print(f"[INFO] Logging started for {DURATION_SEC} seconds...")

# --- Threaded Data Collector ---
def read_serial():
    global running, data
    while running:
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line or ',' not in line:
                continue
            target, rtd, pwm = map(float, line.split(','))
            timestamp = time.time() - start_time
            data.append([timestamp, target, rtd, pwm])
        except Exception:
            continue

# --- Plot Setup ---
plt.style.use("seaborn-v0_8-darkgrid")
fig, ax = plt.subplots(figsize=(10, 6))
line1, = ax.plot([], [], label='Target RTD', linestyle='--')
line2, = ax.plot([], [], label='Measured RTD')
line3, = ax.plot([], [], label='PWM (%)')
ax.set_xlim(0, DURATION_SEC)
ax.set_ylim(0, 200)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Value")
ax.set_title("Live RTD Control")
ax.legend()

def update_plot(frame):
    if not data:
        return

    latest_time = time.time() - start_time
    times = [row[0] for row in data]
    targets = [row[1] for row in data]
    readings = [row[2] for row in data]
    pwms = [row[3] for row in data]

    line1.set_data(times, targets)
    line2.set_data(times, readings)
    line3.set_data(times, pwms)

    ax.set_xlim(max(0, latest_time - 10), latest_time + 1)
    ax.set_ylim(0, max(200, max(readings + targets) + 20))

# --- Start Serial Thread ---
thread = threading.Thread(target=read_serial)
thread.start()

# --- Start Plotting ---
ani = FuncAnimation(fig, update_plot, interval=REFRESH_MS)
plt.tight_layout()
plt.show()

# --- Finish Logging ---
running = False
thread.join()
ser.close()

# --- Save All Formats ---
df = pd.DataFrame(data, columns=['Time (s)', 'Target RTD', 'Measured RTD', 'PWM (%)'])
df.to_csv(CSV_FILE, index=False)
np.save(NPY_FILE, df.to_numpy())


print(f"[INFO] Saved to:\n - {CSV_FILE}\n - {NPY_FILE}\n")
