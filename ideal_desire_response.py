import numpy as np
import matplotlib.pyplot as plt

# Parameters
T_s = 30
omega_n = 4 / T_s

# Time vector
t = np.linspace(0, 60, 1000)

# Critically damped step response
y = 1 - (1 + omega_n * t) * np.exp(-omega_n * t)

# Plot
plt.figure(figsize=(8, 5))
plt.plot(t, y, label=f'Critically Damped Step\n$T_s$={T_s}, $\\omega_n$={omega_n:.4f}')
plt.axhline(1.0, color='gray', linestyle='--', linewidth=0.7)
plt.axhline(0.98, color='red', linestyle=':', linewidth=0.7, label='2% band')
plt.axhline(1.02, color='red', linestyle=':', linewidth=0.7)
plt.xlabel('Time (s)')
plt.ylabel('Response')
plt.title('Critically Damped Step Response')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
