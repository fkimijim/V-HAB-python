import numpy as np
import matplotlib.pyplot as plt

# Constants
R = 8.3145  # [J/mol*K]
T = 293  # [K] Lab room temperature

# Ionic Liquid (IL) properties
v_d = 406  # [mPa-s] Dynamic viscosity of IL
p = 1.0538  # [g/cm^3] Density of IL
v = (v_d / p) * (1e-6)  # [m^2/s] Kinematic viscosity
D = 7.52398e-11  # [m^2/s] Diffusivity of CO2 in IL

# Hollow Fiber Contactor numbers
L_gas = 17.9832  # [m] Length of gas channels (118 fibers, 6" each)
L_liquid = 0.0315  # [m] Average length of particle travel across contactor
A_x_gas = 5.6385e-05 / 4  # [m^2] Gas flow channel cross-sectional area
A_x_liquid = 2 * ((np.pi / 4) * ((0.364 * 2.54 / 100) ** 2))  # [m^2] Inlet areas of the liquid channel
Flow_g = np.linspace(0.2, 0.6, 5)  # [SLPM] Gas flow rate

# Initialize arrays
Q_g = Flow_g / 60000  # [m^3/s] Convert gas flow rate to m^3/s
delta_C = np.linspace(2, 4, 6)  # [Torr] Partial pressure gradient of gas species of interest

# Preallocate results
d_ppm = np.zeros((len(Flow_g), len(delta_C)))
vel_gas = np.zeros(len(Flow_g))
t_gas_all = np.zeros(len(Flow_g))
t_liquid = 0  # Placeholder for residence time of liquid

# Loop over gas flow rates
for i in range(len(Flow_g)):
    Q_l = 1.51e-6  # [m^3/s] IL flow rate (90.6 mL/min)
    vel_gas[i] = Q_g[i] / A_x_gas  # [m/s] Gas velocity
    vel_liquid = Q_l / A_x_liquid  # [m/s] Liquid velocity

    # Dimensionless numbers
    Re = (0.00065 * vel_liquid) / v  # Reynolds number
    Sc = v / D  # Schmidt number
    a, b, c = 0.7742, 0.67, 1 / 3  # Correlation coefficients
    Sh = a * (Re ** b) * (Sc ** c)  # Sherwood number

    k = Sh * D / 0.00065  # [m/s] Mass transfer coefficient
    A_HFM = 0.035909606  # [m^2] Contact area
    V_HFM = 2.1611e-06  # [m^3] Inner housing volume

    # Loop over concentration gradients
    for j in range(len(delta_C)):
        delta_C_m = delta_C[j] / (R * T)  # [mol/m^3] Molar concentration gradient

        x = delta_C_m * k  # [mol/m^2*s] Mass flux rate
        n = x * A_HFM  # [mol/s] Molar rate of absorption
        dP = (n * R * T) / V_HFM  # [Torr/s] Rate of partial pressure change

        t_gas_all[i] = L_gas / vel_gas[i]  # [s] Residence time
        delta_n = dP * t_gas_all[i]  # [Torr] Predicted partial pressure change

        d_ppm[i, j] = (delta_n / 760) * 100 * 10000  # [ppm] Concentration change

        # Print results for this iteration
        print(f"The change in concentration is {d_ppm[i, j]:.2f} ppm CO2 "
              f"for a concentration gradient of {delta_C[j]} Torr and a gas flow rate of {Flow_g[i]} SLPM.")

# Residence time calculations
t_gas = (L_gas / 118) / vel_gas  # [s] Gas residence time (scaled for appropriate contactor length)
t_liquid = L_liquid / vel_liquid  # [s] Liquid residence time

# Print important parameters
print(f"The Reynolds number is {Re:.2f}.")
print(f"The Schmidt number is {Sc:.2f}.")
print(f"The Sherwood number is {Sh:.2f}.")
print(f"The residence time of the liquid is {t_liquid:.2f} seconds.")
for i in range(len(t_gas)):
    print(f"The residence time of the gas is {t_gas[i]:.2f} seconds at a gas flow rate of {Flow_g[i]} SLPM.")

# Plotting the results
plt.figure(figsize=(10, 6))
for j in range(len(delta_C)):
    plt.plot(Flow_g, d_ppm[:, j], label=f'{delta_C[j]} Torr Concentration Gradient')

plt.grid(True)
plt.xlabel('Gas Flow Rate [SLPM]')
plt.ylabel('CO$_2$ Absorbed [Δppm]')
plt.title('CO$_2$ uptake as a function of flow rate and concentration gradient')
plt.legend()
plt.show()
