class CondenserCounterpart:
    def __init__(self, oMT, sName, oCondenser, oCondenserP2P):
        self.oMT = oMT
        self.sName = sName
        self.fHydrDiam = 1  # Hydraulic diameter value (irrelevant for manual solver)
        self.fHydrLength = 0  # Hydraulic length (irrelevant for manual solver)
        self.bActiveTemperatureRegulation = True
        self.oCondenser = oCondenser
        self.oCondenserP2P = oCondenserP2P

        # Solver support (manual and callback)
        self.support_solver_manual = self.update_manual_solver
        self.support_solver_callback = self.solver_deltas

    def update_manual_solver(self):
        # Placeholder for manual solver update
        pass

    def solver_deltas(self, *_):
        # Solver callback
        return 0  # Delta pressure is always zero

    def update_thermal(self):
        # Calculate the heat flow, including latent heat of condensation
        self.fHeatFlow = (
            -self.oCondenser.fTempChangeHeatFlow + 2.2564e6 * self.oCondenserP2P.fFlowRate
        )

    def set_active(self, bActive, _=None):
        # Enable or disable active temperature regulation
        self.bActiveTemperatureRegulation = bActive
