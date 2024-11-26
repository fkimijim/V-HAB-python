def calculateAdiabaticIndex(self, *args):
    """
    CALCULATEADIABATICINDEX Calculates the adiabatic index of matter.
    Calculates the density of the matter inside a phase, flowing through a
    flow object, or based on provided properties. The adiabatic index is 
    defined as the ratio between the isobaric and isochoric specific heat 
    capacities of a gas.

    Examples:
        fAdiabaticIndex = calculateAdiabaticIndex(oFlow)
        fAdiabaticIndex = calculateAdiabaticIndex(oPhase)
        fAdiabaticIndex = calculateAdiabaticIndex(sType, xfMass, fTemperature, afPartialPressures)

    Returns:
        fAdiabaticIndex (float): Adiabatic index of the gas.
    """
    # Getting the parameters for the calculation
    (
        fTemperature,
        arPartialMass,
        csPhase,
        aiPhase,
        aiIndices,
        afPartialPressures,
        *_,
    ) = self.getNecessaryParameters(*args)

    # Calculate the isobaric heat capacity
    bUseIsoBaricData = True
    fIsobaricSpecificHeatCapacity = self.calculateProperty(
        "Heat Capacity",
        fTemperature,
        arPartialMass,
        csPhase,
        aiPhase,
        aiIndices,
        afPartialPressures,
        bUseIsoBaricData,
    )

    # Calculate the isochoric heat capacity
    bUseIsoBaricData = False
    fIsochoricSpecificHeatCapacity = self.calculateProperty(
        "Heat Capacity",
        fTemperature,
        arPartialMass,
        csPhase,
        aiPhase,
        aiIndices,
        afPartialPressures,
        bUseIsoBaricData,
    )

    # Calculate the adiabatic index
    fAdiabaticIndex = fIsobaricSpecificHeatCapacity / fIsochoricSpecificHeatCapacity

    return fAdiabaticIndex
