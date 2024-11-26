class GasExme:
    """
    GAS: An ExMe (External Mass Exchange) that interfaces with a gaseous phase.
    The main purpose of this class is to provide the method `get_flow_data()`
    which returns the pressure and temperature of the attached phase.
    """

    def __init__(self, oPhase, sName):
        """
        Gas ExMe class constructor.
        
        Parameters:
        oPhase: The phase the ExMe is attached to.
        sName: The name of the processor.
        """
        super().__init__(oPhase, sName)
        self.oPhase = oPhase
        self.sName = sName
        self.iSign = None  # Assuming `iSign` is set externally

    def get_flow_data(self, fFlowRate=None):
        """
        Get flow data for the ExMe.

        Parameters:
        fFlowRate: Optional. Current mass flow rate in kg/s. If not provided,
                   it will use the flow rate of the connected flow.

        Returns:
        fFlowRate: Current mass flow rate in kg/s with respect to the connected phase
                   (negative values mean the mass of `self.oPhase` is being reduced).
        arPartials: A list of partial mass ratios for each substance in the current flow rate.
                    The sum of this list is 1, and multiplying it with `fFlowRate` gives
                    the partial mass flow rates for each substance.
        afProperties: A list with two entries: the flow temperature and the flow specific heat capacity.
        arCompoundMass: A list containing the compound masses in the flow.
        """
        # If fFlowRate is provided, apply the ExMe's sign. Otherwise, use the connected flow rate.
        if fFlowRate is not None:
            fFlowRate = fFlowRate * self.iSign
        else:
            fFlowRate = self.oFlow.fFlowRate * self.iSign

        # Get the properties from the connected flow
        arPartials = self.oFlow.arPartialMass
        afProperties = [self.oFlow.fTemperature, self.oFlow.fSpecificHeatCapacity]
        arCompoundMass = self.oFlow.arCompoundMass

        return fFlowRate, arPartials, afProperties, arCompoundMass
