import numpy as np

def calculateILEquilibriumImproved(oLumen, oShell, tEquilibriumCurveFits, fShellDensity):
    """
    Calculates the equilibrium partial pressure of CO2 in the gas above the IL.
    Correlates gas pressure of the solute gas with how much can be absorbed
    into the solvent based on Vapor Liquid Equilibrium (VLE) curves.
    """
    # Extract curve fit coefficients and temperature data
    afFitCoefficientA = tEquilibriumCurveFits['afFitCoefficients'][:, 0]
    afFitCoefficientB = tEquilibriumCurveFits['afFitCoefficients'][:, 1]
    afTemperatureData = tEquilibriumCurveFits['afTemperatureData']

    # Calculate molar ratios for the shell and lumen
    afShellMolarRatios = (oShell['arPartialMass'] / oShell['oMT']['afMolarMass']) / \
                         np.sum(oShell['arPartialMass'] / oShell['oMT']['afMolarMass'])
    afLumenMolarRatios = (oLumen['arPartialMass'] / oLumen['oMT']['afMolarMass']) / \
                         np.sum(oLumen['arPartialMass'] / oLumen['oMT']['afMolarMass'])

    fMolFractionCO2LookUp = afShellMolarRatios[oShell['oMT']['tiN2I']['CO2']]
    if np.isnan(fMolFractionCO2LookUp):
        fMolFractionCO2LookUp = 0

    fMolFractionCO2Lumen = afLumenMolarRatios[oLumen['oMT']['tiN2I']['CO2']]
    fPressure = oLumen['fPressure']
    fTemperatureLookUp = oLumen['fTemperature']
    fMinTemp = np.min(afTemperatureData)
    fMaxTemp = np.max(afTemperatureData)

    # Ensure temperature is within the range of the data
    if fTemperatureLookUp <= fMinTemp:
        fTemperatureLookUp = fMinTemp
    elif fTemperatureLookUp >= fMaxTemp:
        fTemperatureLookUp = fMaxTemp

    # Find closest indices for temperature interpolation
    closestIndex = np.argmin(np.abs(afTemperatureData - fTemperatureLookUp))
    deltaDirection = afTemperatureData[closestIndex] - fTemperatureLookUp

    if deltaDirection < 0:
        lowerIndex = closestIndex
        upperIndex = closestIndex + 1
    elif deltaDirection > 0:
        upperIndex = closestIndex
        lowerIndex = closestIndex - 1
    else:
        lowerIndex = upperIndex = closestIndex

    # Calculate equilibrium CO2 pressure using interpolation
    p1 = afFitCoefficientA[lowerIndex] * np.exp(afFitCoefficientB[lowerIndex] * fMolFractionCO2LookUp)
    p2 = afFitCoefficientA[upperIndex] * np.exp(afFitCoefficientB[upperIndex] * fMolFractionCO2LookUp)
    T1 = afTemperatureData[lowerIndex]
    T2 = afTemperatureData[upperIndex]

    if p1 == p2:
        fEquilibriumCO2Pressure = p1
    else:
        fEquilibriumCO2Pressure = p1 + (p2 - p1) / (T2 - T1) * (fTemperatureLookUp - T1)

    # Calculate Henry's constant
    if fMolFractionCO2LookUp == 0:
        fHenrysConstant = 2200
    else:
        fHenrysConstant = fEquilibriumCO2Pressure / (
            fMolFractionCO2LookUp * (fShellDensity / oShell['fMolarMass']) *
            oShell['oMT']['Const']['fUniversalGas'] * fTemperatureLookUp
        )

    return fEquilibriumCO2Pressure, fHenrysConstant
