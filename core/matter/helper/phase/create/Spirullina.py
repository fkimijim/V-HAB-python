def Spirullina(oStore, fVolume, fTemperature=273.15, rRH=0, fPressure=101325):
    """
    Spirullina: Helper function to define a matter phase for Spirullina.

    Parameters:
    - oStore: Object containing the matter table and constants.
    - fVolume: Volume in cubic meters (m³).
    - fTemperature: Temperature in Kelvin (default: 273.15 K).
    - rRH: Relative humidity (default: 0).
    - fPressure: Pressure in Pascals (default: 101325 Pa).

    Returns:
    - cParams: Parameters for constructing the phase.
    - sDefaultPhase: Default phase type ('matter.phases.liquid').
    """
    # Values from @matter.table
    fRm = oStore["oMT"]["Const"]["fUniversalGas"]  # ideal gas constant [J/K]
    fMolarMassCO2 = oStore["oMT"]["afMolarMass"][oStore["oMT"]["tiN2I"]["CO2"]]  # molar mass of CO2 [kg/mol]

    # Calculate mass using ideal gas law: m = (p * V * M) / (R_m * T)
    fMass = fPressure * fVolume * fMolarMassCO2 / (fRm * fTemperature)

    # Matter composition
    tfMass = {"Spirullina": fMass}

    # Check relative humidity - currently not used but can be extended.
    if rRH > 0:
        tfMass["H2O"] = 0

    # Create cParams for constructing the phase
    cParams = [tfMass, fVolume, fTemperature]

    # Default phase type
    sDefaultPhase = "matter.phases.liquid"

    return cParams, sDefaultPhase


# # サンプルデータ
# oStore = {
#     "oMT": {
#         "Const": {"fUniversalGas": 8.314},  # 理想気体定数
#         "afMolarMass": [0.044],            # モル質量の例
#         "tiN2I": {"CO2": 0}                # CO2のインデックス
#     }
# }

# # 関数の呼び出し
# fVolume = 1.0  # m³
# fTemperature = 300  # K
# rRH = 0  # 相対湿度
# fPressure = 101325  # Pa

# cParams, sDefaultPhase = Spirullina(oStore, fVolume, fTemperature, rRH, fPressure)

# print("Parameters:", cParams)
# print("Default Phase:", sDefaultPhase)
