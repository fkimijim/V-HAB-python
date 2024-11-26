import numpy as np

def calculateILEquilibriumSimple(oLumen, oShell):
    """
    Calculates the equilibrium loading of CO2 in the IL based on the temperature and pressure.
    Output is the mol fraction of CO2 in the IL (xCO2 / (xCO2 + xIL)).
    """
    # Set min and max temperature values from the experimental dataset
    fMinTemp = 283.1  # [K]
    fMaxTemp = 348.1  # [K]
    afTemperatureData = np.array([283.1, 298.1, 323.1, 348.1])  # [K]
    afTemperature = np.linspace(fMinTemp, fMaxTemp, 100)  # [K]

    # Check which IL is being used, BMIMAc or EMIMAc
    if oShell['afMass'][oShell['oMT']['tiN2I']['BMIMAc']] > 0:
        # Data for BMIMAc ([C1C4Im][OAc])
        afPressureData = 1e6 * np.array([
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
    elif oShell['afMass'][oShell['oMT']['tiN2I']['EMIMAc']] > 0:
        # TODO: Replace with correct dataset for EMIMAc
        afPressureData = afPressureData_BMIMAc
        afSolubilityData = afSolubilityData_BMIMAc
    elif (oShell['afMass'][oShell['oMT']['tiN2I']['BMIMAc']] > 0 and 
          oShell['afMass'][oShell['oMT']['tiN2I']['EMIMAc']] > 0):
        raise ValueError("No vapor-liquid equilibrium profiles are set for mixtures of ILs")

    fMaxPressure = np.max(afPressureData)  # [Pa]
    afPressure = np.linspace(0, fMaxPressure, 100)  # [Pa]

    # Fit coefficients from external analysis
    afSlopeCoeff = np.array([0.0462, 0.0472, 0.0485, 0.0592])
    afInterceptCoeff = np.array([0.231, 0.2618, 0.3501, 0.5464])

    mrEquilibriumSolubility = np.zeros((len(afTemperatureData), len(afPressure)))

    # Build the equilibrium curves as a function of gas pressure
    for ii in range(1, len(afPressure)):
        for jj in range(len(afTemperatureData)):
            mrEquilibriumSolubility[jj, ii] = afSlopeCoeff[jj] * np.log(afPressure[ii]) - afInterceptCoeff[jj]

    # Look up molar fraction of water in the IL
    fShellMolarRatios = (oShell['arPartialMass'] / oShell['oMT']['afMolarMass']) / \
                        np.sum(oShell['arPartialMass'] / oShell['oMT']['afMolarMass'])
    rH2OLookUp = fShellMolarRatios[oShell['oMT']['tiN2I']['H2O']]

    # Look up current pressure of the gas and temperature of the IL
    fPressureLookUp = oLumen['fPressure']  # [Pa]
    fTemperatureLookUp = oShell['fTemperature']  # [K]

    if fPressureLookUp < fMaxPressure:
        closestIndex = np.argmin(np.abs(afPressure - fPressureLookUp))
        for ii in range(len(afTemperatureData) - 1):
            if afTemperatureData[ii] <= fTemperatureLookUp <= afTemperatureData[ii + 1]:
                v1 = mrEquilibriumSolubility[ii + 1, closestIndex]
                v2 = mrEquilibriumSolubility[ii, closestIndex]
                a2 = afTemperatureData[ii + 1]
                a1 = afTemperatureData[ii]
                break
    else:
        raise ValueError("IL pressure is out of the range necessary for determining equilibrium loading!")

    rEquilibriumLookUp = v2 - (fTemperatureLookUp - a2) * (v2 - v1) / (a1 - a2)
    return rEquilibriumLookUp
