class FanSimple(matter.procs.f2f):
    """
    FAN_SIMPLE Linear, static, RPM-independent fan model.
    Interpolates between max flow rate and max pressure rise.
    Values are taken from AIAA-2012-3460 for a fan running at 4630 RPM.
    """

    def __init__(self, oParent, sName, fMaxDeltaP, bReverse=False):
        """
        Initialize the fan model.

        :param oParent: Parent container
        :param sName: Name of the fan
        :param fMaxDeltaP: Maximum pressure rise in [Pa]
        :param bReverse: If True, reverses the flow direction
        """
        super().__init__(oParent, sName)

        self.fMaxDeltaP = fMaxDeltaP  # Maximum pressure rise
        self.iDir = -1 if bReverse else 1  # Flow direction
        self.bTurnedOn = True  # Whether the fan is turned on

        # Mark the fan as active to indicate it produces a pressure rise
        self.bActive = True

        # Support different solver modes
        self.supportSolver('hydraulic', -1, 1, True, self.update)
        self.supportSolver('callback', self.solverDeltas)
        self.supportSolver('manual', True, self.updateManualSolver)

    def switchOn(self):
        """Turn the fan on."""
        self.bTurnedOn = True
        self.oBranch.setOutdated()

    def switchOff(self):
        """Turn the fan off."""
        self.bTurnedOn = False
        self.oBranch.setOutdated()

    def update(self):
        """
        Update the pressure delta based on the fan state.
        
        :return: The pressure delta produced by the fan
        """
        if self.bTurnedOn:
            self.fDeltaPressure = -1 * self.fMaxDeltaP
        else:
            self.fDeltaPressure = 0
        return self.fDeltaPressure

    def solverDeltas(self, _):
        """
        Calculate the pressure delta for the solver.

        :return: A tuple containing (pressure delta, temperature delta)
        """
        if self.bTurnedOn:
            fDeltaTemp = 0
            fDeltaPressure = -1 * self.fMaxDeltaP
            self.fDeltaPressure = fDeltaPressure
        else:
            fDeltaTemp = 0
            self.fDeltaPressure = 0
            fDeltaPressure = 0
        return fDeltaPressure, fDeltaTemp

    def updateManualSolver(self):
        """
        Manual solver update function.

        :return: The temperature delta
        """
        return self.fDeltaTemperature
