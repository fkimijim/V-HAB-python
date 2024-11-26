class Filter_F2F(matter.procs.f2f):
    """
    A filter model for face-to-face (F2F) flow with a friction factor.
    """

    def __init__(self, oContainer, sName, fFrictionFactor):
        """
        Constructor for the Filter_F2F class.

        Parameters:
        - oContainer: The container to which this filter belongs.
        - sName: The name of the filter.
        - fFrictionFactor: Friction factor for the filter.
        """
        super().__init__(oContainer, sName)
        self.fFrictionFactor = fFrictionFactor

        # Support solvers
        self.supportSolver("callback", self.solverDeltas)
        self.supportSolver("manual", False)

    def solverDeltas(self, fFlowRate):
        """
        Update function for the callback solver to calculate pressure drop.

        Parameters:
        - fFlowRate: The current flow rate through the filter.

        Returns:
        - fDeltaPressure: The pressure drop across the filter.
        """
        fDeltaPressure = fFlowRate**2 * self.fFrictionFactor
        self.fDeltaPressure = fDeltaPressure
        return fDeltaPressure
