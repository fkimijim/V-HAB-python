class CheckValve(matter.procs.f2f):
    """
    A check valve that allows fluid to pass in one direction only and blocks it otherwise.
    Currently works with the multi-branch solver but can be extended for other solvers.
    """

    def __init__(self, oContainer, sName, bReversed=False, fFlowThroughPressureDropCoefficient=0):
        """
        Initialize the check valve.
        
        :param oContainer: Parent container
        :param sName: Name of the valve
        :param bReversed: Whether the flow direction is reversed
        :param fFlowThroughPressureDropCoefficient: Coefficient for calculating pressure drop
        """
        super().__init__(oContainer, sName)

        self.fPressureDrop = 0  # Current Pressure Drop
        self.fFlowThroughPressureDropCoefficient = fFlowThroughPressureDropCoefficient  # Pressure drop coefficient
        self.bReversed = bReversed  # Reversed flow flag
        self.bOpen = True  # Whether the valve is open

        self.bCheckValve = True  # Mark this as a check valve

        self.supportSolver('callback', self.solverDeltas)

    def solverDeltas(self, fFlowRate):
        """
        Calculate the pressure drop based on the flow rate.
        
        :param fFlowRate: Current flow rate through the valve
        :return: Calculated pressure drop
        """
        # Use the existing pressure drop if the solver has not converged
        try:
            if not self.oBranch.oHandler.bFinalLoop:
                return self.fPressureDrop
        except AttributeError:
            pass  # For solvers that are not iterative, always calculate the valve

        # Determine pressure drop based on flow direction and valve state
        if not self.bReversed and fFlowRate <= 0:
            self.fPressureDrop = float('inf')  # Block reverse flow
            self.bOpen = False
        elif self.bReversed and fFlowRate >= 0:
            self.fPressureDrop = float('inf')  # Block forward flow for reversed valve
            self.bOpen = False
        else:
            self.bOpen = True
            self.fPressureDrop = self.fFlowThroughPressureDropCoefficient * fFlowRate**2

        return self.fPressureDrop
