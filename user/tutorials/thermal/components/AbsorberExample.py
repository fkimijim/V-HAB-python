class AbsorberExample(matter.procs.p2ps.Stationary):
    """
    AbsorberExample: A demonstration of a P2P processor.
    The logic is not based on any specific physical system.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, sSubstance, fCapacity):
        """
        Initialize the absorber.

        Args:
            oStore: The store containing this processor.
            sName: Name of the processor.
            sPhaseIn: Input phase.
            sPhaseOut: Output phase.
            sSubstance: The substance to absorb.
            fCapacity: Maximum absorption capacity (kg).
        """
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)

        self.sSubstance = sSubstance
        self.fCapacity = fCapacity
        self.arExtractPartials = [0] * self.oMT.iSubstances
        self.arExtractPartials[self.oMT.tiN2I[self.sSubstance]] = 1
        self.rLoad = 0

    def update(self):
        """
        Update the P2P processor whenever flow rates change.
        """
        iSpecies = self.oMT.tiN2I[self.sSubstance]
        self.rLoad = self.oOut.oPhase.afMass[iSpecies] / self.fCapacity if self.fCapacity != 0 else 1

        afFlowRate, mrPartials = self.get_in_flows()

        if not afFlowRate:  # No inflow
            self.set_matter_properties(0, self.arExtractPartials)
            return

        afFlowRate = [rate * mrPartials[idx][iSpecies] for idx, rate in enumerate(afFlowRate)]

        fFlowRate = sum(afFlowRate) * math.exp(-self.rLoad)

        if round(fFlowRate, self.oStore.oTimer.iPrecision) == 0:
            fFlowRate = 0

        fFlowRate /= 4  # Reduce the absorption speed arbitrarily

        self.set_matter_properties(fFlowRate, self.arExtractPartials)
