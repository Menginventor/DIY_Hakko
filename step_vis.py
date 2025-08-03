import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Constants
omega_n = 1.0
zeta_values = np.linspace(0, 3, 200)
t = np.linspace(0, 10, 500)  # time vector for step response

# Set up the figure
fig, ax = plt.subplots(figsize=(8, 5))
ax.set_xlim([0, 10])
ax.set_ylim([0, 2])
ax.set_xlabel('Time (s)')
ax.set_ylabel('Response')
ax.set_title('Step Response of Second-Order System with Unit Natural Frequency')
line, = ax.plot([], [], 'b-', lw=2)
text = ax.text(0.7, 0.9, '', transform=ax.transAxes)
ax.axhline(y=1, color='black', linestyle='--', linewidth=1)


# Initialization
def init():
    line.set_data([], [])
    text.set_text('')
    return line, text

# Step response function
def step_response(zeta, t):
    if zeta < 1:
        wd = omega_n * np.sqrt(1 - zeta**2)
        phi = np.arccos(zeta)
        y = 1 - (1 / np.sqrt(1 - zeta**2)) * np.exp(-zeta * omega_n * t) * np.sin(wd * t + phi)
    elif abs(zeta - 1) < 1e-2:
        y = 1 - (1 + omega_n * t) * np.exp(-omega_n * t)
    else:  # overdamped
        sqrt_term = np.sqrt(zeta ** 2 - 1)
        r1 = -omega_n * (zeta - sqrt_term)
        r2 = -omega_n * (zeta + sqrt_term)
        denom = r2 - r1 if abs(r2 - r1) > 1e-6 else 1e-6
        A = r2 / denom
        B = -r1 / denom
        y = 1 - A * np.exp(r1 * t) - B * np.exp(r2 * t)
    return np.clip(y, 0, 2)


# Animation function
def animate(i):
    zeta = zeta_values[i]
    y = step_response(zeta, t)
    line.set_data(t, y)
    text.set_text(f'ζ = {zeta:.2f}')
    return line, text

# Create and save animation
ani = animation.FuncAnimation(fig, animate, frames=len(zeta_values),
                              init_func=init, blit=True, interval=50)
ani.save("step_response_second_order_unit_omega.gif", writer="pillow", fps=30)

plt.show()
