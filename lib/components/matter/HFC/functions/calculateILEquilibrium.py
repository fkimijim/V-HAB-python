import numpy as np
import matplotlib.pyplot as plt

# Constants and parameters
R = 8.314  # [J/mol/K]
fDensityIL = 1052  # [kg/m^3]
fTemperature = 283.15  # [K]
fPressure = 101325  # [Pa]
fVaporPressure = 6501 * 1e3  # [Pa]

# Initialize molar fractions of CO2 and IL
n = 100
x = np.zeros((n, 2))
x[:, 0] = np.linspace(0, 1, n)  # mol fraction of CO2 (component 1)
x[:, 1] = 1 - x[:, 0]  # mol fraction of IL (component 2)

# Pure component parameters: column 1 - CO2; column 2 - BMIMAc
afMolarMass = [0.04401, 0.19826]  # [kg/mol]
afMolarVolume = [R * fTemperature / fPressure, afMolarMass[1] / fDensityIL]
afCriticalTemperature = [304.13, 867.68]  # [K]
afCriticalPressure = [7385, 2942] * 1e3  # [Pa]
afBeta = np.array([[1.005, 1.0], [0.43866, 1.34306], [-0.10498, 0], [0.06250, 0]])  # unitless
afLambda = np.array([[0, 0.11580], [0.53511, 0]])  # unitless
afMixing = np.array([[0, -0.03976], [-0.03976, 0]])  # unitless
afTao = np.array([[0, 79.594], [79.594, 0]])  # [K]

# Initialize results
afFugacityCoefficient = np.zeros((n, 2))

# Calculate fugacity coefficients
for qq in range(n):
    alpha = np.zeros(2)
    aSubstance = np.zeros(2)
    bSubstance = np.zeros(2)
    alpha_single = np.zeros((4, 2))
    
    for ii in range(2):
        rTemperatureRatio = fTemperature / afCriticalTemperature[ii]
        for kk in range(4):
            alpha_single[kk, ii] = afBeta[kk, ii] * (1 / rTemperatureRatio - rTemperatureRatio)**(kk - 1)
        alpha[ii] = np.sum(alpha_single[:, ii])
        aSubstance[ii] = 0.427480 * R**2 * afCriticalTemperature[ii]**2 / afCriticalPressure[ii] * alpha[ii]
        bSubstance[ii] = 0.08664 * R * afCriticalTemperature[ii] / afCriticalPressure[ii]
    
    # Equation of state
    aTotal, bTotal = 0, 0
    aSingle = np.zeros((2, 2))
    bSingle = np.zeros((2, 2))
    afFugacity = np.zeros((2, 2))
    afKparameter = np.zeros((2, 2))
    
    for ii in range(2):
        for jj in range(2):
            afFugacity[ii, jj] = 1 + afTao[ii, jj] / fTemperature
            afKparameter[ii, jj] = (afLambda[ii, jj] * afLambda[jj, ii] * 
                                     (x[qq, ii] + x[qq, jj]) / 
                                     (afLambda[jj, ii] * x[qq, ii] + afLambda[ii, jj] * x[qq, jj]))
            if ii == jj:
                afKparameter[ii, jj] = 0
            aSingle[ii, jj] = (np.sqrt(aSubstance[ii] * aSubstance[jj]) * afFugacity[ii, jj] *
                               (1 - afKparameter[ii, jj]) * x[qq, ii] * x[qq, jj])
            bSingle[ii, jj] = ((bSubstance[ii] + bSubstance[jj]) * (1 - afKparameter[ii, jj]) * 
                               (1 - afMixing[ii, jj]) * x[qq, ii] * x[qq, jj])
    aTotal = np.sum(aSingle)
    bTotal = 0.5 * np.sum(bSingle)

    # Fugacity coefficients
    aPrimeTotal = np.zeros(2)
    bPrimeTotal = np.zeros(2)
    for ii in range(2):
        aPrimeTotal[ii] = 2 * np.sum(aSingle[ii, :])
        bPrimeTotal[ii] = np.sum(bSingle[ii, :])
    
    for ii in range(2):
        ln_fugacity = (np.log(R * fTemperature / (fPressure * (afMolarVolume[ii] - bTotal))) +
                       bPrimeTotal[ii] * (1 / (afMolarVolume[ii] - bTotal) -
                                          aTotal / (R * fTemperature * bTotal * (afMolarVolume[ii] + bTotal))) +
                       aTotal / (R * fTemperature * bTotal) *
                       (aPrimeTotal[ii] / aTotal - bPrimeTotal[ii] / bTotal + 1) *
                       np.log(afMolarVolume[ii] / (afMolarVolume[ii] + bTotal)))
        afFugacityCoefficient[qq, ii] = np.exp(ln_fugacity)

# Plot fugacity coefficient
plt.figure(1)
plt.plot(x[:, 0], afFugacityCoefficient[:, 0])
plt.xlabel('CO2 in solution (mol fraction)')
plt.ylabel('Fugacity Coefficient')
plt.title('Fugacity Coefficient vs. CO2 Mol Fraction')
plt.grid()

# Calculate PP and plot
PP2 = (x[:, 0] * fVaporPressure * 
       np.exp(np.log(afFugacityCoefficient[:, 0] / x[:, 0]) + 
              (1 - afFugacityCoefficient[:, 0] / x[:, 0])))

afPressureData = np.array([
    [0.0102, 0.0502, 0.1002, 0.3997, 0.6994, 0, 0, 0, 0],
    [0.0101, 0.0502, 0.1003, 0.3999, 0.7002, 0.9996, 1.3001, 1.5001, 1.9994],
    [0.0104, 0.0504, 0.1004, 0.3995, 0.7003, 1.0001, 1.3002, 1.4995, 1.9993],
    [0.0104, 0.0505, 0.1000, 0.4002, 0.6994, 1.0003, 1.2994, 1.4997, 1.9993]
])

afSolubilityData = np.array([
    [0.192, 0.273, 0.307, 0.357, 0.394, 0, 0, 0, 0],
    [0.188, 0.252, 0.274, 0.324, 0.355, 0.381, 0.405, 0.420, 0.455],
    [0.108, 0.176, 0.204, 0.263, 0.292, 0.315, 0.334, 0.346, 0.373],
    [0.063, 0.129, 0.161, 0.226, 0.253, 0.272, 0.287, 0.294, 0.316]
])

plt.figure(2)
plt.plot(x[:, 0], PP2 / 1e6, label='Calculated PP2')
for ii in range(4):
    plt.plot(afSolubilityData[ii, :], afPressureData[ii, :], '--o', label=f'Temp {283.1 + 15 * ii} K')
plt.xlabel('CO2 in solution (mol fraction)')
plt.ylabel('Pressure (MPa)')
plt.legend()
plt.title('Pressure vs. CO2 Mol Fraction')
plt.grid()
plt.show()
