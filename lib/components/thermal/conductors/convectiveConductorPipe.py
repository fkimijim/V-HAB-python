class ConvectiveConductorPipe(thermal_procs_conductors_convective):
    """
    A convective conductor to model convective heat transfer between a fluid 
    in a pipe and the pipe wall.
    """

    def __init__(self, oContainer, sName, oMassBranch, iFlow, fHydraulicDiameter, fLength):
        """
        Constructor for ConvectiveConductorPipe.

        Args:
            oContainer: The system in which the conductor is placed.
            sName: A unique name for the conductor within oContainer.
            oMassBranch: The matter branch modeling the mass flow through the pipe.
            iFlow: The index of the flow within the branch for this conductor.
            fHydraulicDiameter: Hydraulic diameter of the pipe [m].
            fLength: Length of the pipe [m].
        """
        # Calculate heat transfer area
        fArea = fLength * 3.14159265359 * fHydraulicDiameter

        # Initialize the superclass
        super().__init__(oContainer, sName, fArea, oMassBranch, iFlow)

        # Store properties
        self.fHydraulicDiameter = fHydraulicDiameter
        self.fLength = fLength

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

        # If flow rate is zero, heat transfer coefficient is zero
        if oFlow.fFlowRate == 0:
            return 0
        else:
            # Calculate the matter properties
            fDensity = self.oMT.calculateDensity(oFlow)
            fDynamicViscosity = self.oMT.calculateDynamicViscosity(oFlow)
            fThermalConductivity = self.oMT.calculateThermalConductivity(oFlow)
            fSpecificHeatCapacity = self.oMT.calculateSpecificHeatCapacity(oFlow)

            # Calculate the current flow speed
            fFlowSpeed = (oFlow.fFlowRate / fDensity) / (0.25 * 3.14159265359 * self.fHydraulicDiameter**2)

            # Calculate the convective heat transfer coefficient using pipe assumption
            fConvection_alpha = functions.calculateHeatTransferCoefficient.convectionPipe(
                self.fHydraulicDiameter,
                self.fLength,
                fFlowSpeed,
                fDynamicViscosity,
                fDensity,
                fThermalConductivity,
                fSpecificHeatCapacity,
                0
            )

            # Return the thermal conductivity of the connection [W/m^2 K]
            return fConvection_alpha
