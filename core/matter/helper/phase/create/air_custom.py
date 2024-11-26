def air_custom(oStore, fVolume, trMasses=None, fTemperature=273.15, rRH=0, fPressure=101325):
    """
    Helper function to create an air matter phase.

    If only volume is given, it defaults to ICAO International Standard Atmosphere:
    101325 Pa, 15°C, and 0% relative humidity.

    Parameters:
    - oStore: The store containing the matter table and constants.
    - fVolume: Volume in cubic meters (m³).
    - trMasses: Dictionary containing mass fractions of gases (optional).
    - fTemperature: Temperature in Kelvin (default: 273.15 K).
    - rRH: Relative humidity (default: 0, range: 0 to 1).
    - fPressure: Pressure in Pascals (default: 101325 Pa).

    Returns:
    - cParams: Parameters for constructing a gas phase.
    - sDefaultPhase: Default phase type ('matter.phases.gas').
    """
    # Default values for trMasses
    if trMasses is None:
        trMasses = {}
    if 'O2' not in trMasses:
        trMasses['O2'] = 0.23135
    if 'Ar' not in trMasses:
        trMasses['Ar'] = 0.01288
    if 'CO2' not in trMasses:
        trMasses['CO2'] = 0.00058

    # Calculate N2 mass fraction
    trMasses['N2'] = 1 - trMasses['O2'] - trMasses['Ar'] - trMasses['CO2']

    # Universal gas constant and molar mass of water
    fRm = oStore['oMT']['Const']['fUniversalGas']  # Ideal gas constant [J/K]
    fMolarMassH2O = oStore['oMT']['afMolarMass'][oStore['oMT']['tiN2I']['H2O']]  # Molar mass of water [kg/mol]

    # Initial pseudo mass for molar mass calculation
    afPseudoMasses = [0] * oStore['oMT']['iSubstances']
    for key, value in trMasses.items():
        afPseudoMasses[oStore['oMT']['tiN2I'][key]] = value

    # Initial molar mass
    fMolarMass = oStore['oMT']['calculateMolarMass'](afPseudoMasses)

    # Saturation vapor pressure for water
    fSaturationVapourPressure = oStore['oMT']['calculateVaporPressure'](fTemperature, 'H2O')

    # Calculate vapor pressure
    fVapourPressure = rRH * fSaturationVapourPressure

    fMolarMassNew = float('inf')
    iCounter = 0

    # Iterative correction for molar mass and mass fractions
    while abs(fMolarMass - fMolarMassNew) > 1e-8 and iCounter < 500:
        fMolarMass = fMolarMassNew
        # Update water vapor mass fraction
        trMasses['H2O'] = fMolarMassH2O / fMolarMass * fVapourPressure / (fPressure - fVapourPressure)
        # Update N2 mass fraction
        trMasses['N2'] = 1 - trMasses['O2'] - trMasses['Ar'] - trMasses['CO2'] - trMasses['H2O']

        # Recalculate pseudo masses
        afPseudoMasses = [0] * oStore['oMT']['iSubstances']
        for key, value in trMasses.items():
            afPseudoMasses[oStore['oMT']['tiN2I'][key]] = value

        # Recalculate molar mass
        fMolarMassNew = oStore['oMT']['calculateMolarMass'](afPseudoMasses)
        iCounter += 1

    # Total mass calculation
    fMassGes = fPressure * fVolume * fMolarMass / (fRm * fTemperature)

    # Dry air mass
    fMass = fMassGes * (1 - trMasses['H2O'])

    # Matter composition
    tfMass = {
        'N2': trMasses['N2'] * fMass,
        'O2': trMasses['O2'] * fMass,
        'Ar': trMasses['Ar'] * fMass,
        'CO2': trMasses['CO2'] * fMass,
        'H2O': trMasses['H2O'] * fMass
    }

    # Construct parameters for a standard gas phase
    cParams = [tfMass, fVolume, fTemperature]

    # Default phase type
    sDefaultPhase = 'matter.phases.gas'

    return cParams, sDefaultPhase


# # サンプルデータ
# oStore = {
#     'oMT': {
#         'Const': {'fUniversalGas': 8.314472},
#         'afMolarMass': {'H2O': 0.01801528},
#         'tiN2I': {'N2': 0, 'O2': 1, 'Ar': 2, 'CO2': 3, 'H2O': 4},
#         'iSubstances': 5,
#         'calculateMolarMass': lambda x: sum(x),  # サンプルのダミー実装
#         'calculateVaporPressure': lambda T, _: 2339.9  # サンプルのダミー値
#     }
# }

# # 実行
# cParams, sDefaultPhase = air_custom(oStore, 1.0, fTemperature=293.15, rRH=0.5, fPressure=101325)
# print("Parameters:", cParams)
# print("Default Phase:", sDefaultPhase)
