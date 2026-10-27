
import numpy as np
import matplotlib.pyplot as plt
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt

# Parameters
alpha_deg = 5.0
alpha     = np.radians(alpha_deg)
V_inf     = 40.0          # free-stream speed  [m/s]
c         = 1.0           # chord length        [m]
rho       = 1.225         # air density        [kg/m^3]
N         = 10            # number of panels
dt_star   = 0.25          # Delta_t * V_inf / c  (non-dim time step)
dt        = dt_star * c / V_inf
N_steps   = 600           # 15 chord lengths of travel


# Panel geometry
dx   = c / N
x_bv = np.array([(j + 0.25) * dx for j in range(N)])  # bound vortex locations
x_cp = np.array([(j + 0.75) * dx for j in range(N)])  # collocation points

# Downwash at cp_i due to unit vortex at x_bv[j]  (2D Biot-Savart)
A = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        A[i, j] = -1.0 / (2.0 * np.pi * (x_cp[i] - x_bv[j]))

# Wake vortex
def x_wake(k, n):
    """x-position (body frame) of wake vortex shed at step k, evaluated at step n."""
    return c + V_inf * (n - k + 0.5) * dt

def wake_inf(k, n, x_field):
    """Downwash at x_field due to unit-strength wake vortex k at step n."""
    return -1.0 / (2.0 * np.pi * (x_field - x_wake(k, n)))

Gw         = {}                    # Gw[k] = strength of wake vortex shed at step k
Gamma_arr  = np.zeros(N_steps)
L_arr      = np.zeros(N_steps)
D_arr      = np.zeros(N_steps)
t_arr      = np.arange(1, N_steps + 1) * dt
Gamma_prev = 0.0



# Timestep loop
for n in range(1, N_steps + 1):

    # Influence of new wake vortex (shed this step) at each collocation point
    B = np.array([wake_inf(n, n, x_cp[i]) for i in range(N)])

    # Downwash from all previously shed wake vortices at each cp
    w_old = np.zeros(N)
    for k, gw_k in Gw.items():
        for i in range(N):
            w_old[i] += gw_k * wake_inf(k, n, x_cp[i])

    sum_old = sum(Gw.values())   # total old wake circulation (Kelvin RHS)

    # Assemble (N+1) x (N+1) system:
    #   rows 0..N-1 : no-normal-flow at each collocation point
    #   row N       : Kelvin's theorem (total circulation = 0)
    M   = np.zeros((N + 1, N + 1))
    rhs = np.zeros(N + 1)
    M[:N, :N] = A          # bound vortex influence
    M[:N,  N] = B          # new wake vortex influence
    M[N,  :N] = 1.0        # Kelvin: sum of bound strengths
    M[N,   N] = 1.0        # Kelvin: new wake strength
    rhs[:N]   = -V_inf * np.sin(alpha) - w_old
    rhs[N]    = -sum_old

    sol      = np.linalg.solve(M, rhs)
    Gamma_b  = sol[:N]     # individual panel vortex strengths
    Gw[n]    = sol[N]      # new wake vortex strength

    # Total bound circulation and its time derivative
    Gamma          = np.sum(Gamma_b)
    Gamma_arr[n-1] = Gamma
    dGdt           = (Gamma - Gamma_prev) / dt

    # Lift  (Katz & Plotkin Eq. 13.36)
    L_arr[n-1] = rho * (V_inf * Gamma + dGdt * c)

    # Wake downwash at all collocation points (including newly shed vortex)
    w_W = np.zeros(N)
    for k, gw_k in Gw.items():
        for i in range(N):
            w_W[i] += gw_k * wake_inf(k, n, x_cp[i])

    # Circulation-weighted effective downwash
    abs_Gb   = np.abs(Gamma_b)
    w_W_eff  = np.dot(abs_Gb, w_W) / (np.sum(abs_Gb) + 1e-30)

    # Drag  (Katz & Plotkin Eq. 13.37)
    D_arr[n-1] = rho * (w_W_eff * Gamma + dGdt * c * np.sin(alpha))

    Gamma_prev = Gamma

# Steady-state reference values
Gamma_ss = np.pi * V_inf * c * np.sin(alpha)   # thin-airfoil theory
L_ss     = rho * V_inf * Gamma_ss
q_ref    = 0.5 * rho * V_inf**2 * c
tau      = t_arr * V_inf / c                    # non-dim time V_inf*t/c

# Plots 
fig, axes = plt.subplots(3, 1, figsize=(6, 9), sharex=True)
fig.subplots_adjust(hspace=0.38, top=0.96, bottom=0.07, left=0.13, right=0.97)

ax = axes[0]
ax.plot(tau, Gamma_arr / Gamma_ss, 'o-', ms=2.5, lw=1.4, color='steelblue',
        markevery=12, label=f'Panel method (N={N})')
ax.axhline(1.0, ls='--', color='gray', lw=1.2, label=r'Steady-state $\Gamma_\infty$')
ax.set_ylabel(r'$\Gamma(t)\;/\;\Gamma_\infty$', fontsize=10)
ax.set_title(r'(a) Bound Circulation', fontsize=10, pad=3)
ax.set_ylim(0, 1.18); ax.legend(fontsize=8, loc='lower right'); ax.grid(True, alpha=0.3)
ax.annotate(r'$\Gamma(0)=0$', xy=(0.25, Gamma_arr[0]/Gamma_ss), xytext=(2, 0.15),
    arrowprops=dict(arrowstyle='->', lw=0.8, color='steelblue'), fontsize=7.5, color='steelblue')
ax.annotate(r'Slow approach to $\Gamma_\infty$', xy=(10, 0.94), xytext=(6, 0.70),
    arrowprops=dict(arrowstyle='->', lw=0.8, color='gray'), fontsize=7.5, color='gray')

ax = axes[1]
ax.plot(tau, L_arr / L_ss, 's-', ms=2.5, lw=1.4, color='darkorange',
        markevery=12, label=f'Panel method (N={N})')
ax.axhline(1.0, ls='--', color='gray', lw=1.2, label=r"Steady-state $L'_\infty$")
ax.axhline(0.5, ls=':', color='purple', lw=1.0,
           label=r"Wagner: $L'(0^+)=\frac{1}{2}L'_\infty$")
ax.set_ylabel(r"$L'(t)\;/\;L'_\infty$", fontsize=10)
ax.set_title(r"(b) Lift per Unit Span", fontsize=10, pad=3)
ax.legend(fontsize=8, loc='right'); ax.grid(True, alpha=0.3)
ax.annotate('Apparent-mass\nspike at $t=0^+$', xy=(0.25, L_arr[0]/L_ss),
    xytext=(2.5, 1.55),
    arrowprops=dict(arrowstyle='->', lw=0.8, color='darkorange'), fontsize=7.5,
    color='darkorange')

ax = axes[2]
ax.plot(tau, D_arr / q_ref, '^-', ms=2.5, lw=1.4, color='crimson',
        markevery=12, label=f'Panel method (N={N})')
ax.axhline(0.0, ls='--', color='gray', lw=0.8)
ax.set_ylabel(r'$C_D(t)$', fontsize=10)
ax.set_xlabel(r'Non-dimensional time $\;V_\infty t/c$', fontsize=10)
ax.set_title(r"(c) Induced Drag Coefficient", fontsize=10, pad=3)
ax.legend(fontsize=8, loc='upper right'); ax.grid(True, alpha=0.3)
ax.annotate('Large initial drag\n(close starting vortex)',
    xy=(0.25, D_arr[0]/q_ref), xytext=(3, 0.045),
    arrowprops=dict(arrowstyle='->', lw=0.8, color='crimson'), fontsize=7.5, color='crimson')
ax.annotate(r"$C_D\to 0$ (d'Alembert)", xy=(12, 0.001), xytext=(7, 0.012),
    arrowprops=dict(arrowstyle='->', lw=0.8, color='gray'), fontsize=7.5, color='gray')

plt.show()
