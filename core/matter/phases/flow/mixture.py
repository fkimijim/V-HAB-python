import Flow
import math

Flow = Flow()

class Mixture(Flow):
    """
    Mixture flow node class

    A mixture phase modeled as containing no matter. For implementation purposes,
    the phase does have a mass, but calculations enforce zero mass change for 
    the phase and calculate all values based on the inflows.
    """

    sType = 'mixture'

    def __init__(self, oStore, sName, sPhaseType, tfMass, fTemperature, fPressure=1e5):
        """
        Initializes the mixture flow node.

        Args:
            oStore (str): Name of parent store.
            sName (str): Name of phase.
            sPhaseType (str): Actual phase type of matter ('liquid', 'solid', 'gas').
            tfMass (dict): Dictionary containing mass value for each species.
            fTemperature (float): Temperature of matter in phase.
            fPressure (float): Pressure of the phase (default is 1e5 Pa).
        """
        # Calling the parent constructor with a placeholder volume of 1e-6
        super().__init__(oStore, sName, tfMass, 1e-6, fTemperature)

        self.sPhaseType = sPhaseType
        self.bGasPhase = sPhaseType == 'gas'

        # Setting the pressure
        self.fVirtualPressure = fPressure
        self.update_pressure()

        # Calculating density and volume
        self.fDensity = self.oMT.calculateDensity(self)
        self.fVolume = self.fMass / self.fDensity if self.fDensity else 0

    @property
    def afPP(self):
        if self.oMultiBranchSolver.bUpdateInProgress:
            raise Exception(
                f"Unsafe access to afPP during multi-branch solver iteration in phase {self.sName}. "
                "Use the appropriate matter.flow object."
            )
        if not self.bGasPhase:
            raise ValueError(
                "Invalid access: Partial pressures (afPP) are only available for gas phases."
            )

        afPartialMassFlow_In = [
            [0] * self.oMT.iSubstances for _ in range(self.iProcsEXME)
        ]

        for iExme in range(self.iProcsEXME):
            exme = self.coProcsEXME[iExme]
            fFlowRate = exme.iSign * exme.oFlow.fFlowRate
            if fFlowRate > 0:
                afPartialMassFlow_In[iExme] = [
                    partial * fFlowRate for partial in exme.oFlow.arPartialMass
                ]

        afCurrentMolsIn = [
            sum(mass_flow) / molar_mass
            for mass_flow, molar_mass in zip(zip(*afPartialMassFlow_In), self.oMT.afMolarMass)
        ]
        totalMols = sum(afCurrentMolsIn)
        arFractions = [mol / totalMols for mol in afCurrentMolsIn] if totalMols else [0] * len(afCurrentMolsIn)

        afPartialPressure = [frac * self.fPressure for frac in arFractions]
        afPartialPressure = [max(0, pp if not math.isnan(pp) else 0) for pp in afPartialPressure]

        return afPartialPressure

    @property
    def rRelHumidity(self):
        if self.oMultiBranchSolver.bUpdateInProgress:
            raise Exception(
                f"Unsafe access to rRelHumidity during multi-branch solver iteration in phase {self.sName}. "
                "Use the appropriate matter.flow object."
            )
        if not self.bGasPhase:
            raise ValueError(
                "Invalid access: Relative humidity (rRelHumidity) is only available for gas phases."
            )
        if self.afPP[self.oMT.tiN2I.H2O]:
            fSaturationVapourPressure = self.oMT.calculateVaporPressure(self.fTemperature, 'H2O')
            return self.afPP[self.oMT.tiN2I.H2O] / fSaturationVapourPressure
        else:
            return 0

    @property
    def afPartsPerMillion(self):
        if self.oMultiBranchSolver.bUpdateInProgress:
            raise Exception(
                f"Unsafe access to afPartsPerMillion during multi-branch solver iteration in phase {self.sName}. "
                "Use the appropriate matter.flow object."
            )
        if not self.bGasPhase:
            raise ValueError(
                "Invalid access: Parts per million (afPartsPerMillion) is only available for gas phases."
            )
        return self.oMT.calculatePartsPerMillion(self)
