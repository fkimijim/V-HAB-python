import numpy as np

def calculate_pressure(self, *args):
    """
    Calculate pressure based on the provided data.
    This function handles two cases:
    1. When an object (phase, flow, etc.) is provided.
    2. When specific data is directly provided as arguments.

    Parameters:
        args: Variable arguments, either an object or direct data.

    Returns:
        float: The calculated pressure.
    """
    iNumArgs = len(args)

    # Case 1: Object is provided
    if iNumArgs == 1:
        oMatterRef = args[0]

        # Handle matter.phase or matter.flow objects
        if oMatterRef.sObjectType == 'phase':
            sMatterState = oMatterRef.sType
            arPartialMass = oMatterRef.arPartialMass
            oPhase = oMatterRef
            afMass = oPhase.afMass
            fCurrentPressure = oPhase.fPressure

        elif oMatterRef.sObjectType == 'p2p':
            sMatterState = oMatterRef.sType
            arPartialMass = oMatterRef.arPartialMass
            oPhase = oMatterRef.get_in_exme().oPhase
            afMass = oPhase.afMass
            fCurrentPressure = oPhase.fPressure

        elif oMatterRef.sObjectType == 'flow':
            sMatterState = oMatterRef.oBranch.get_in_exme().oPhase.sType
            arPartialMass = oMatterRef.arPartialMass
            if oMatterRef.fFlowRate >= 0:
                oPhase = oMatterRef.oBranch.coExmes[0][0].oPhase
            else:
                oPhase = oMatterRef.oBranch.coExmes[1][0].oPhase
            afMass = oPhase.afMass
            fCurrentPressure = oPhase.fPressure

        else:
            raise ValueError("Single parameter must be of type 'matter.phase' or 'matter.flow'.")

        # Extract temperature and density
        fTemperature = oMatterRef.fTemperature
        fDensity = oMatterRef.fDensity
        if fTemperature is None or np.isnan(fTemperature):
            fTemperature = self.Standard.Temperature

        bUseIsobaricData = True

    else:
        # Case 2: Data is directly provided
        sMatterState = args[0]
        afMass = args[1]
        arPartialMass = afMass / sum(afMass)

        fTemperature = args[2] if iNumArgs > 2 else self.Standard.Temperature
        fDensity = args[3] if iNumArgs > 3 else self.Standard.Density
        fCurrentPressure = args[4] if iNumArgs > 4 else self.Standard.Pressure
        bUseIsobaricData = args[5] if iNumArgs > 5 else True

    # Return 0 if no mass is present
    if sum(arPartialMass) == 0:
        return 0

    aiIndices = [i for i, mass in enumerate(arPartialMass) if mass > 0]
    csPhase = ['solid', 'liquid', 'gas', 'supercritical']

    if sMatterState == 'solid':
        raise ValueError("In V-HAB, solids do not have a pressure.")
    elif sMatterState == 'liquid':
        afPartialDensity = [mass * fDensity for mass in arPartialMass]
        aiPhase = [2] * self.iSubstances
    elif sMatterState == 'gas':
        afPartialDensity = [mass * fDensity for mass in arPartialMass]
        aiPhase = [3] * self.iSubstances
    elif sMatterState == 'mixture':
        afPartialDensity = [mass * fDensity for mass in arPartialMass]
        aiPhase = self.determine_phase(afMass, fTemperature, [fCurrentPressure] * self.iSubstances)

    afPartialDensity = [d if d >= 1e-4 * sum(afPartialDensity) else 0 for d in afPartialDensity]
    aiIndices = [i for i in aiIndices if afPartialDensity[i] > 0]

    afPP = []
    for i in aiIndices:
        tParameters = {
            'sSubstance': self.csSubstances[i],
            'sProperty': 'Pressure',
            'sFirstDepName': 'Temperature',
            'fFirstDepValue': fTemperature,
            'sPhaseType': csPhase[aiPhase[i] - 1],
            'sSecondDepName': 'Density',
            'fSecondDepValue': afPartialDensity[i],
            'bUseIsobaricData': bUseIsobaricData,
        }
        if self.ttxMatter[tParameters['sSubstance']].bIndividualFile:
            afPP.append(self.find_property(tParameters))
        else:
            afPP.append(self.Standard.Pressure)

    if any(np.isnan(pp) for pp in afPP):
        raise ValueError("Invalid entries in partial pressure vector.")

    if any(pp < 0 for pp in afPP):
        raise ValueError("Negative partial pressure values are invalid.")

    return sum(afPP)
