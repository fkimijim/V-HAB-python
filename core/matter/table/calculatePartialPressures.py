def calculate_partial_pressures(self, *args):
    """
    Calculates partial pressures of gas phases and flows.

    Parameters:
        *args:
            - If one argument is provided, it must be a matter.phase or matter.flow object.
            - If multiple arguments are provided:
                1. Phase type (string): 'gas', 'liquid', or 'solid'
                2. Substance masses (list of floats): masses of each substance
                3. Pressure (float, optional): phase pressure (Pa)
                4. Temperature (float, optional): phase temperature (K)

    Returns:
        list: Partial pressures for each substance in Pa.
    """
    if len(args) == 1:
        obj = args[0]

        # Determine phase or flow type
        if obj.sObjectType == 'phase':
            if obj.sType == 'gas':
                sPhase = obj.sType
                bIsMixture = False
            elif obj.sType == 'mixture':
                sPhase = obj.sPhaseType
                bIsMixture = True
            else:
                raise ValueError("Unsupported phase type.")

            afMass = obj.afMass
            if obj.bFlow:
                fPressure = obj.fVirtualPressure
            else:
                fPressure = obj.fMass * obj.fMassToPressure

        elif obj.sObjectType in ['flow', 'p2p']:
            oFlow = obj
            afMols = oFlow.arPartialMass / self.afMolarMass
            fGasAmount = sum(afMols)

            if fGasAmount == 0:
                return [0] * self.iSubstances

            arFractions = afMols / fGasAmount
            afPartialPressures = arFractions * oFlow.fPressure
            return afPartialPressures

        else:
            raise ValueError("If only one argument is provided, it must be a matter.phase or matter.flow object.")

        fTemperature = obj.fTemperature

        if fPressure is None or fPressure != fPressure:  # Check for NaN
            fPressure = self.Standard['Pressure']
            fTemperature = self.Standard['Temperature']

        if fPressure == 0:
            return [0] * len(afMass)

    else:
        # Case with explicit matter data provided
        sPhase = args[0]
        afMass = args[1]
        bIsMixture = False

        fPressure = args[2] if len(args) > 2 else self.Standard['Pressure']
        fTemperature = args[3] if len(args) > 3 else self.Standard['Temperature']

    # Ensure phase is gas
    if sPhase != 'gas':
        raise ValueError("Partial pressures can only be calculated for gases!")

    # Calculate moles and fractions
    afMols = afMass / self.afMolarMass
    fGasAmount = sum(afMols)

    arFractions = afMols / fGasAmount
    afPartialPressures = arFractions * fPressure

    # Adjust for two-phase systems
    if bIsMixture:
        aiPhases = self.determine_phase(afMass, fTemperature, afPartialPressures)
        miTwoPhaseIndices = [i for i, phase in enumerate(aiPhases) if phase % 1 != 0]
        for iK in miTwoPhaseIndices:
            afPartialPressures[iK] = self.calculate_vapor_pressure(fTemperature, self.csSubstances[iK])

    return afPartialPressures
