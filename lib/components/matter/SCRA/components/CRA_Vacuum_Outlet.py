class CRA_Vacuum_Outlet:
    """
    Represents a vacuum outlet in the system, designed for use with a solver.
    """

    def __init__(self, oContainer, sName):
        """
        Constructor for the CRA_Vacuum_Outlet.

        :param oContainer: The container object to which this outlet belongs.
        :param sName: Name of the outlet.
        """
        self.oContainer = oContainer
        self.sName = sName
        self.bFlowRateDependPressureDrop = False  # Indicates no pressure drop dependence on flow rate.
        self.fDeltaPressure = 0  # Default pressure difference.

        self.supported_solvers = {
            "callback": self.solverDeltas,
            "manual": False
        }

    def solverDeltas(self, _):
        """
        Update function for the callback solver.

        :param _: Placeholder for solver parameters.
        :return: Fixed pressure difference for the vacuum outlet.
        """
        fDeltaPressure = 9e4  # Fixed pressure difference for the vacuum outlet.
        self.fDeltaPressure = fDeltaPressure
        return fDeltaPressure

    def supportSolver(self, solver_type, handler):
        """
        Register a solver type and its associated handler.

        :param solver_type: Type of solver (e.g., "callback" or "manual").
        :param handler: Associated handler or flag for the solver type.
        """
        self.supported_solvers[solver_type] = handler
