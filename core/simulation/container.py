class Container:
    """
    Base class for simulation models.
    This is the basic container class which provides the general framework
    for models to be created. It serves as the root system for each simulation.
    """

    def __init__(self, sName, oTimer, oMT, oCfgParams=None, tSolverParams=None):
        """
        Constructor for the Container class.

        Parameters:
        - sName: Name of the container.
        - oTimer: Global timer object.
        - oMT: Global/unique matter table.
        - oCfgParams: Configuration object for vsys (optional).
        - tSolverParams: Global solver tuning parameters (optional).
        """
        self.sName = sName  # Name of the container
        self.oTimer = oTimer  # Global timer object
        self.oMT = oMT  # Global matter table
        self.oCfgParams = oCfgParams  # Configuration parameters for vsys

        # Default solver tuning parameters
        self.tSolverParams = {
            "rUpdateFrequency": 1,
            "rHighestMaxChangeDecrease": 0,
            "rSolverDampening": 1,
            "fMaxTimeStep": 20,
            "fSolverSensitivity": 5,
        }

        # Merge provided solver parameters with the defaults, if applicable
        if tSolverParams:
            self.tSolverParams.update(tSolverParams)
