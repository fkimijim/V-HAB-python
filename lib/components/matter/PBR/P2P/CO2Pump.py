class CO2Pump(matter.procs.p2ps.stationary):
    """
    CO2Pump moves CO2 from the cabin air interface into the high CO2 content
    chamber of the PBR that supplies the algae.
    """

    def __init__(self, oStore, sName, sExmePhaseIntoP2P, sExmePhaseOutofP2P, oSystem):
        super().__init__(oStore, sName, sExmePhaseIntoP2P, sExmePhaseOutofP2P)
        self.oSystem = oSystem

        # Control parameters
        self.fStartPumpingCO2PP = 59000  # [Pa]
        self.fEndPumpingCO2PP = 60000  # [Pa]
        self.fSeparationFactor = 1  # [-] efficiency of CO2 separation
        self.bPumpActive = False  # Initially set to inactive

        # P2P-relevant properties
        self.arExtractPartials = [0] * self.oMT.iSubstances
        self.arExtractPartials[self.oMT.tiN2I.CO2] = 1  # Define extraction for CO2

    def update(self):
        """
        Update the flow rate based on current CO2 partial pressure and control logic.
        """
        self.fCurrentPP = self.oOut.oPhase.afPP[self.oMT.tiN2I.CO2]

        # Hysteresis behavior: activate pump below start partial pressure, deactivate above end partial pressure
        if self.fCurrentPP < self.fStartPumpingCO2PP:
            self.bPumpActive = True
        elif self.fCurrentPP > self.fEndPumpingCO2PP:
            self.bPumpActive = False

        if self.bPumpActive:
            afFlowRate, mrPartials = self.getInFlows()

            # Element-wise multiplication to calculate CO2 mass flow
            afCO2InFlows = [flow * mrPartials[i][self.oMT.tiN2I.CO2] for i, flow in enumerate(afFlowRate)]

            fFlowRate = sum(afCO2InFlows) * self.fSeparationFactor  # [kg/s]
        else:
            fFlowRate = 0

        # Set flow rate and update matter properties
        self.setMatterProperties(fFlowRate, self.arExtractPartials)
