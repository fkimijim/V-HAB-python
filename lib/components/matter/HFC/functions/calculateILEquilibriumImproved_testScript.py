import numpy as np
from scipy.optimize import curve_fit

# Function for exponential fitting
def exp1(x, a, b):
    return a * np.exp(b * x)

# Initialize parameters
a = 1
fMolFractionCO2LookUp = 0.01
fTemperatureLookUp = 320
fxH2OLookUp = 0

# Data from Stevanovic et al. (2012)
if a == 1:
    fMinTemp = 303.54  # [K]
    fMaxTemp = 343.6  # [K]
    afTemperatureData = np.array([303.54, 313.5, 323.55, 333.44, 343.5])  # [K]
    afTemperature = np.linspace(fMinTemp, fMaxTemp, 100)  # [K]
    afxH2O = np.array([0, 0.2045, 0.4054, 0.6426, 0.8015])
    afEqPressureData = {
        1: np.array([
            [0, 9626, 9940, 17661, 20649],
            [0, 14458, 23130, 26572, np.nan],
            [0, 19161, 19716, 32927, np.nan],
            [0, 25555, 35435, np.nan, np.nan],
            [0, 25555, 46378, 30906, 41830]
        ]),
        2: np.array([0, 5860, 9257, 13600, 18752, 24497]),
        3: np.array([0, 4550, 7223, 11207, 15995, 21616]),
        4: np.array([0, 13388, 19029, 25625, 33128, 41094]),
        5: np.array([0, 37860, 45291, 53351, 62021, 71636])
    }
    afEqSolubilityData = {
        1: np.array([
            [0, 0.1904, 0.1932, 0.2155, 0.2188],
            [0, 0.1851, 0.2043, 0.2069, np.nan],
            [0, 0.1730, 0.1759, 0.1945, np.nan],
            [0, 0.1659, 0.1766, np.nan, np.nan],
            [0, 0.1527, 0.1690, 0.1659, 0.1676]
        ]),
        2: np.array([0, 0.1205, 0.1160, 0.1104, 0.1040, 0.0971]),
        3: np.array([0, 0.0656, 0.0635, 0.0606, 0.0572, 0.0534]),
        4: np.array([0, 0.0320, 0.0294, 0.0264, 0.0233, 0.0205]),
        5: np.array([0, 0.0146, 0.0129, 0.0114, 0.0101, 0.0091])
    }

elif a == 0:
    fMinTemp = 303.3  # [K]
    fMaxTemp = 343.3  # [K]
    afTemperatureData = np.array([303.3, 313.4, 323.4, 333.4, 343.3])  # [K]
    afTemperature = np.linspace(fMinTemp, fMaxTemp, 100)  # [K]
    afxH2O = np.array([0, 0.2059, 0.4016, 0.6066])
    afEqPressureData = {
        1: np.array([
            [2796, 4136, 5544],
            [4770, 6845, 8855],
            [7552, 10520, 13148],
            [11168, 15099, 18275]
        ]),
        2: np.array([1749, 3068, 5062, 7874]),
        3: np.array([4325, 7223, 11156, 16149]),
        4: np.array([13175, 18964, 25814, 33186])
    }
    afEqSolubilityData = {
        1: np.array([
            [0.1415, 0.1485, 0.1624],
            [0.1383, 0.1443, 0.1570],
            [0.1339, 0.1387, 0.1501],
            [0.1283, 0.1319, 0.1421]
        ]),
        2: np.array([0.0765, 0.0745, 0.0728, 0.0706]),
        3: np.array([0.0579, 0.0559, 0.0533, 0.0501]),
        4: np.array([0.0390, 0.0358, 0.0322, 0.0287])
    }

# Fit exponential curves
afFitCoefficientsA = []
afFitCoefficientsB = []
for iTemp in range(len(afTemperatureData)):
    afEqPressureTemp = afEqPressureData[1][iTemp, ~np.isnan(afEqPressureData[1][iTemp, :])]
    afEqSolubilityTemp = afEqSolubilityData[1][iTemp, ~np.isnan(afEqSolubilityData[1][iTemp, :])]
    popt, _ = curve_fit(exp1, afEqSolubilityTemp, afEqPressureTemp)
    afFitCoefficientsA.append(popt[0])
    afFitCoefficientsB.append(popt[1])

afFitCoefficientsA = np.array(afFitCoefficientsA)
afFitCoefficientsB = np.array(afFitCoefficientsB)

# Interpolation for the lookup temperature
if fTemperatureLookUp <= fMinTemp:
    fTemperatureLookUp = fMinTemp
    print("Warning: Temperature below minimum range!")

elif fTemperatureLookUp >= fMaxTemp:
    fTemperatureLookUp = fMaxTemp
    print("Warning: Temperature above maximum range!")

closestIndex = np.argmin(np.abs(afTemperatureData - fTemperatureLookUp))
deltaDirection = afTemperatureData[closestIndex] - fTemperatureLookUp

if deltaDirection < 0:
    lowerIndex = closestIndex
    upperIndex = closestIndex + 1
elif deltaDirection > 0:
    upperIndex = closestIndex
    lowerIndex = closestIndex - 1
else:
    lowerIndex = None

if lowerIndex is not None:
    p1 = afFitCoefficientsA[lowerIndex] * np.exp(afFitCoefficientsB[lowerIndex] * fMolFractionCO2LookUp)
    p2 = afFitCoefficientsA[upperIndex] * np.exp(afFitCoefficientsB[upperIndex] * fMolFractionCO2LookUp)
    T1 = afTemperatureData[lowerIndex]
    T2 = afTemperatureData[upperIndex]
    fEquilibriumCO2Pressure = p1 + (p2 - p1) / (T2 - T1) * (fTemperatureLookUp - T1)
else:
    fEquilibriumCO2Pressure = afFitCoefficientsA[closestIndex] * np.exp(afFitCoefficientsB[closestIndex] * fMolFractionCO2LookUp)

print(f"Equilibrium CO2 Pressure: {fEquilibriumCO2Pressure} Pa")
