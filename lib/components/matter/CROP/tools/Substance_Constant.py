class Substance_Constant(matter.procs.p2ps.flow):
    """
    The P2P processor to hold the nominal mass level in a phase as described in section 4.2.2.2 in the thesis.
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, csSubstance, afLimit_Level):
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)

        # Cell of substance strings, instead of one substance at a time
        self.csSubstance = csSubstance

        # Array with limit levels for all substances in csSubstance
        self.afLimit_Level = afLimit_Level

        # Array with oMT indices of the substances in csSubstance
        self.aiIndices = [
            self.oMT.tiN2I[substance] for substance in self.csSubstance
        ]

        # The extracting percentage of the substance is set to 1 since
        # it is the only substance to be extracted.
        self.arExtractPartials = [0] * self.oMT.iSubstances

        for substance in self.csSubstance:
            self.arExtractPartials[self.oMT.tiN2I[substance]] = 1 / len(self.csSubstance)

        # Initialize other properties
        self.afMassDifference = [0] * len(self.csSubstance)
        self.fLastExecp2p = 0

    def update(self):
        # The time step of the P2P in each loop
        fTimeStep = self.oTimer.fTime - self.fLastExecp2p

        # To avoid numerical oscillation
        if fTimeStep <= 0.1:
            return

        # Simultaneous mass comparison for all substances
        self.afMassDifference = [
            self.oOut.oPhase.afMass[index] - limit
            for index, limit in zip(self.aiIndices, self.afLimit_Level)
        ]

        # Calculate the mass flow rate of the substance according to
        # the nominal mass level in "self.oOut.oPhase"
        if any(
            self.oOut.oPhase.afMass[self.oMT.tiN2I[substance]] != limit
            for substance, limit in zip(self.csSubstance, self.afLimit_Level)
        ):
            fFlowRate = sum(
                (limit - self.oOut.oPhase.afMass[self.oMT.tiN2I[substance]]) / fTimeStep
                for substance, limit in zip(self.csSubstance, self.afLimit_Level)
            )
        else:
            fFlowRate = 0

        # Hold the nominal mass level by extracting the substance out
        # of the "self.oOut.oPhase" according to the mass flow rate
        self.setMatterProperties(fFlowRate, self.arExtractPartials)

        self.fLastExecp2p = self.oTimer.fTime
