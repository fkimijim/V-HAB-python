class GrowthMediumChanges:
    """
    GrowthMediumChanges manipulates the growth medium phase content resulting from
    chemical reactions and photosynthesis. Flow rates are calculated from separate
    modules and combined in this class.
    """

    def __init__(self, sName, oPhase):
        """
        Constructor for GrowthMediumChanges.

        :param sName: Name of the manipulator.
        :param oPhase: Phase associated with this manipulator.
        """
        self.sName = sName
        self.oPhase = oPhase

        self.fLastExecTimeStep = 0  # [s]
        self.fTimeStep = 0  # [s]
        self.afMass = []  # [kg], array of current masses of components in the growth medium
        self.afPartialFlowRatesFromPhotosynthesis = []  # [kg/s]
        self.afPartialFlowRatesFromFunctions = []  # [kg/s]

        # Initialize modules
        self.oChemicalReactions = BBMReactions(self)
        try:
            self.oPhotosynthesisModule = self.oPhase.oStore.oContainer.oPhotosynthesisModule
        except AttributeError:
            self.oPhotosynthesisModule = None

    def update(self):
        """
        Update method to handle changes in the growth medium based on photosynthesis
        and chemical reactions.
        """
        # Calculate time steps
        self.fTimeStep = self.oPhase.fTimeStep  # [s], predicted future time step
        self.fLastExecTimeStep = self.oPhase.oTimer.fTime - self.oPhase.oTimer.fLastExec  # [s]

        # Photosynthesis module update
        if self.oPhotosynthesisModule:
            self.afPartialFlowRatesFromPhotosynthesis = self.oPhotosynthesisModule.update(self)  # [kg/s]
        else:
            self.afPartialFlowRatesFromPhotosynthesis = [0] * self.oPhase.oMT.iSubstances

        # Chemical reactions module update
        afPartialFlowRatesFromReactions = self.oChemicalReactions.update(self.fTimeStep)  # [kg/s]

        # Combine flow rates from different modules
        self.afPartialFlowRatesFromFunctions = [
            ps + cr for ps, cr in zip(self.afPartialFlowRatesFromPhotosynthesis, afPartialFlowRatesFromReactions)
        ]

        # Handle compound masses for urine, if applicable
        if self.oPhase.afMass[self.oPhase.oMT.tiN2I.Urine] > 0 and self.oPhase.oMT.abCompound[self.oPhase.oMT.tiN2I.Urine]:
            afCompoundMasses = [0] * self.oPhase.oMT.iSubstances
            afCompoundMasses[self.oPhase.oMT.tiN2I.Urine] = self.oPhase.afMass[self.oPhase.oMT.tiN2I.Urine]
            afResolvedMass = self.oPhase.oMT.resolveCompoundMass(
                afCompoundMasses, self.oPhase.arCompoundMass
            )
            afCompoundFlowRates = [
                (rm / self.fTimeStep - cm / self.fTimeStep)
                for rm, cm in zip(afResolvedMass, afCompoundMasses)
            ]
            self.afPartialFlowRatesFromFunctions = [
                pf + cf for pf, cf in zip(self.afPartialFlowRatesFromFunctions, afCompoundFlowRates)
            ]

        # Set flow rates to return
        if self.fTimeStep > 0:
            afPartialFlowRates = self.afPartialFlowRatesFromFunctions
        else:
            afPartialFlowRates = [0] * self.oPhase.oMT.iSubstances

        # Convert flows to compounds
        aarFlowsToCompound = [[0] * self.oPhase.oMT.iSubstances for _ in range(self.oPhase.oMT.iSubstances)]
        csCompositions = list(self.oPhase.oMT.ttxMatter.Chlorella.trBaseComposition.keys())
        for field in csCompositions:
            aarFlowsToCompound[self.oPhase.oMT.tiN2I.Chlorella][self.oPhase.oMT.tiN2I[field]] = \
                self.oPhase.oMT.ttxMatter.Chlorella.trBaseComposition[field]

        # Validate flow rates
        if abs(sum(afPartialFlowRates)) > 1e-7:
            raise ValueError("Flow rates do not sum to zero.")

        self._update_base(afPartialFlowRates, aarFlowsToCompound)

    def _update_base(self, afPartialFlowRates, aarFlowsToCompound):
        """
        Placeholder for the base class update method.

        :param afPartialFlowRates: Partial flow rates for substances [kg/s].
        :param aarFlowsToCompound: Mapping of flows to compounds.
        """
        # Replace this with actual logic from the base class
        pass


class BBMReactions:
    """
    Placeholder for the BBMReactions module.
    """

    def __init__(self, parent):
        self.parent = parent

    def update(self, time_step):
        """
        Simulates chemical reactions.

        :param time_step: Time step [s].
        :return: Partial flow rates from reactions [kg/s].
        """
        # Replace with actual reaction logic
        return [0] * self.parent.oPhase.oMT.iSubstances
