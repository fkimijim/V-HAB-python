def air(oStore, fVolume, fTemperature=None, rRH=0, fPressure=None):
    """
    Helper function to create an air matter phase.
    If only volume is given, it defaults to ICAO International Standard Atmosphere:
    101325 Pa, 15°C, and 0% relative humidity.

    Parameters:
    - oStore: Store containing the matter table and constants.
    - fVolume: Volume in cubic meters (m³).
    - fTemperature: Temperature in Kelvin (default: 288.15 K).
    - rRH: Relative humidity (default: 0, range: 0 to 1).
    - fPressure: Pressure in Pascals (default: 101325 Pa).

    Returns:
    - cParams: Parameters for constructing a gas phase.
    - sDefaultPhase: Default phase type ('matter.phases.gas').
    """

    # Default values for constants
    fMolarMassAir = 0.029088  # [kg/mol], molar mass of air

    # Values from @matter.table
    fRm = oStore["oMT"]["Const"]["fUniversalGas"]  # Ideal gas constant [J/K]
    fMolarMassH2O = oStore["oMT"]["afMolarMass"][oStore["oMT"]["tiN2I"]["H2O"]]  # Molar mass of water [kg/mol]

    # Default values for arguments
    if fTemperature is None:
        fTemperature = oStore["oMT"]["Standard"]["Temperature"]  # 288.15 K
    if fPressure is None:
        fPressure = oStore["oMT"]["Standard"]["Pressure"]  # 101325 Pa

    if rRH > 0:
        # Calculation of the saturation vapor pressure
        fSaturationVapourPressure = oStore["oMT"]["calculateVaporPressure"](fTemperature, "H2O")

        # Calculate vapor pressure [Pa]
        fVapourPressure = rRH * fSaturationVapourPressure

        # Calculate mass fraction of H2O in air
        fMassFractionH2O = fMolarMassH2O / fMolarMassAir * fVapourPressure / (fPressure - fVapourPressure)

        # Calculate molar fraction of H2O in air
        fMolarFractionH2O = fMassFractionH2O / fMolarMassH2O * fMolarMassAir

        # Calculate total mass
        fTotalMass = (
            fPressure
            * fVolume
            * (fMolarFractionH2O * fMolarMassH2O + (1 - fMolarFractionH2O) * fMolarMassAir)
            / (fRm * fTemperature)
        )

        # Calculate dry air mass
        fDryAirMass = fTotalMass * (1 - fMassFractionH2O)
    else:
        # Dry air calculation
        fDryAirMass = fPressure * fVolume * fMolarMassAir / (fRm * fTemperature)

        # Set water-related values to zero
        fTotalMass = 0
        fMassFractionH2O = 0

    # Matter composition
    tfMass = {
        "N2": 0.75518 * fDryAirMass,
        "O2": 0.23135 * fDryAirMass,
        "Ar": 0.01288 * fDryAirMass,
        "CO2": 0.00058 * fDryAirMass,
    }

    # Add H2O mass if present
    tfMass["H2O"] = fTotalMass * fMassFractionH2O

    # Parameters for a standard gas phase
    cParams = [tfMass, fVolume, fTemperature]

    # Default phase type
    sDefaultPhase = "matter.phases.gas"

    return cParams, sDefaultPhase


# # サンプルデータ
# oStore = {
#     "oMT": {
#         "Const": {"fUniversalGas": 8.314472},
#         "afMolarMass": {"H2O": 0.01801528},
#         "tiN2I": {"H2O": 0},
#         "Standard": {"Temperature": 288.15, "Pressure": 101325},
#         "calculateVaporPressure": lambda T, _: 2339.9,  # ダミー実装
#     }
# }

# # 関数呼び出し
# cParams, sDefaultPhase = air(oStore, fVolume=1.0, fTemperature=300, rRH=0.5, fPressure=101325)
# print("Parameters:", cParams)
# print("Default Phase:", sDefaultPhase)
