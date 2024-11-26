class O2Pump(matter.procs.p2ps.stationary):
    """
    O2Pump moves O2 from the high CO2 content chamber of the PBR that supplies
    the algae into the cabin air interface.
    """

    def __init__(self, oStore, sName, sExmePhaseIntoP2P, sExmePhaseOutofP2P, oSystem):
        super().__init__(oStore, sName, sExmePhaseIntoP2P, sExmePhaseOutofP2P)
        self.oSystem = oSystem

        # Control parameters
        self.fStartPumpingO2PP = 6000  # [Pa] start pumping if O2 partial pressure is above this
        self.fEndPumpingO2PP = 4000    # [Pa] stop pumping if O2 partial pressure falls below this
        self.fSeparationFactor = 1     # [-] efficiency of O2 separation, between 0 and 1
        self.bPumpActive = False       # Initially set to inactive

        # P2P-relevant properties
        self.arExtractPartials = [0] * self.oMT.iSubstances
        self.arExtractPartials[self.oMT.tiN2I.O2] = 1  # Define extraction for O2

    def update(self):
        """
        Update the flow rate based on current O2 partial pressure and control logic.
        """
        self.fCurrentPP = self.oOut.oPhase.afPP[self.oMT.tiN2I.O2]

        # Hysteresis behavior for pump activation and deactivation
        if self.fCurrentPP > self.fStartPumpingO2PP:
            self.bPumpActive = True
        elif self.fCurrentPP < self.fEndPumpingO2PP:
            self.bPumpActive = False

        if self.bPumpActive:
            # Get the current mass of O2 in the reactor air
            self.fCurrentMass = self.oSystem.toStores.ReactorAir.toPhases.HighCO2Air.afMass[self.oMT.tiN2I.O2]
            # Calculate flow rate with a 20% reduction over the time step
            fFlowRate = (self.fCurrentMass * self.fSeparationFactor) / (self.oSystem.fTimeStep * 20)
        else:
            fFlowRate = 0

        # Set the flow rate and update the matter properties
        self.setMatterProperties(fFlowRate, self.arExtractPartials)
