import numpy as np

def calculateILViscosity(this):
    """
    Calculates the viscosity of an IL based on the temperature and the water content.
    
    Returns:
        fViscosityLookUp: Viscosity in mPa*s or cP (same unit).
    """

    # Set min and max temperature values from the experimental dataset
    fMinTemp = 293  # [K]
    fMaxTemp = 363  # [K]
    afTemperature = np.linspace(fMinTemp, fMaxTemp, 100)  # [K]

    # Check which IL is being used, BMIMAc or EMIMAc
    if this["afMass"][this["oMT"]["tiN2I"]["BMIMAc"]] > 0:
        # Data for BMIMAc ([C1C4Im][OAc])
        arH2O = np.array([0, 0.1843, 0.3889, 0.5951, 0.8004])  # [molar fraction]
        afC1 = np.array([2.45, 1.95, 3.86, 2.07, 3.08]) * 10**-3  # [mPa*s/K^1/2]
        afC2 = np.array([1081, 1128, 927, 1021, 751])  # [K]
        afT0 = np.array([185, 177, 183, 168, 175])  # [K]

    elif this["afMass"][this["oMT"]["tiN2I"]["EMIMAc"]] > 0:
        # Data for EMIMAc ([C1C2Im][OAc])
        arH2O = np.array([0, 0.2088, 0.4000, 0.6014, 0.8023])  # [molar fraction]
        afC1 = np.array([10.33, 1.99, 3.93, 1.83, 0.57])  # [mPa*s/K^1/2]
        afC2 = np.array([663, 1042, 890, 1078, 1279])  # [K]
        afT0 = np.array([199, 164, 169, 148, 126])  # [K]

    elif this["afMass"][this["oMT"]["tiN2I"]["BMIMAc"]] > 0 and this["afMass"][this["oMT"]["tiN2I"]["EMIMAc"]] > 0:
        raise ValueError("No viscosity profiles are set for mixtures of ILs")

    # Build the viscosity curves as a function of temperature
    mfViscosity = np.zeros((len(afTemperature), len(arH2O)))
    for ii in range(len(arH2O)):
        for jj in range(len(afTemperature)):
            mfViscosity[jj, ii] = (
                afC1[ii] * afTemperature[jj]**0.5 * np.exp(afC2[ii] / (afTemperature[jj] - afT0[ii]))
            )

    # Look up how much water is currently in the IL as a molar fraction
    if np.sum(this["arPartialMass"]) == 0:
        rH2OLookUp = 0
    else:
        fMolarRatios = (this["arPartialMass"] / this["oMT"]["afMolarMass"]) / np.sum(
            this["arPartialMass"] / this["oMT"]["afMolarMass"]
        )
        rH2OLookUp = fMolarRatios[this["oMT"]["tiN2I"]["H2O"]]

    # Look up current temperature of the IL
    fTemperatureLookUp = this["fTemperature"]

    # Find the closest temperature and interpolate viscosity
    if fMinTemp <= fTemperatureLookUp <= fMaxTemp:
        closestIndex = np.argmin(np.abs(afTemperature - fTemperatureLookUp))
        for ii in range(len(arH2O) - 1):
            if rH2OLookUp >= arH2O[ii] and rH2OLookUp < arH2O[ii + 1]:
                v1 = mfViscosity[closestIndex, ii + 1]
                v2 = mfViscosity[closestIndex, ii]
                a1 = arH2O[ii + 1]
                a2 = arH2O[ii]
                break
    else:
        raise ValueError(
            "IL temperature is out of the range necessary for determining viscosity of the IL based on temperature!"
        )

    fViscosityLookUp = v2 - (rH2OLookUp - a2) * (v2 - v1) / (a1 - a2)

    return fViscosityLookUp
