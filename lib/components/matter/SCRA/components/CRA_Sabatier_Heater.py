class CRA_Sabatier_Heater:
    """
    This heater calculates the heat flow required to keep both Sabatier reactors
    at a constant temperature. It is specific to this system and requires changes
    for use in other systems.
    """

    def __init__(self, oContainer, sName):
        self.oContainer = oContainer
        self.sName = sName
        self.fDeltaTemp = 0  # Temperature difference created by the component [K]
        self.fDeltaPress = 0  # Pressure difference created by the component [Pa]
        self.fHeatFlow = 0  # Heat flow in the system [W]

    def thermal_update(self):
        """
        Trigger a thermal update.
        """
        self.update_manual_solver()

    def update_manual_solver(self):
        """
        Updates the heat flow and temperature difference for the heater.
        """
        try:
            # Attempt to get the flows for this process
            flow1, flow2 = self.get_flows()
        except Exception:
            # If flows are not available, reset heat flow and delta temp to zero
            self.fHeatFlow = 0
            self.fDeltaTemp = 0
            return

        # Determine the inlet flow based on the flow rate
        in_flow = flow1 if flow1.fFlowRate > 0 else flow2

        # Heat flow produced by the Sabatier reactor
        fHeatFlowProducedSabatier = self.oContainer.toStores.CRA_Sabatier.aoPhases[0][0].toManips.substance.fHeatFlowProduced
        # Heat flow required to maintain the temperature of the Sabatier reactor
        fHeatFlowUpkeepSabatier = self.oContainer.toStores.CRA_Sabatier.aoPhases[0][0].oCapacity.toHeatSources.Sabatier_Constant_Temperature.fHeatFlow

        # Heat flow required for cooling air to maintain constant temperature for both reactors
        self.fHeatFlow = fHeatFlowProducedSabatier - fHeatFlowUpkeepSabatier

        # Calculate outlet temperature
        fTemperatureOut = (self.fHeatFlow / (in_flow.fFlowRate * in_flow.fSpecificHeatCapacity)) + in_flow.fTemperature

        # Update temperature difference
        self.fDeltaTemp = fTemperatureOut - in_flow.fTemperature

    def get_flows(self):
        """
        Retrieve the flows associated with this process.
        Placeholder method; actual implementation depends on system context.
        """
        # Example:
        # return self.oContainer.get_flows_for_proc(self.sName)
        raise NotImplementedError("get_flows method must be implemented.")
