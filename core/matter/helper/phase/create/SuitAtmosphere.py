def SuitAtmosphere(oStore, fVolume, fTemperature=None, rRH=0, fPressure=28900):
    """
    Creates a matter phase with a standard space suit atmosphere.

    Parameters:
    - oStore: Object containing the matter table and constants.
    - fVolume: Volume in cubic meters (m³).
    - fTemperature: Temperature in Kelvin (default: 293.15 K).
    - rRH: Relative humidity (default: 0, max: 1).
    - fPressure: Pressure in Pascals (default: 28900 Pa).

    Returns:
    - cParams: Parameters for constructing the phase.
    - sDefaultPhase: Default phase type ('matter.phases.gas').
    """
    # Default temperature if not provided
    if fTemperature is None:
        fTemperature = oStore["oMT"]["Standard"]["Temperature"]

    # Constants and values from oStore
    fRm = oStore["oMT"]["Const"]["fUniversalGas"]  # Ideal gas constant [J/K]
    fMolarMassH2O = oStore["oMT"]["ttxMatter"]["H2O"]["fMolarMass"]  # Molar mass of water [kg/mol]
    fMolarMassO2 = oStore["oMT"]["ttxMatter"]["O2"]["fMolarMass"]  # Molar mass of oxygen [kg/mol]

    if rRH > 0:
        # Calculate saturation vapor pressure
        fSaturationVapourPressure = oStore["oMT"]["calculateVaporPressure"](fTemperature, "H2O")
        
        # Calculate vapor pressure [Pa]
        fVapourPressure = rRH * fSaturationVapourPressure

        # Calculate mass fraction of H2O in air
        fMassFractionH2O = (fMolarMassH2O / fMolarMassO2) * (fVapourPressure / (fPressure - fVapourPressure))
        
        # Calculate molar fraction of H2O in air
        fMolarFractionH2O = fMassFractionH2O / fMolarMassH2O * fMolarMassO2

        # Total mass calculation using ideal gas law
        fTotalMass = (
            fPressure
            * fVolume
            * ((fMolarFractionH2O * fMolarMassH2O + (1 - fMolarFractionH2O) * fMolarMassO2))
            / (fRm * fTemperature)
        )

        # Calculate dry air mass
        fDryMass = fTotalMass * (1 - fMassFractionH2O)
    else:
        # Dry atmosphere calculations
        fDryMass = fPressure * fVolume * fMolarMassO2 / (fRm * fTemperature)
        fTotalMass = 0
        fMassFractionH2O = 0

    # Matter composition
    tfMass = {"O2": fDryMass}

    # Add H2O mass if present
    tfMass["H2O"] = fTotalMass * fMassFractionH2O

    # Parameters for constructing the phase
    cParams = [tfMass, fVolume, fTemperature]

    # Default phase type
    sDefaultPhase = "matter.phases.gas"

    return cParams, sDefaultPhase
