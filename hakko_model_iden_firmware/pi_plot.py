import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
CSV_FILE = 'rtd_log_20250724_174622.csv'  # Change to your actual file name

# --- Load Data ---
df = pd.read_csv(CSV_FILE)

# --- Plot ---
plt.figure(figsize=(10, 6))
plt.plot(df['Time (s)'], df['Target RTD'], label='Target RTD', linestyle='--')
plt.plot(df['Time (s)'], df['Measured RTD'], label='Measured RTD')
plt.plot(df['Time (s)'], df['PWM (%)'], label='PWM (%)', alpha=0.7)

plt.xlabel('Time (s)')
plt.ylabel('Value')
plt.title('RTD Closed-Loop Control (from CSV)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
