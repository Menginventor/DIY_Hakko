# Step responses with derivative-on-measurement, all critically damped (ζ = 1)
# Poles fixed at ω_n = 4 rad/s; plant: G(s)=k/(τ s + 1) with τ=1, k=1.
# We sweep K_D from 0 → 10 and re-tune K_P, K_I to keep the same poles.
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# ---- Parameters ----
tau = 1.0
k = 1.0
omega_n = 4.0
zeta = 1.0  # critical damping
KD_values = np.linspace(0, 10.0, 11)  # 0,1,...,10
Tvec = np.linspace(0, 2.0, 2000)
tol = 0.02  # 2% settling band

# ---- Gains to keep the same closed-loop poles (pole placement) ----
# Denominator target: (tau + k K_D) * [ s^2 + 2 zeta omega_n s + omega_n^2 ]
def kp_ki_for_fixed_poles(Kd, tau=1.0, k=1.0, omega_n=4.0, zeta=1.0):
    Kp = ((tau + k*Kd) * (2*zeta*omega_n) - 1.0) / k
    Ki = ((tau + k*Kd) * (omega_n**2)) / k
    return Kp, Ki

# Closed-loop TF for derivative-on-measurement (DoM):
# T(s) = k (Kp s + Ki) / [ (tau + k Kd) s^2 + (1 + k Kp) s + k Ki ]
def closed_loop_DoM(Kd):
    Kp, Ki = kp_ki_for_fixed_poles(Kd, tau, k, omega_n, zeta)
    num = [k*Kp, k*Ki]                        # first-order numerator
    den = [(tau + k*Kd), (1 + k*Kp), k*Ki]    # fixed second-order poles
    return signal.TransferFunction(num, den), Kp, Ki

# ---- Simulation & plotting ----
plt.figure()
metrics = []

for Kd in KD_values:
    sys, Kp, Ki = closed_loop_DoM(Kd)
    t, y = signal.step(sys, T=Tvec)

    # Plot response
    plt.plot(t, y, label=f"K_D={Kd:.0f}")

    # Peak overshoot (%)
    peak = y.max()
    os_percent = max(0.0, (peak - 1.0) * 100.0)

    # Correct 2% settling time:
    # "Last time the response enters the ±2% band and stays within afterwards"
    within = np.abs(y - 1.0) <= tol
    last_out_idx = np.where(~within)[0]
    if last_out_idx.size == 0:
        ts = t[0]  # always within tolerance
    else:
        enter_idx = last_out_idx[-1] + 1
        ts = t[enter_idx] if enter_idx < len(t) else np.nan  # didn't settle within Tvec

    metrics.append((Kd, Kp, Ki, os_percent, ts))

plt.title("Step Response, Critically Damped (ω_n=4, ζ=1, τ=1)")
plt.xlabel("Time [s]")
plt.ylabel("Output")
plt.grid(True)
plt.axhline(y=1,color='k',linestyle = '-')
plt.axhline(y=1.02,color='k',linestyle = '--')
plt.legend(loc="best", ncol=3)


# ---- Print metrics ----
print("K_D   K_P       K_I       %OS    t_s(2%) [s]")
for Kd, Kp, Ki, os_percent, ts in metrics:
    ts_str = f"{ts:.6f}" if not np.isnan(ts) else "—"
    print(f"{Kd:4.0f}  {Kp:8.2f}  {Ki:8.2f}  {os_percent:6.2f}   {ts_str}")
plt.show()