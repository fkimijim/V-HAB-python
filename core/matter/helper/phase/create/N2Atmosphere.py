def N2Atmosphere(oStore, fVolume, fTemperature=293.15, rRH=0, fPressure=28900):
    """
    Helper to create a nitrogen-rich atmosphere for testing purposes.

    Parameters:
    - oStore: Store object containing the matter table and constants.
    - fVolume: Volume in cubic meters (m³).
    - fTemperature: Temperature in Kelvin (default: 293.15 K).
    - rRH: Relative Humidity as a ratio (default: 0, max: 1).
    - fPressure: Pressure in Pascals (default: 28900 Pa).

    Returns:
    - cParams: Parameters for constructing a nitrogen-rich atmosphere phase.
    - sDefaultPhase: Default phase type ('matter.phases.gas').
    """
    # Ideal gas constant [J/K]
    fRm = oStore["oMT"]["Const"]["fUniversalGas"]

    # Molecular mass of water in [kg/mol]
    fMolarMassH2O = oStore["oMT"]["ttxMatter"]["H2O"]["fMolarMass"]

    # Molecular mass of nitrogen in [kg/mol]
    fMolarMassN2 = oStore["oMT"]["ttxMatter"]["N2"]["fMolarMass"]

    if rRH > 0:
        # Calculate saturation vapor pressure
        fSaturationVaporPressure = oStore["oMT"]["calculateVaporPressure"](fTemperature, "H2O")

        # Calculate vapor pressure [Pa]
        fVapourPressure = rRH * fSaturationVaporPressure

        # Calculate mass fraction of H2O in air
        fMassFractionH2O = fMolarMassH2O / fMolarMassN2 * fVapourPressure / (fPressure - fVapourPressure)

        # Calculate molar fraction of H2O in air
        fMolarFractionH2O = fMassFractionH2O / fMolarMassH2O * fMolarMassN2

        # Calculate total mass
        fMassGes = fPressure * fVolume * (fMolarFractionH2O * fMolarMassH2O + (1 - fMolarFractionH2O) * fMolarMassN2) / (fRm * fTemperature)

        # Calculate dry air mass
        fMass = fMassGes * (1 - fMassFractionH2O)

    else:
        fMass = fPressure * fVolume * fMolarMassN2 / (fRm * fTemperature)

        # For dry gas, these are set to zero
        fMassGes = 0
        fMassFractionH2O = 0

    # Matter composition
    tfMass = {"N2": 0.95 * fMass}

    # Calculate H2O mass if present
    tfMass["H2O"] = fMassGes * fMassFractionH2O

    # Parameters for creating the nitrogen-rich atmosphere phase
    cParams = [tfMass, fVolume, fTemperature]

    # Default phase type
    sDefaultPhase = "matter.phases.gas"

    return cParams, sDefaultPhase


# # サンプルデータ
# oStore = {
#     "oMT": {
#         "Const": {"fUniversalGas": 8.314},
#         "ttxMatter": {
#             "H2O": {"fMolarMass": 0.018},
#             "N2": {"fMolarMass": 0.028},
#         },
#         "calculateVaporPressure": lambda T, substance: 2330 if substance == "H2O" else 0,
#     },
# }

# # 関数呼び出し
# cParams, sDefaultPhase = N2Atmosphere(oStore, fVolume=1.0, fTemperature=300, rRH=0.5, fPressure=101325)

# print("Parameters:", cParams)
# print("Default Phase:", sDefaultPhase)
