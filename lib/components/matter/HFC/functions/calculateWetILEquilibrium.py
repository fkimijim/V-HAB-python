import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def exp_fit(x, a, b):
    """Exponential fitting function."""
    return a * np.exp(b * x)

def calculate_equilibrium(a=1, fxH2OLookUp=0):
    if a == 1:
        fMinTemp = 303.54  # [K]
        fMaxTemp = 343.6  # [K]
        afTemperatureData = [303.54, 313.5, 323.55, 333.44, 343.5]  # [K]
        afTemperature = np.linspace(fMinTemp, fMaxTemp, 100)  # [K]
        afxH2O = [0, 0.2045, 0.4054, 0.6426, 0.8015]

        # Equilibrium pressure data for different water mol fractions
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
        afTemperatureData = [303.3, 313.4, 323.4, 333.4, 343.3]  # [K]
        afTemperature = np.linspace(fMinTemp, fMaxTemp, 100)  # [K]
        afxH2O = [0, 0.2059, 0.4016, 0.6066]

        # Similar data initialization for `a == 0` case omitted for brevity
        raise NotImplementedError("Data for a == 0 is not implemented.")
    else:
        raise ValueError("Invalid 'a' value. Only 0 or 1 supported.")

    oFit = []
    if fxH2OLookUp == 0:
        afEqPressureTemp = {}
        afEqSolubilityTemp = {}
        for iTemp, temp in enumerate(afTemperatureData):
            pressure_temp = afEqPressureData[1][iTemp, ~np.isnan(afEqPressureData[1][iTemp, :])]
            solubility_temp = afEqSolubilityData[1][iTemp, ~np.isnan(afEqSolubilityData[1][iTemp, :])]

            afEqPressureTemp[iTemp] = pressure_temp
            afEqSolubilityTemp[iTemp] = solubility_temp

            # Fit exponential curve
            popt, _ = curve_fit(exp_fit, solubility_temp, pressure_temp)
            oFit.append(popt)

    # Plot the fitted data
    plt.figure(2)
    for iTemp, fit_params in enumerate(oFit):
        solubility_temp = afEqSolubilityTemp[iTemp]
        pressure_temp = afEqPressureTemp[iTemp]
        plt.plot(solubility_temp, exp_fit(solubility_temp, *fit_params), label=f"Temp {afTemperatureData[iTemp]:.2f} K")
        plt.scatter(solubility_temp, pressure_temp, marker='o', label=f"Data {afTemperatureData[iTemp]:.2f} K")
    plt.scatter([0.27], [101325], marker='s', label='Point of Interest')
    plt.legend()
    plt.xlabel('Solubility (mol fraction)')
    plt.ylabel('Pressure (Pa)')
    plt.show()

    # Plot raw solubility and pressure data
    plt.figure(10)
    for i in range(5):
        plt.plot(afEqSolubilityData[1][i, :], afEqPressureData[1][i, :], label=f"Row {i+1}")
    plt.xlabel('Solubility (mol fraction)')
    plt.ylabel('Pressure (Pa)')
    plt.legend()
    plt.show()

    return oFit
