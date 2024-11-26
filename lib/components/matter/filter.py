class Filter(matter.store):
    """
    Generic filter model
    This filter is modeled as a store with two phases: a flow volume phase and a filter material phase.
    These phases are connected by two phase-to-phase (p2p) processors:
    - Sorption processor (filterproc_sorp): handles sorption processes and flows.
    - Desorption processor (filterproc_deso): handles potential desorption flows.
    """

    def __init__(self, oParentSys, sName, sType, tParameters):
        """
        Constructor for the Filter class.

        :param oParentSys: Parent system.
        :param sName: Name of the filter.
        :param sType: Type of the filter ('FBA', 'RCA', 'MetOx').
        :param tParameters: Dictionary containing optional parameters:
            - fTimeStep: Fixed time step for phases.
            - sAtmosphereHelper: Helper for atmosphere settings.
            - tGeometry: Geometry parameters with 'sShape', dimensions, etc.
            - fFilterTemperature: Initial filter temperature.
            - fFilterPressure: Initial filter pressure.
            - rRelativeHumidity: Initial relative humidity.
        """
        # Initialize superclass
        super().__init__(oParentSys, sName, tParameters.get("tGeometry", {}).get("fVolume", None))

        # Initialize properties
        self.oParentSys = oParentSys
        self.sType = sType
        self.rVoidFraction = None
        self.fx = None
        self.fy = None
        self.fz = None
        self.oProc_sorp = None
        self.oProc_deso = None

        # Geometry and volume setup
        tGeometry = tParameters.get("tGeometry", {})
        fVolume = None
        if tGeometry.get("sShape") == "cuboid":
            f_x = tGeometry["fLength"]
            f_y = tGeometry["fWidth"]
            f_z = tGeometry["fHeight"]
            fVolume = f_x * f_y * f_z
        elif tGeometry.get("sShape") == "cylinder":
            fRadius = tGeometry["fRadius"]
            fHeight = tGeometry["fHeight"]
            fVolume = 3.141592653589793 * (fRadius ** 2) * fHeight
        else:
            raise ValueError(f"Unsupported filter shape: {tGeometry.get('sShape')}")

        # Filter type-specific properties
        if sType == "FBA":
            if not fVolume:
                fVolume = 3.141592653589793 * (0.03 ** 2) * 0.3
            rVoidFraction = 0.4
        elif sType == "RCA":
            if not fVolume:
                f_x, f_y, f_z = 0.1692, 0.1097, 0.0586
                fVolume = f_x * f_y * f_z
            rVoidFraction = 0.343
        elif sType == "MetOx":
            if not fVolume:
                f_x, f_y, f_z = 0.1764, 0.1764, 0.1764
                fVolume = f_x * f_y * f_z
            rVoidFraction = 0.510
        else:
            raise ValueError(f"Unsupported filter type: {sType}")

        self.fVolume = fVolume
        self.rVoidFraction = rVoidFraction

        if sType in ["RCA", "MetOx"]:
            self.fx = f_x
            self.fy = f_y
            self.fz = f_z

        # Atmosphere settings
        sAtmosphereHelper = tParameters.get("sAtmosphereHelper", "")
        fTemperature = tParameters.get("fFilterTemperature", self.oMT.Standard.Temperature)
        fPressure = tParameters.get("fFilterPressure", self.oMT.Standard.Pressure)
        rRelativeHumidity = tParameters.get("rRelativeHumidity", 0)

        # Create flow phase
        if sAtmosphereHelper:
            oFlowPhase = self.createPhase(
                sAtmosphereHelper, "FlowPhase", self.fVolume * self.rVoidFraction, fTemperature, rRelativeHumidity, fPressure
            )
        else:
            oFlowPhase = self.createPhase(
                "SuitAtmosphere", "FlowPhase", self.fVolume * self.rVoidFraction, fTemperature, rRelativeHumidity, fPressure
            )

        # Create filtered phase
        tfMass = {"AmineSA9T": self.oMT.ttxMatter.AmineSA9T.ttxPhases.tSolid.Density * self.fVolume * (1 - self.rVoidFraction)}
        matter.phases.mixture(self, "FilteredPhase", "solid", tfMass, fTemperature, fPressure)

        # Set fixed time step
        fFixedTimeStep = tParameters.get("fTimeStep", None)
        if fFixedTimeStep:
            tTimeStepProperties = {"fFixedTimeStep": fFixedTimeStep}
            self.toPhases.FlowPhase.setTimeStepProperties(tTimeStepProperties)
            self.toPhases.FilteredPhase.setTimeStepProperties(tTimeStepProperties)

        # Create exmes for external connections
        matter.procs.exmes.gas(oFlowPhase, "Inlet")
        matter.procs.exmes.gas(oFlowPhase, "Outlet")

        # Create p2p processors
        self.oProc_deso = components.matter.filter.FilterProc_deso(self, "DesorptionProcessor", "FlowPhase", "FilteredPhase")
        if sType == "RCA":
            self.oProc_sorp = components.matter.RCA.RCA_FilterProc_sorp(
                oParentSys, self, "SorptionProcessor", "FlowPhase", "FilteredPhase", sType
            )
        else:
            self.oProc_sorp = components.matter.filter.FilterProc_sorp(
                self, "SorptionProcessor", "FlowPhase", "FilteredPhase", sType
            )

    def setVolume(self):
        """
        Override matter.store setVolume to allocate volumes for flow and filtered phases.
        """
        self.toPhases.FlowPhase.setVolume(self.fVolume * self.rVoidFraction)
        # Uncomment the following line if needed:
        # self.toPhases.FilteredPhase.setVolume(self.fVolume * (1 - self.rVoidFraction))
