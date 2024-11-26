class ThermallyActivePipe(components.matter.pipe):
    """
    ThermallyActivePipe: A pipe which also models the heat flow from the
    expansion/compression within it.
    """

    def __init__(self, oContainer, sName, fLength, fDiameter, fRoughness=0):
        """
        Constructor for ThermallyActivePipe.

        :param oContainer: The container object
        :param sName: Name of the pipe
        :param fLength: Length of the pipe
        :param fDiameter: Diameter of the pipe
        :param fRoughness: Roughness of the pipe, default is 0
        """
        # Call the parent class constructor
        super().__init__(oContainer, sName, fLength, fDiameter, fRoughness)

    def solverDeltas(self, fFlowRate):
        """
        Update function for callback solver.

        :param fFlowRate: Flow rate through the pipe
        :return: Pressure difference (fDeltaPressure)
        """
        # First, use the standard pipe calculation to calculate the pressure difference
        fDeltaPressure = super().solverDeltas(fFlowRate)

        # Select the inflow to use for matter property values
        if fFlowRate >= 0:
            oFlow = self.aoFlows[0]
        else:
            oFlow = self.aoFlows[1]

        # Calculate the Joule-Thomson coefficient in K/Pa
        fJouleThomson = self.oMT.calculateJouleThomson(oFlow)

        # Calculate the heat flow
        # HeatFlow = MassFlow * SpecificHeatCapacity * DeltaTemperature
        # DeltaTemperature = PressureDifference * JouleThomsonCoefficient
        # Since a positive delta pressure from the pipe is handled as a pressure loss,
        # a negative sign for this calculation is required.
        self.fHeatFlow = -abs(fFlowRate) * oFlow.fSpecificHeatCapacity * fJouleThomson * fDeltaPressure

        return fDeltaPressure
