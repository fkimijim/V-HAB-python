def gas(oStore, fVolume, tfPartialPressure, fTemperature=None, rRelativeHumidity=0):
    """
    Helper to create a gas matter phase by defining the partial pressures of the components and the temperature.

    Parameters:
    - oStore: Store containing the matter table and constants.
    - fVolume: Volume in cubic meters (m³).
    - tfPartialPressure: Dictionary containing the partial pressures in Pa for the substances.
                         Example: {'N2': 8e4, 'O2': 2e4} for a gas phase with 0.2 bar O2 and 0.8 bar N2.
    - fTemperature: Temperature in Kelvin (default: 288.15 K).
    - rRelativeHumidity: Relative humidity as a ratio (default: 0, max: 1).

    Returns:
    - cParams: Parameters for constructing a gas phase.
    - sDefaultPhase: Default phase type ('matter.phases.gas').
    """

    # Values from @matter.table
    fRm = oStore["oMT"]["Const"]["fUniversalGas"]  # Ideal gas constant [J/K]

    # Default values for temperature and relative humidity
    if fTemperature is None:
        fTemperature = oStore["oMT"]["Standard"]["Temperature"]  # Default: 288.15 K

    # Initialize partial pressure vector
    mfPartialPressure = [0] * oStore["oMT"]["iSubstances"]
    csSubstances = tfPartialPressure.keys()

    # Create the partial pressure vector from the input dictionary
    for substance in csSubstances:
        mfPartialPressure[oStore["oMT"]["tiN2I"][substance]] = tfPartialPressure[substance]

    # If relative humidity is defined, calculate and add the partial pressure of water
    if rRelativeHumidity > 0:
        fSaturationVaporPressureWater = oStore["oMT"]["calculateVaporPressure"](fTemperature, "H2O")
        mfPartialPressure[oStore["oMT"]["tiN2I"]["H2O"]] = rRelativeHumidity * fSaturationVaporPressureWater

    # Find indices of substances with non-zero partial pressures
    aiIndices = [i for i, pressure in enumerate(mfPartialPressure) if pressure > 0]

    # Calculate masses using the ideal gas law or other methods
    if sum(mfPartialPressure) < oStore["oContainer"]["fMaxIdealGasLawPressure"]:
        # Ideal gas law: m = (p * V) / (R / M * T)
        afMass = [
            (mfPartialPressure[i] * fVolume) / ((fRm / oStore["oMT"]["afMolarMass"][i]) * fTemperature)
            for i in range(len(mfPartialPressure))
        ]
    else:
        # Calculate density for each substance and compute mass
        afRho = [0] * len(aiIndices)
        for idx, iIndex in enumerate(aiIndices):
            # Generate parameters for findProperty
            tParameters = {
                "sSubstance": oStore["oMT"]["csSubstances"][iIndex],
                "sProperty": "Density",
                "sFirstDepName": "Temperature",
                "fFirstDepValue": fTemperature,
                "sPhaseType": "gas",
                "sSecondDepName": "Pressure",
                "fSecondDepValue": mfPartialPressure[iIndex],
                "bUseIsobaricData": True,
            }
            # Call findProperty
            afRho[idx] = oStore["oMT"]["findProperty"](tParameters)
        # Calculate masses
        afMass = [0] * oStore["oMT"]["iSubstances"]
        for idx, iIndex in enumerate(aiIndices):
            afMass[iIndex] = afRho[idx] * fVolume

    # Define the mass struct
    tfMass = {}
    for iIndex in aiIndices:
        tfMass[oStore["oMT"]["csSubstances"][iIndex]] = afMass[iIndex]

    # Create parameters for constructing the gas phase
    cParams = [tfMass, fVolume, fTemperature]

    # Default phase type
    sDefaultPhase = "matter.phases.gas"

    return cParams, sDefaultPhase



# # サンプルデータ
# oStore = {
#     "oMT": {
#         "Const": {"fUniversalGas": 8.314472},
#         "afMolarMass": [0.0280134, 0.0319988, 0.039948, 0.04401, 0.01801528],  # Example molar masses: N2, O2, Ar, CO2, H2O
#         "tiN2I": {"N2": 0, "O2": 1, "Ar": 2, "CO2": 3, "H2O": 4},
#         "csSubstances": ["N2", "O2", "Ar", "CO2", "H2O"],
#         "Standard": {"Temperature": 288.15, "Pressure": 101325},
#         "calculateVaporPressure": lambda T, _: 2339.9,  # Example implementation for water vapor pressure
#         "findProperty": lambda params: 1.225,  # Dummy density
#     },
#     "oContainer": {"fMaxIdealGasLawPressure": 1e7},  # Example limit
# }

# # 関数呼び出し
# tfPartialPressure = {"N2": 8e4, "O2": 2e4}  # Partial pressures in Pa
# cParams, sDefaultPhase = gas(oStore, 1.0, tfPartialPressure, 300, 0.5)
# print("Parameters:", cParams)
# print("Default Phase:", sDefaultPhase)
