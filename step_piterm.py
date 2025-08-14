import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.integrate import solve_ivp

# System constants
tau = 1.0
k = 1.0
Ki = 1.0
t_eval = np.linspace(0, 20, 1000)
zeta_values = np.arange(0.01, 4.0, 0.01)

# Precomputed pole trajectories (for standard ω_n = 1 view)
omega_n = np.sqrt(k * Ki / tau)
zeta_traj = np.arange(0, 3, 0.001)
real_underdamped = -zeta_traj[zeta_traj < 1] * omega_n
imag_underdamped = omega_n * np.sqrt(1 - zeta_traj[zeta_traj < 1] ** 2)
real_overdamped_1 = -zeta_traj[zeta_traj > 1] * omega_n + omega_n * np.sqrt(zeta_traj[zeta_traj > 1] ** 2 - 1)
real_overdamped_2 = -zeta_traj[zeta_traj > 1] * omega_n - omega_n * np.sqrt(zeta_traj[zeta_traj > 1] ** 2 - 1)
real_underdamped = np.append(real_underdamped, -omega_n)
imag_underdamped = np.append(imag_underdamped, 0)
real_overdamped_1 = np.insert(real_overdamped_1, 0, -omega_n)
real_overdamped_2 = np.insert(real_overdamped_2, 0, -omega_n)


# Closed-loop simulation using solve_ivp
def simulate_process(Kp, Ki):
    def dynamics(t, x):
        y, integral = x
        e = 1 - y
        u = Kp * e + Ki * integral
        dy = (-y + k * u) / tau
        dintegral = e
        return [dy, dintegral]

    sol = solve_ivp(dynamics, [t_eval[0], t_eval[-1]], [0, 0], t_eval=t_eval)
    y = sol.y[0]
    integral = sol.y[1]
    e = 1 - y
    u = Kp * e + Ki * integral
    p_term = Kp * e
    i_term = u - p_term
    return y, u, p_term, i_term


# Set up plots
fig, (ax_pole, ax_step) = plt.subplots(1, 2, figsize=(13, 5))
plt.subplots_adjust(wspace=0.3)

# Pole plot
ax_pole.axhline(0, color='gray', lw=0.5)
ax_pole.axvline(0, color='gray', lw=0.5)
ax_pole.set_xlim([-3, 1])
ax_pole.set_ylim([-1.5, 1.5])
ax_pole.set_xlabel('Real Axis')
ax_pole.set_ylabel('Imaginary Axis')
ax_pole.set_title('Pole Geometry')
ax_pole.plot(real_underdamped, imag_underdamped, 'b--', lw=1)
ax_pole.plot(real_underdamped, -imag_underdamped, 'b--', lw=1)
ax_pole.plot(real_overdamped_1, np.zeros_like(real_overdamped_1), 'r--', lw=1)
ax_pole.plot(real_overdamped_2, np.zeros_like(real_overdamped_2), 'r--', lw=1)
point_real, = ax_pole.plot([], [], 'ro')
point_imag, = ax_pole.plot([], [], 'bo')
text_pole = ax_pole.text(0.05, 0.9, '', transform=ax_pole.transAxes)

# Step response + PI terms
ax_step.set_xlim([0, 20])
ax_step.set_ylim([-0.5, 2])
ax_step.set_xlabel('Time (s)')
ax_step.set_ylabel('Value')
ax_step.set_title('Response and Control Terms')
ax_step.axhline(y=1, color='black', linestyle='--', linewidth=1)
ax_step.axhline(y=0, color='black', linestyle='--', linewidth=1)
line_y, = ax_step.plot([], [], 'b-', lw=2, label='Output y(t)')
line_p, = ax_step.plot([], [], 'r--', lw=1.5, label='P term')
line_i, = ax_step.plot([], [], 'g--', lw=1.5, label='I term')
line_u, = ax_step.plot([], [], 'k-.', lw=1.2, label='Control u(t)')
text_step = ax_step.text(0.6, 0.9, '', transform=ax_step.transAxes)
ax_step.legend(loc='lower right')


# Init
def init():
    point_real.set_data([], [])
    point_imag.set_data([], [])
    line_y.set_data([], [])
    line_p.set_data([], [])
    line_i.set_data([], [])
    line_u.set_data([], [])
    text_pole.set_text('')
    text_step.set_text('')
    return point_real, point_imag, line_y, line_p, line_i, line_u, text_pole, text_step


# Animate
def animate(i):
    zeta = zeta_values[i]
    wn = np.sqrt(k * Ki / tau)
    Kp = 2 * zeta * np.sqrt(tau * k * Ki) - 1

    y, u, p_term, i_term = simulate_process(Kp, Ki)

    # Update poles
    if zeta < 1:
        real = -zeta * omega_n
        imag = omega_n * np.sqrt(1 - zeta ** 2)
        point_real.set_data([], [])
        point_imag.set_data([real, real], [imag, -imag])
    elif np.isclose(zeta, 1.0):
        real = -omega_n
        point_real.set_data([real], [0])
        point_imag.set_data([], [])
    else:
        sqrt_term = np.sqrt(zeta ** 2 - 1)
        real1 = -zeta * omega_n + omega_n * sqrt_term
        real2 = -zeta * omega_n - omega_n * sqrt_term
        point_real.set_data([real1, real2], [0, 0])
        point_imag.set_data([], [])

    # Update plots
    line_y.set_data(t_eval, y)
    line_p.set_data(t_eval, p_term)
    line_i.set_data(t_eval, i_term)
    line_u.set_data(t_eval, u)
    text_pole.set_text(f'ζ = {zeta:.2f}')
    text_step.set_text(f'Kp = {Kp:.2f}, Ki = {Ki:.2f}')
    return point_real, point_imag, line_y, line_p, line_i, line_u, text_pole, text_step


# Run animation
ani = animation.FuncAnimation(fig, animate, frames=len(zeta_values),
                              init_func=init, blit=True, interval=50)

# Optional: Save as video
ani.save("pi_response_solve_ivp.mp4", writer="ffmpeg", fps=30, dpi=200)

plt.show()
