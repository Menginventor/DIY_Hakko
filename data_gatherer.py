import serial
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# === CONFIG ===
SERIAL_PORT = 'COM7'   # Or 'COMx' on Windows
BAUD_RATE = 115200
PLOT_DURATION_SEC = 60         # How much time to show in real-time plot

# === DATA STORAGE ===
timestamps = []
resistances = []
controls = []
cycles = []
adcs = []
start_time = None

# === SETUP SERIAL ===
print("Opening serial...")
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

time.sleep(2)
ser.write(b"start\n")

# === PLOTTING SETUP ===
plt.style.use("seaborn-whitegrid")
fig, ax1 = plt.subplots()
line_rtd, = ax1.plot([], [], label="RTD Resistance (Ω)", color='tab:blue')
ax1.set_ylabel("Resistance (Ω)", color='tab:blue')
ax1.set_xlabel("Time (s)")
ax1.set_ylim(0, 300)

ax2 = ax1.twinx()
line_u, = ax2.plot([], [], label="Control (u)", color='tab:red', linestyle='--')
ax2.set_ylabel("Control Signal", color='tab:red')
ax2.set_ylim(-0.1, 1.1)

ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# === Update function for FuncAnimation ===
def update_plot(frame):
    global start_time

    # Try to read multiple lines per frame for better responsiveness
    for _ in range(10):
        line = ser.readline().decode().strip()
        if not line or not line.startswith("round="):
            continue
        try:
            parts = line.split(", ")
            round_num = int(parts[0].split("=")[1])
            adc = int(parts[1].split("=")[1])
            rtd = float(parts[2].split("=")[1])
            u = int(parts[3].split("=")[1])
            t_off = int(parts[4].split("=")[1])
        except Exception as e:
            print("Parse error:", e)
            continue

        if start_time is None:
            start_time = time.time()
        t = time.time() - start_time

        timestamps.append(t)
        resistances.append(rtd)
        controls.append(u)
        cycles.append(round_num)
        adcs.append(adc)

        print(f"t={t:.2f}s | round={round_num} | adc={adc} | R={rtd:.2f}Ω | u={u} | t_off={t_off}s")

    if timestamps:
        t0 = timestamps[-1] - PLOT_DURATION_SEC if timestamps[-1] > PLOT_DURATION_SEC else 0
        indices = [i for i, t in enumerate(timestamps) if t >= t0]
        t_disp = [timestamps[i] for i in indices]
        r_disp = [resistances[i] for i in indices]
        u_disp = [controls[i] for i in indices]

        line_rtd.set_data(t_disp, r_disp)
        line_u.set_data(t_disp, u_disp)
        ax1.set_xlim(t0, t_disp[-1])

    return line_rtd, line_u

ani = FuncAnimation(fig, update_plot, interval=100)

try:
    plt.show()  # This will keep updating until the window is closed
except KeyboardInterrupt:
    print("Stopped by user.")

# === Save data after closing the plot ===
ser.close()
print("Saving data...")

data_array = np.array([timestamps, adcs, resistances, controls, cycles]).T
np.save("rtd_step_response.npy", data_array)

df = pd.DataFrame({
    "time_s": timestamps,
    "adc": adcs,
    "resistance_ohm": resistances,
    "control_u": controls,
    "cycle": cycles
})
df.to_csv("rtd_step_response.csv", index=False)

print("Saved to rtd_step_response.npy and .csv")
