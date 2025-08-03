import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Parameters
omega_n = 1.0
zeta_values = np.arange(0, 3, 0.001)

# Precompute full pole trajectory
real_underdamped = -zeta_values[zeta_values < 1] * omega_n
imag_underdamped = omega_n * np.sqrt(1 - zeta_values[zeta_values < 1]**2)

real_overdamped_1 = -zeta_values[zeta_values > 1] * omega_n + omega_n * np.sqrt(zeta_values[zeta_values > 1]**2 - 1)
real_overdamped_2 = -zeta_values[zeta_values > 1] * omega_n - omega_n * np.sqrt(zeta_values[zeta_values > 1]**2 - 1)

# Add critically damped point to both trajectories to make them meet
real_underdamped = np.append(real_underdamped, -omega_n)
imag_underdamped = np.append(imag_underdamped, 0)
real_overdamped_1 = np.insert(real_overdamped_1, 0, -omega_n)
real_overdamped_2 = np.insert(real_overdamped_2, 0, -omega_n)

# Regenerate zeta_values for animation steps
zeta_values = np.linspace(0, 3, 200)

# Set up the figure
fig, ax = plt.subplots(figsize=(8, 6))
ax.axhline(0, color='gray', lw=0.5)
ax.axvline(0, color='gray', lw=0.5)
ax.set_xlim([-3, 1])
ax.set_ylim([-1.5, 1.5])
ax.set_xlabel('Real Axis')
ax.set_ylabel('Imaginary Axis')
ax.set_title('Pole Geometry of a Second-Order System with Unit Natural Frequency')

# Plot static trajectories
ax.plot(real_underdamped,  imag_underdamped,   'b--', lw=1, label='Underdamped Trajectory')
ax.plot(real_underdamped, -imag_underdamped,   'b--', lw=1)
ax.plot(real_overdamped_1, np.zeros_like(real_overdamped_1), 'r--', lw=1, label='Overdamped Trajectory')
ax.plot(real_overdamped_2, np.zeros_like(real_overdamped_2), 'r--', lw=1)

# Animated moving poles
point_real, = ax.plot([], [], 'ro', label='Real Poles')
point_imag, = ax.plot([], [], 'bo', label='Complex Conjugate Poles')
text = ax.text(0.05, 0.6, '', transform=ax.transAxes)
ax.legend()

# Initialization
def init():
    point_real.set_data([], [])
    point_imag.set_data([], [])
    text.set_text('')
    return point_real, point_imag, text

# Animation function
def animate(i):
    zeta = zeta_values[i]
    if zeta < 1:
        real = -zeta * omega_n
        imag = omega_n * np.sqrt(1 - zeta**2)
        point_real.set_data([], [])
        point_imag.set_data([real, real], [imag, -imag])
    elif np.isclose(zeta, 1, atol=1e-2):
        real = -omega_n
        point_real.set_data([real, real], [0, 0])
        point_imag.set_data([], [])
    else:
        real1 = -zeta * omega_n + omega_n * np.sqrt(zeta**2 - 1)
        real2 = -zeta * omega_n - omega_n * np.sqrt(zeta**2 - 1)
        point_real.set_data([real1, real2], [0, 0])
        point_imag.set_data([], [])
    text.set_text(f'ζ = {zeta:.2f}')
    return point_real, point_imag, text

# Create and save animation
ani = animation.FuncAnimation(fig, animate, frames=len(zeta_values),
                              init_func=init, blit=True, interval=50)
ani.save("pole_geometry_second_order_unit_omega.gif", writer="pillow", fps=30)

plt.show()
