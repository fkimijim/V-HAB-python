def calculate_parts_per_million(self, *args):
    """
    Calculates parts per million (ppm) for gas phases and flows.

    Parameters:
        *args:
            - If one argument is provided:
                - matter.phase or matter.flow object
            - If multiple arguments are provided:
                1. Phase type (string): 'gas', 'liquid', or 'solid'
                2. Substance masses (list of floats): masses of each substance
                3. Pressure (float, optional): phase pressure (Pa)

    Returns:
        list: Parts per million (ppm) for each substance.
    """
    if len(args) == 1:
        obj = args[0]
        b_isa_matter_phase = obj.sObjectType == 'phase'
        b_isa_matter_flow = obj.sObjectType == 'flow'

        if not (b_isa_matter_phase or b_isa_matter_flow):
            raise ValueError("If only one argument is provided, it must be a matter.phase or matter.flow object.")

        # Initialize attributes from input object
        if b_isa_matter_phase:
            afMass = obj.afMass
        elif b_isa_matter_flow:
            afMass = obj.arPartialMass

        if b_isa_matter_phase:
            fPressure = obj.fMass * obj.fMassToPressure
        else:
            fPressure = obj.fPressure

        if fPressure is None or not fPressure:  # Check for None or zero
            fPressure = self.Standard['Pressure']

        if fPressure == 0:
            return [0] * self.iSubstances

        try:
            afPartsPerMillion = (afMass * obj.fMolarMass) / (self.afMolarMass * obj.fMass) * 1e6
        except AttributeError:
            afPartsPerMillion = (afMass * self.calculate_molar_mass(afMass)) / (self.afMolarMass * sum(afMass)) * 1e6

    else:
        # Case with explicit matter data provided
        sPhase = args[0]
        afMass = args[1]

        fPressure = args[2] if len(args) > 2 else self.Standard['Pressure']

        if sPhase != 'gas':
            raise ValueError("Parts per million can only be calculated for gases!")

        if fPressure == 0:
            return [0] * self.iSubstances

        afPartsPerMillion = (afMass * self.calculate_molar_mass(afMass)) / (self.afMolarMass * sum(afMass)) * 1e6

    return afPartsPerMillion
