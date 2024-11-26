import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load Experimental Data
# Assume HFC_Gas, HFC_Gas_E, HFC_IL are loaded here from a file
# Replace this with your data loading logic
# Example: HFC_Gas = np.load('HFC_Gas.npy')
# For this code example, dummy arrays are used
HFC_Gas = np.array([[0.2, 1000], [0.4, 3000], [0.6, 5000]])  # Dummy data
HFC_Gas_E = np.array([[0.2, 100], [0.4, 150], [0.6, 200]])  # Dummy data
HFC_IL = np.array([[0.1]])  # Dummy data

# Universal Constants
R = 8.3145  # Gas Constant [J/mol*K]
T = 293.15  # Room Temperature [K]
T_std = 273.15
P = 8.41e4
P_std = 1e5

# Hollow Fiber Contactor Constants
L_gas = 17.9832  # [m]
L_liquid = 0.0315  # [m]
A_x_gas = 1.4180e-05  # [m^2]
A_x_liquid = 2 * ((np.pi / 4) * ((0.364) * 2.54 / 100) ** 2)  # [m^2]
A_HFM = 0.0379  # Contact Area [m^2]
V_HFM = 2.1611e-06  # Contact Volume [m^3]
L_c_HFM = 0.00065  # Characteristic Length [m]

# IL Properties
v_d = 406  # Dynamic Viscosity of IL [mPa-s]
p = 1.0538  # Density of IL [g/cm^3]
v = (v_d / p) * (1e-6)  # Kinematic Viscosity [m^2/s]
D = 7.52398e-11  # Diffusivity of CO2 in IL [m^2/s]
Q_l = HFC_IL[0, 0] * 1.6667e-8  # IL Flow Rate [m^3/s]
vl = Q_l / A_x_liquid  # Average Liquid Velocity [m/s]
Re = (vl * L_c_HFM) / v  # Reynolds Number for the IL
Sc = v / D  # Schmidt Number for the IL

# Gas Properties
delta_C = 2  # Concentration Gradient [torr]
Q_g_std = HFC_Gas[:, 0] / 60000  # Gas Flow Rate [m^3/s]
Q_g = Q_g_std * (T / T_std) * (P_std / P)
vg = Q_g / A_x_gas  # Average Gas Velocity [m/s]
tg = L_gas / vg  # Residence Time [s]
dP = HFC_Gas[:, 1] * (P_std / P) * (T / T_std)

# Define Constant
Const = D * delta_C * A_HFM * 1e6 / (L_c_HFM * V_HFM * 760) * (P_std / P) * (T / T_std)

# Define Model Fit Function
def model_fit(x, a):
    return a * (Re ** (2/3)) * (Sc ** (1/3)) * Const * x

# Perform Curve Fitting
popt, pcov = curve_fit(model_fit, tg, dP, bounds=(0, 10))
a_fit = popt[0]
print(f"Fitted Parameter: a = {a_fit}")

# Prepare Model for Plotting
HFC_Gas_MC_PX = np.linspace(0.1, 0.9, 100)
HFC_Gas_MC_PY = model_fit(L_gas / (HFC_Gas_MC_PX / (A_x_gas * 60000)), a_fit)

# Plot Results
plt.figure(figsize=(10, 6))
plt.errorbar(Q_g * 60000, dP, HFC_Gas_E[:, 1], fmt='.k', markersize=10, label='Experiment')
plt.plot(HFC_Gas_MC_PX, HFC_Gas_MC_PY, 'b', label='Fitted Model')
plt.grid(True)
plt.xlim(0.1, 0.8)
plt.ylim(0, 7000)
plt.title('Hollow Fiber CO$_2$ Concentration Difference vs. Gas Flow Rate')
plt.xlabel('Gas Flow Rate [LPM]')
plt.ylabel('Concentration Difference [ΔPPM CO$_2$]')
plt.legend()
plt.show()
