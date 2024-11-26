class DummyAdsorber(matter.procs.p2ps.stationary):
    """
    DummyAdsorber: An example P2P processor implementation.
    This class demonstrates a p2p processor's functionality for a simplified
    adsorption model.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, sSubstance, fCapacity):
        """
        Initialize the DummyAdsorber.

        Args:
            oStore: The store to which this processor belongs.
            sName: Name of the processor.
            sPhaseIn: Input phase.
            sPhaseOut: Output phase.
            sSubstance: Substance to be absorbed.
            fCapacity: Maximum absorption capacity in kg.
        """
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)

        # Initialize attributes
        self.sSubstance = sSubstance
        self.fCapacity = fCapacity
        self.fMaxAbsorption = 1e-9  # Max absorption rate (not used)
        self.rLoad = 0  # Initial loading ratio

        # Partial extraction for the specified substance
        self.arExtractPartials = [0] * self.oMT.iSubstances
        self.arExtractPartials[self.oMT.tiN2I[self.sSubstance]] = 1

    def update(self):
        """
        Update the absorber behavior whenever a flow rate changes.
        """
        # Get the index of the substance in the matter table
        iSpecies = self.oMT.tiN2I[self.sSubstance]

        # Calculate the current load ratio based on the absorber's mass
        if self.fCapacity == 0:
            self.rLoad = 1
        else:
            self.rLoad = self.oOut.oPhase.afMass[iSpecies] / self.fCapacity

        # If there are no inflows, set flow rate to zero
        afFlowRate, mrPartials = self.getInFlows()
        if not afFlowRate:
            self.setMatterProperties(0, self.arExtractPartials)
            return

        # Calculate the inflowing flow rates for the target species
        afFlowRate = [flow * mrPartial[iSpecies] for flow, mrPartial in zip(afFlowRate, mrPartials)]

        # Adjust the flow rate based on the current load of the filter
        fFlowRate = (1 - self.rLoad) * sum(afFlowRate)

        # Set the matter properties for the absorber
        self.setMatterProperties(fFlowRate, self.arExtractPartials)
