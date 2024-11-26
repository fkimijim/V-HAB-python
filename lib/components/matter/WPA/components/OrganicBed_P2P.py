class OrganicBed_P2P(matter.procs.p2ps.flow):
    """
    OrganicBed_P2P: A P2P processor that removes big organic compounds
    until the ionic beds are full and experience a breakthrough.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut):
        """
        Initialize the OrganicBed_P2P processor.
        
        :param oStore: The store to which the processor belongs.
        :param sName: Name of the processor.
        :param sPhaseIn: Input phase.
        :param sPhaseOut: Output phase.
        """
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)
        
        # Initialize big organics tracking array
        self.abBigOrganics = [False] * self.oMT.iSubstances
        # Currently only one big organic component is considered: C30H50
        self.abBigOrganics[self.oMT.tiN2I["C30H50"]] = True

    def calculateFlowRate(self, afInsideInFlowRate, aarInsideInPartials, *args):
        """
        Calculate the flow rate for the OrganicBed_P2P processor.
        
        :param afInsideInFlowRate: Array of input flow rates.
        :param aarInsideInPartials: Array of input partial flow rates.
        """
        fFlowRate = 0
        arExtractPartials = [0] * self.oMT.iSubstances

        # Remove big organic compounds unless the ionic beds are nearly full
        if not all(fill_state > 0.99 for fill_state in self.oStore.oContainer.mfCurrentFillState):
            afPartialInFlows = [sum(flow * partial for flow, partial in zip(afInsideInFlowRate, column))
                                for column in zip(*aarInsideInPartials)]

            afPartialFlowsOrganics = [0] * self.oMT.iSubstances
            for i, isBigOrganic in enumerate(self.abBigOrganics):
                if isBigOrganic:
                    afPartialFlowsOrganics[i] = afPartialInFlows[i]

            fFlowRate = sum(afPartialFlowsOrganics)
            if fFlowRate != 0:
                arExtractPartials = [flow / fFlowRate if fFlowRate != 0 else 0 for flow in afPartialFlowsOrganics]

        # Set the calculated flow rate and partials
        self.setMatterProperties(fFlowRate, arExtractPartials)

    def update(self):
        """
        Update method for OrganicBed_P2P (no operations required in this implementation).
        """
        pass
