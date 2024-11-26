def solid(oStore, fVolume, trMassRatios, fTemperature=293.15, fPressure=28300):
    """
    Helper to create a solid matter phase.

    Parameters:
    - oStore: Object containing the matter table and constants.
    - fVolume: Volume in cubic meters (m³).
    - trMassRatios: Dictionary containing mass ratios for each substance.
    - fTemperature: Temperature in Kelvin (default: 293.15 K).
    - fPressure: Pressure in Pascals (default: 28300 Pa).

    Returns:
    - cParams: Parameters for constructing the solid phase.
    - sDefaultPhase: Default phase type ('matter.phases.solid').
    """
    import numpy as np

    # Initialize mass ratios vector
    mrMassRatios = np.zeros(oStore["oMT"]["iSubstances"])
    csSubstances = list(trMassRatios.keys())

    # Initialize compound mass array
    arCompoundMass = np.zeros((oStore["oMT"]["iSubstances"], oStore["oMT"]["iSubstances"]))

    # Populate mass ratios and compound mass
    for substance in csSubstances:
        iMatterIndexSubstance = oStore["oMT"]["tiN2I"][substance]
        mrMassRatios[iMatterIndexSubstance] = trMassRatios[substance]

        if oStore["oMT"]["abCompound"][iMatterIndexSubstance]:
            trBaseComposition = oStore["oMT"]["ttxMatter"][substance]["trBaseComposition"]
            for entry, value in trBaseComposition.items():
                arCompoundMass[iMatterIndexSubstance, oStore["oMT"]["tiN2I"][entry]] = value

    # Resolve compound mass ratios
    mrResolvedMassRatios = oStore["oMT"]["resolveCompoundMass"](mrMassRatios, arCompoundMass)

    # Calculate density
    afPressures = np.ones(oStore["oMT"]["iSubstances"]) * fPressure
    fDensity = oStore["oMT"]["calculateDensity"]('solid', mrResolvedMassRatios, fTemperature, afPressures)

    # Calculate total mass
    fMass = fDensity * fVolume

    # Calculate partial masses
    tfMass = {}
    for substance in csSubstances:
        tfMass[substance] = fMass * trMassRatios[substance]

    # Create cParams for a solid matter phase
    cParams = [tfMass, fTemperature, fPressure]

    # Default phase type
    sDefaultPhase = 'matter.phases.solid'

    return cParams, sDefaultPhase


# サンプルデータ
oStore = {
    "oMT": {
        "iSubstances": 5,
        "tiN2I": {"H2O": 0, "CO2": 1, "N2": 2},
        "abCompound": [False, True, False],
        "ttxMatter": {
            "CO2": {
                "trBaseComposition": {"C": 0.273, "O2": 0.727}
            }
        },
        "resolveCompoundMass": lambda mr, ar: mr,  # モック関数
        "calculateDensity": lambda phase, mr, temp, pres: 1000  # モック関数
    }
}

# # パラメータの準備
# fVolume = 1.0  # m³
# trMassRatios = {"H2O": 0.5, "CO2": 0.5}
# fTemperature = 300  # K
# fPressure = 101325  # Pa

# # 関数呼び出し
# cParams, sDefaultPhase = solid(oStore, fVolume, trMassRatios, fTemperature, fPressure)

# print("Parameters:", cParams)
# print("Default Phase:", sDefaultPhase)
