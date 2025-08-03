import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Constants
omega_n = 1.0
zeta_values = np.linspace(0, 3, 200)
t = np.linspace(0, 20, 500)

# Precompute pole trajectories
zeta_traj = np.arange(0, 3, 0.001)
real_underdamped = -zeta_traj[zeta_traj < 1] * omega_n
imag_underdamped = omega_n * np.sqrt(1 - zeta_traj[zeta_traj < 1]**2)
real_overdamped_1 = -zeta_traj[zeta_traj > 1] * omega_n + omega_n * np.sqrt(zeta_traj[zeta_traj > 1]**2 - 1)
real_overdamped_2 = -zeta_traj[zeta_traj > 1] * omega_n - omega_n * np.sqrt(zeta_traj[zeta_traj > 1]**2 - 1)

# Add critically damped point
real_underdamped = np.append(real_underdamped, -omega_n)
imag_underdamped = np.append(imag_underdamped, 0)
real_overdamped_1 = np.insert(real_overdamped_1, 0, -omega_n)
real_overdamped_2 = np.insert(real_overdamped_2, 0, -omega_n)

# Step response function
def step_response(zeta, t):
    if zeta < 1:
        wd = omega_n * np.sqrt(1 - zeta**2)
        phi = np.arccos(zeta)
        y = 1 - (1 / np.sqrt(1 - zeta**2)) * np.exp(-zeta * omega_n * t) * np.sin(wd * t + phi)
    elif abs(zeta - 1) < 1e-2:
        y = 1 - (1 + omega_n * t) * np.exp(-omega_n * t)
    else:
        sqrt_term = np.sqrt(zeta**2 - 1)
        r1 = -omega_n * (zeta - sqrt_term)
        r2 = -omega_n * (zeta + sqrt_term)
        denom = r2 - r1 if abs(r2 - r1) > 1e-6 else 1e-6
        A = r2 / denom
        B = -r1 / denom
        y = 1 - A * np.exp(r1 * t) - B * np.exp(r2 * t)
    return np.clip(y, 0, 2)

# Set up figure with two subplots
fig, (ax_pole, ax_step) = plt.subplots(1, 2, figsize=(12, 5))
plt.subplots_adjust(wspace=0.3)


# Pole plot setup
ax_pole.axhline(0, color='gray', lw=0.5)
ax_pole.axvline(0, color='gray', lw=0.5)
ax_pole.set_xlim([-3, 1])
ax_pole.set_ylim([-1.5, 1.5])
ax_pole.set_xlabel('Real Axis')
ax_pole.set_ylabel('Imaginary Axis')
ax_pole.set_title('Pole Geometry')
ax_pole.plot(real_underdamped,  imag_underdamped,   'b--', lw=1)
ax_pole.plot(real_underdamped, -imag_underdamped,   'b--', lw=1)
ax_pole.plot(real_overdamped_1, np.zeros_like(real_overdamped_1), 'r--', lw=1)
ax_pole.plot(real_overdamped_2, np.zeros_like(real_overdamped_2), 'r--', lw=1)
point_real, = ax_pole.plot([], [], 'ro')
point_imag, = ax_pole.plot([], [], 'bo')
text_pole = ax_pole.text(0.05, 0.9, '', transform=ax_pole.transAxes)

# Step response setup
ax_step.set_xlim([0, 20])
ax_step.set_ylim([0, 2])
ax_step.set_xlabel('Time (s)')
ax_step.set_ylabel('Response')
ax_step.set_title('Step Response')
ax_step.axhline(y=1, color='black', linestyle='--', linewidth=1)
line_step, = ax_step.plot([], [], 'b-', lw=2)
text_step = ax_step.text(0.7, 0.9, '', transform=ax_step.transAxes)

# Init function
def init():
    point_real.set_data([], [])
    point_imag.set_data([], [])
    line_step.set_data([], [])
    text_pole.set_text('')
    text_step.set_text('')
    return point_real, point_imag, line_step, text_pole, text_step

# Animation function
def animate(i):
    zeta = zeta_values[i]

    # Update poles
    if zeta < 1:
        real = -zeta * omega_n
        imag = omega_n * np.sqrt(1 - zeta**2)
        point_real.set_data([], [])
        point_imag.set_data([real, real], [imag, -imag])
    elif abs(zeta - 1) < 1e-2:
        real = -omega_n
        point_real.set_data([real, real], [0, 0])
        point_imag.set_data([], [])
    else:
        sqrt_term = np.sqrt(zeta**2 - 1)
        real1 = -zeta * omega_n + omega_n * sqrt_term
        real2 = -zeta * omega_n - omega_n * sqrt_term
        point_real.set_data([real1, real2], [0, 0])
        point_imag.set_data([], [])

    # Update step response
    y = step_response(zeta, t)
    line_step.set_data(t, y)

    # Update texts
    text_pole.set_text(f'ζ = {zeta:.2f}')
    text_step.set_text(f'ζ = {zeta:.2f}')

    return point_real, point_imag, line_step, text_pole, text_step

# Create and save animation
ani = animation.FuncAnimation(fig, animate, frames=len(zeta_values),
                              init_func=init, blit=True, interval=50)
ani.save("pole_and_step_response.gif", writer="pillow", fps=30)


plt.show()