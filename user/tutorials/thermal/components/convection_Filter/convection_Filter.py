class ConvectionFilter(thermal.procs.conductors.Convective):
    """
    ConvectionFilter represents a convective conductor instance for a filter.
    """

    def __init__(self, oContainer, sName, fLength, fBroadness, fFlowArea, oMassBranch, iFlow):
        """
        Initialize a convective conductor for a filter.

        Args:
            oContainer: Container for the conductor.
            sName: Name of the conductor.
            fLength: Length of the conductor.
            fBroadness: Broadness of the conductor.
            fFlowArea: Flow area of the conductor.
            oMassBranch: Associated mass branch.
            iFlow: Flow index within the mass branch.
        """
        fArea = fLength * fBroadness
        super().__init__(oContainer, sName, fArea, oMassBranch, iFlow)

        self.fLength = fLength
        self.fBroadness = fBroadness
        self.fFlowArea = fFlowArea

    def update_heat_transfer_coefficient(self, _):
        """
        Update the heat transfer coefficient based on current conditions.

        Args:
            _: Placeholder for any unused arguments.

        Returns:
            The calculated heat transfer coefficient.
        """
        # Get required matter properties
        fDensity = self.oMT.calculate_density(self.oMassBranch.aoFlows[self.iFlow])

        if fDensity == 0:
            return 0

        fSpecificHeatCapacity = self.oMT.calculate_specific_heat_capacity(self.oMassBranch.aoFlows[self.iFlow])
        fThermalConductivity = self.oMT.calculate_thermal_conductivity(self.oMassBranch.aoFlows[self.iFlow])
        fDynViscosity = self.oMT.calculate_dynamic_viscosity(self.oMassBranch.aoFlows[self.iFlow])

        # Calculate the current flow speed
        fFlowSpeed = self.oMassBranch.fFlowRate / (self.fFlowArea * fDensity)

        if fFlowSpeed == 0:
            return 0

        # Calculate heat transfer coefficient using convection plate formula
        return functions.calculate_heat_transfer_coefficient.convection_plate(
            self.fLength, fFlowSpeed, fDynViscosity, fDensity, fThermalConductivity, fSpecificHeatCapacity
        )
