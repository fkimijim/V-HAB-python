import Flow
import math

Flow = Flow()

class Gas(Flow):
    """
    Gas flow node class

    A gas phase modeled as containing no matter. For implementation purposes,
    the phase does have a mass, but calculations enforce zero mass change for 
    the phase and calculate all values based on the inflows.
    """

    sType = 'gas'

    def __init__(self, oStore, sName, tfMasses, fVolume, fTemperature):
        """
        Initializes the gas flow node.

        Args:
            oStore (str): Name of parent store.
            sName (str): Name of phase.
            tfMasses (dict): Dictionary containing mass value for each species.
            fVolume (float): Informative value, not used in calculations.
            fTemperature (float): Temperature of matter in phase.
        """
        super().__init__(oStore, sName, tfMasses, fVolume, fTemperature)

        self.fVirtualPressure = (
            self.fMass * self.oMT.Const.fUniversalGas * self.fTemperature /
            (self.fMolarMass * self.fVolume)
        )

    @property
    def afPP(self):
        if self.oMultiBranchSolver.bUpdateInProgress:
            raise Exception(
                f"Unsafe access to afPP during multi-branch solver iteration in phase {self.sName}. "
                "Use the appropriate matter.flow object."
            )
        else:
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
                sum(mass_flow) / molar_mass for mass_flow, molar_mass in
                zip(zip(*afPartialMassFlow_In), self.oMT.afMolarMass)
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
        else:
            if self.afPP[self.oMT.tiN2I.H2O]:
                fSaturationVapourPressure = self.oMT.calculateVaporPressure(
                    self.fTemperature, 'H2O'
                )
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
        else:
            return self.oMT.calculatePartsPerMillion(self)
