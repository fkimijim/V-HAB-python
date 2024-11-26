def calculateDensity(self, *args):
    """
    CALCULATEDENSITY Calculates the density of the matter in a phase or flow.
    Calculates the density of the matter inside a phase or the matter
    flowing through a flow object. The density is computed by adding the 
    single substance densities at the current temperature and pressure and 
    weighing them with their mass fraction. Optionally, temperature and 
    partial pressures can be passed as input parameters, or the phase type 
    (sType) and the masses array.

    Examples:
        fDensity = calculateDensity(oFlow)
        fDensity = calculateDensity(oPhase)
        fDensity = calculateDensity(sType, xfMass, fTemperature, afPartialPressures)

    Returns:
        fDensity (float): Density of matter in the current state in kg/m^3.
    """
    (
        fTemperature,
        arPartialMass,
        csPhase,
        aiPhase,
        aiIndices,
        afPartialPressures,
        tbReference,
        sMatterState,
        bUseIsobaricData,
    ) = self.getNecessaryParameters(*args)

    # Check cases where density calculation is unnecessary
    if tbReference["bFlow"]:
        # If the flow rate is 0, use the density of the phase
        if args[0].fFlowRate == 0:
            oPhase = args[0].oBranch.getInEXME().oPhase
            fDensity = getattr(oPhase, "fDensity", None)
            if fDensity is None:
                fDensity = oPhase.fMass / oPhase.fVolume
            return fDensity

    # If the matter state is gaseous and the pressure is not too high,
    # we can use the ideal gas law for faster calculation.
    if sMatterState == "gas":
        if tbReference["bNone"]:
            fPressure = sum(args[3])
            fMolarMass = sum(arPartialMass * self.afMolarMass)
        else:
            fPressure = args[0].fPressure
            fMolarMass = args[0].fMolarMass

        if fPressure < 5e5:  # Ideal gas approximation valid for low pressure
            fDensity = (fPressure * fMolarMass) / (self.Const["fUniversalGas"] * fTemperature)
            return fDensity

    # Use the general property calculation for density
    fDensity = self.calculateProperty(
        "Density",
        fTemperature,
        arPartialMass,
        csPhase,
        aiPhase,
        aiIndices,
        afPartialPressures,
        bUseIsobaricData,
    )
    return fDensity
