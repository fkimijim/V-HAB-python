class ManualP2P(matter.procs.p2ps.stationary):
    """
    This P2P is designed to function like the manual solver for branches.
    Users can use the `setFlowRate` function to specify desired partial mass
    flow rates (in kg/s) in an array of size `oMT.iSubstances` with zeros
    for unused flow rates.
    """

    def __init__(self, oStore, sName, sPhaseAndPortIn, sPhaseAndPortOut):
        super().__init__(oStore, sName, sPhaseAndPortIn, sPhaseAndPortOut)
        
        self.afFlowRates = [0] * self.oMT.iSubstances
        self.bMassTransferActive = False
        self.fMassTransferStartTime = None
        self.fMassTransferTime = None
        self.fMassTransferFinishTime = None
        
        self.setMassTransferTimeStep = self.oTimer.bind(
            lambda _: self.checkMassTransfer(),
            0,
            {
                'sMethod': 'checkMassTransfer',
                'sDescription': 'The .checkMassTransfer method of a manual P2P',
                'oSrcObj': self
            }
        )
        # Initialize the time step to infinity
        self.setMassTransferTimeStep(float('inf'), True)

    def setFlowRate(self, afPartialFlowRates):
        """
        Set the flow rate for the P2P in kg/s.

        Args:
            afPartialFlowRates (list): Array of partial flow rates for substances.
        """
        if self.bMassTransferActive:
            print('Warning: Currently a mass transfer is in progress')

        self.afFlowRates = afPartialFlowRates

        # Ensure mass updates are triggered for connected phases
        if (
            self.oIn.oPhase.fLastMassUpdate == self.oTimer.fTime and
            self.oOut.oPhase.fLastMassUpdate == self.oTimer.fTime
        ):
            self.update()
        else:
            self.oIn.oPhase.registerMassupdate()
            self.oOut.oPhase.registerMassupdate()

    def setMassTransfer(self, afPartialMasses, fTime):
        """
        Set a specific mass transfer over a given time.

        Args:
            afPartialMasses (list): Array of partial masses for substances (kg).
            fTime (float): Time over which the mass is transferred (s).
        """
        if fTime == 0:
            raise ValueError(
                f"Stop joking, nothing can happen instantly. Manual solver {self.oBranch.sName} was provided 0 time to transfer mass."
            )

        if self.bMassTransferActive:
            print('Warning: Currently a mass transfer is in progress')

        self.bMassTransferActive = True
        self.fMassTransferStartTime = self.oTimer.fTime
        self.fMassTransferTime = fTime
        self.fMassTransferFinishTime = self.oTimer.fTime + fTime

        self.afFlowRates = [mass / fTime for mass in afPartialMasses]

        # Reset the time step
        self.setMassTransferTimeStep(fTime, True)

        # Ensure mass updates are triggered for connected phases
        self.oIn.oPhase.registerMassupdate()
        self.oOut.oPhase.registerMassupdate()

    def checkMassTransfer(self, _):
        """
        Check the status of the ongoing mass transfer and update as necessary.
        """
        if self.bMassTransferActive and self.fMassTransferFinishTime - self.oTimer.fTime < self.oTimer.fMinimumTimeStep:
            self.afFlowRates = [0] * self.oMT.iSubstances
            self.bMassTransferActive = False
            self.setMassTransferTimeStep(float('inf'), True)
            
            # Ensure mass updates are triggered for connected phases
            self.oIn.oPhase.registerMassupdate()
            self.oOut.oPhase.registerMassupdate()
        elif self.bMassTransferActive and self.fMassTransferFinishTime - self.oTimer.fTime > self.oTimer.fMinimumTimeStep:
            # Adjust the time step if the transfer is not yet complete
            fTimeStep = self.fMassTransferFinishTime - self.oTimer.fTime
            self.setMassTransferTimeStep(fTimeStep, True)

    def update(self, _=None):
        """
        Update the P2P flow rates. No additional processing is required here.
        """
        fFlowRate = sum(self.afFlowRates)
        if fFlowRate == 0:
            arPartialFlowRates = [0] * self.oMT.iSubstances
        else:
            arPartialFlowRates = [rate / fFlowRate for rate in self.afFlowRates]

        super().update(fFlowRate, arPartialFlowRates)
