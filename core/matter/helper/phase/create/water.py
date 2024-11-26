def water(oStore, fVolume, fTemperature=293.15, fPressure=28300):
    """
    Helper to create a water phase.

    Parameters:
    - oStore: Object containing the matter table (oMT).
    - fVolume: Volume in cubic meters (m³).
    - fTemperature: Temperature in Kelvin (default: 293.15 K).
    - fPressure: Pressure in Pascals (default: 28300 Pa).

    Returns:
    - cParams: Parameters for constructing the water phase.
    - sDefaultPhase: Default phase type ('matter.phases.liquid').
    """
    # Prepare parameters for density calculation
    tParameters = {
        "sSubstance": "H2O",
        "sProperty": "Density",
        "sFirstDepName": "Temperature",
        "fFirstDepValue": fTemperature,
        "sPhaseType": "liquid",
        "sSecondDepName": "Pressure",
        "fSecondDepValue": fPressure,
        "bUseIsobaricData": True,
    }

    # Calculate density using the provided method
    fDensity = oStore.oMT.findProperty(tParameters)

    # Calculate mass
    fMass = fDensity * fVolume

    # Define matter composition
    tfMass = {
        "H2O": fMass,
    }

    # Construct parameters for phase creation
    cParams = [tfMass, fTemperature, fPressure]

    # Default class for the phase
    sDefaultPhase = "matter.phases.liquid"

    return cParams, sDefaultPhase
