class CondenserTemperatureChange:
    def __init__(self, oMT, sName, oCondenser):
        self.oMT = oMT
        self.sName = sName
        self.oCondenser = oCondenser
        
        # Hydraulic properties
        self.fHydrDiam = 1  # Hydraulic diameter (irrelevant for manual solver)
        self.fHydrLength = 0  # Hydraulic length (irrelevant for manual solver)
        self.fDeltaTemp = 0  # Temperature difference created by the component in [K]
        self.fTemperature = None
        self.fHeatFlow = 0  # Heat flow in the condenser
        self.bActiveTemperatureRegulation = True
        
        # Initialize solver support
        self.support_solver('manual', True, self.update_manual_solver)
        self.support_solver('callback', self.solver_deltas)

    def support_solver(self, solver_type, is_active, callback):
        # Placeholder for solver support registration
        # Implement according to the solver framework being used
        pass

    def recalculate_condenser_temperature_change(self):
        if not self.bActiveTemperatureRegulation:
            self.fHeatFlow = 0
        else:
            try:
                # Retrieve flows
                Flow1, Flow2 = self.get_flows()

                if Flow1.fFlowRate > 0:
                    inFlow = Flow1
                else:
                    inFlow = Flow2
            except Exception:
                inFlow = self.aoFlows[0]  # Default to the first flow if error occurs

            # Calculate heat flow if the condenser's temperature is lower
            if self.oCondenser.fTemperature < inFlow.fTemperature:
                self.fDeltaTemp = self.oCondenser.fTemperature - inFlow.fTemperature
                self.fHeatFlow = inFlow.fFlowRate * inFlow.fSpecificHeatCapacity * self.fDeltaTemp
            else:
                self.fHeatFlow = 0

    def get_flows(self):
        # Placeholder for retrieving flows
        # Replace with actual logic to fetch Flow1 and Flow2
        pass

    def update_manual_solver(self):
        pass  # No implementation needed for manual solver update in this context

    def solver_deltas(self, *args):
        return 0  # No pressure difference in this component

    def update_thermal(self):
        self.recalculate_condenser_temperature_change()

    def set_active(self, bActive, *_):
        self.bActiveTemperatureRegulation = bActive
