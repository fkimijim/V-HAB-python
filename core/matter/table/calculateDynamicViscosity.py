def calculateDynamicViscosity(self, *args):
    """
    CALCULATEDYNAMICVISCOSITY Calculates the dynamic viscosity of the matter in a phase or flow.
    Calculates the dynamic viscosity of the matter inside a phase or the matter
    flowing through a flow object. This is done by adding the single
    substance viscosities at the current temperature and pressure and
    weighing them with their mass fraction. Can use either a phase object
    as input parameter or the phase type (sType) and the masses array
    (afMass). Optionally, temperature and pressure can be passed as third
    and fourth parameters, respectively.

    Examples:
        fEta = calculateDynamicViscosity(oFlow)
        fEta = calculateDynamicViscosity(oPhase)
        fEta = calculateDynamicViscosity(sType, afMass, fTemperature, afPartialPressures)

    Returns:
        fEta (float): Dynamic viscosity of matter in the current state in kg/ms.
    """
    (
        fTemperature,
        arPartialMass,
        csPhase,
        aiPhase,
        aiIndices,
        afPartialPressures,
        _,
        _,
        bUseIsobaricData,
    ) = self.getNecessaryParameters(*args)

    # Decision logic for alternative calculations could be placed here
    # (see calculateDensity for an example)

    fEta = self.calculateProperty(
        "Dynamic Viscosity",
        fTemperature,
        arPartialMass,
        csPhase,
        aiPhase,
        aiIndices,
        afPartialPressures,
        bUseIsobaricData,
    )

    return fEta
