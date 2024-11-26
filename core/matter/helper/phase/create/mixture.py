def mixture(oStore, sPhase, fVolume, trMassRatios, fTemperature=293.15, fPressure=28300):
    """
    Helper to create a mixture phase.

    Parameters:
    - oStore: Store containing the matter table and constants.
    - sPhase: The type of phase (e.g., 'mixture').
    - fVolume: Volume in cubic meters (m³).
    - trMassRatios: Dictionary containing the mass ratios of substances.
    - fTemperature: Temperature in Kelvin (default: 293.15 K).
    - fPressure: Pressure in Pascals (default: 28300 Pa).

    Returns:
    - cParams: Parameters for constructing a mixture phase.
    - sDefaultPhase: Default phase type ('matter.phases.mixture').
    """
    # Initialize mass ratios and compound mass matrices
    mrMassRatios = [0] * oStore["oMT"]["iSubstances"]
    csSubstances = trMassRatios.keys()

    arCompoundMass = [[0] * oStore["oMT"]["iSubstances"] for _ in range(oStore["oMT"]["iSubstances"])]

    # Populate the mass ratio vector and compound mass matrix
    for substance in csSubstances:
        iMatterIndexSubstance = oStore["oMT"]["tiN2I"][substance]
        mrMassRatios[iMatterIndexSubstance] = trMassRatios[substance]

        if oStore["oMT"]["abCompound"][iMatterIndexSubstance]:
            trBaseComposition = oStore["oMT"]["ttxMatter"][substance]["trBaseComposition"]
            for entry in trBaseComposition:
                arCompoundMass[iMatterIndexSubstance][oStore["oMT"]["tiN2I"][entry]] = trBaseComposition[entry]

    # Resolve compound mass ratios
    mrResolvedMassRatios = oStore["oMT"]["resolveCompoundMass"](mrMassRatios, arCompoundMass)

    # Calculate overall density
    afPressures = [fPressure] * oStore["oMT"]["iSubstances"]
    fDensity = oStore["oMT"]["calculateDensity"]('mixture', mrResolvedMassRatios, fTemperature, afPressures)

    # Calculate overall mass in the phase
    fMass = fDensity * fVolume

    # Calculate partial masses for the substances
    tfMass = {}
    for substance in csSubstances:
        tfMass[substance] = fMass * trMassRatios[substance]

    # Parameters for constructing the mixture phase
    cParams = [sPhase, tfMass, fTemperature, fPressure]

    # Default phase type
    sDefaultPhase = 'matter.phases.mixture'

    return cParams, sDefaultPhase


# # サンプルデータ
# oStore = {
#     "oMT": {
#         "iSubstances": 5,
#         "tiN2I": {"H2O": 0, "NaCl": 1, "C6H12O6": 2},
#         "abCompound": [False, True, False, False, False],
#         "ttxMatter": {
#             "NaCl": {"trBaseComposition": {"Na": 0.5, "Cl": 0.5}}
#         },
#         "resolveCompoundMass": lambda mrMassRatios, arCompoundMass: [sum(r) for r in arCompoundMass],
#         "calculateDensity": lambda phase, ratios, temp, pressures: 1000,  # Assume density [kg/m³]
#     },
# }

# # 関数呼び出し
# trMassRatios = {"H2O": 0.7, "NaCl": 0.2, "C6H12O6": 0.1}
# cParams, sDefaultPhase = mixture(oStore, "mixture", 1.0, trMassRatios, 300, 101325)

# print("Parameters:", cParams)
# print("Default Phase:", sDefaultPhase)
