class ConvectiveConductorPlate(thermal_procs_conductors_convective):
    """
    A convective conductor to model convective heat transfer between a fluid 
    flowing along a plate and the plate wall.
    """

    def __init__(self, oContainer, sName, oMassBranch, iFlow, fBroadness, fLength, fFlowArea):
        """
        Constructor for ConvectiveConductorPlate.

        Args:
            oContainer: The system in which the conductor is placed.
            sName: A unique name for the conductor within oContainer.
            oMassBranch: The matter branch modeling the mass flow along the plate.
            iFlow: The index of the flow within the branch for this conductor.
            fBroadness: The broadness of the plate [m].
            fLength: The length of the plate [m].
            fFlowArea: The flow area perpendicular to the flow [m^2].
        """
        # Calculate heat transfer area
        fArea = fLength * fBroadness

        # Initialize the superclass
        super().__init__(oContainer, sName, fArea, oMassBranch, iFlow)

        # Store properties
        self.fBroadness = fBroadness
        self.fLength = fLength
        self.fFlowArea = fFlowArea

    def updateHeatTransferCoefficient(self, _):
        """
        Update the heat transfer coefficient of this conductor.

        This method is triggered when the mass branch calculates a new flow rate, 
        ensuring the correct heat transfer coefficient is always used.

        Returns:
            float: Heat transfer coefficient [W/K].
        """
        # Get the corresponding flow from the associated mass branch
        oFlow = self.oMassBranch.aoFlows[self.iFlow]

        # If flow rate is zero, return zero as the heat transfer coefficient
        if oFlow.fFlowRate == 0:
            return 0
        else:
            # Calculate matter properties
            fDensity = self.oMT.calculateDensity(oFlow)
            fDynamicViscosity = self.oMT.calculateDynamicViscosity(oFlow)
            fThermalConductivity = self.oMT.calculateThermalConductivity(oFlow)
            fSpecificHeatCapacity = self.oMT.calculateSpecificHeatCapacity(oFlow)

            # Calculate the current flow speed
            fFlowSpeed = (oFlow.fFlowRate / fDensity) / self.fFlowArea

            # Calculate the convective heat transfer coefficient for a plate
            fConvection_alpha = functions.calculateHeatTransferCoefficient.convectionPlate(
                self.fLength,
                fFlowSpeed,
                fDynamicViscosity,
                fDensity,
                fThermalConductivity,
                fSpecificHeatCapacity,
            )

            # Return the thermal conductivity of the connection [W/m^2 K]
            return fConvection_alpha
