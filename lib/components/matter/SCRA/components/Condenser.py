class Condenser:
    def __init__(self, oMT, sName, fTemperature, rHumiditySetPoint=0.8):
        self.oMT = oMT
        self.sName = sName
        self.fHydrDiam = 1  # Hydraulic diameter (irrelevant for manual solver)
        self.fHydrLength = 0  # Hydraulic length (irrelevant for manual solver)
        self.fDeltaTemp = 0  # Temperature difference created by the component in [K]
        self.fTemperature = fTemperature
        self.fTempChangeHeatFlow = 0
        self.fCondensateFlow = 0
        self.rHumiditySetPoint = rHumiditySetPoint
        self.bActiveTemperatureRegulation = True

        # Solver support (manual and callback)
        self.support_solver_manual = self.update_manual_solver
        self.support_solver_callback = self.solver_deltas

    def recalculate_condenser(self):
        if not self.bActiveTemperatureRegulation:
            self.fTempChangeHeatFlow = 0
        else:
            try:
                # Get flows and determine the inflow
                Flow1, Flow2 = self.get_flows()
                in_flow = Flow1 if Flow1.fFlowRate > 0 else Flow2
            except Exception:
                in_flow = self.aoFlows[0]  # Default to first flow if flows are unavailable

            if self.fTemperature < in_flow.fTemperature:
                self.fDeltaTemp = self.fTemperature - in_flow.fTemperature
                self.fTempChangeHeatFlow = (
                    in_flow.fFlowRate * in_flow.fSpecificHeatCapacity * self.fDeltaTemp
                )
            else:
                self.fTempChangeHeatFlow = 0

    def update_manual_solver(self):
        # Placeholder for manual solver update
        pass

    def solver_deltas(self, _):
        # Solver callback
        self.recalculate_condenser()
        return 0  # Delta pressure is always zero

    def update_thermal(self):
        # Update thermal calculations
        self.recalculate_condenser()

    def set_active(self, bActive, _=None):
        # Enable or disable active temperature regulation
        self.bActiveTemperatureRegulation = bActive

    def get_flows(self):
        """
        Placeholder for retrieving the flows. This method should return two
        flow objects (Flow1, Flow2) when implemented in a simulation context.
        """
        raise NotImplementedError("get_flows method should be implemented based on the simulation framework.")
