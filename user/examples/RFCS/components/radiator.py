class Radiator:
    """
    Radiator class representing a heat exchange process in a thermal system.
    """

    def __init__(self, oMT, sName, fArea, fEmissivity):
        """
        Initializes the radiator object.

        :param oMT: Reference to the matter table or system.
        :param sName: Name of the radiator.
        :param fArea: Radiator surface area [m^2].
        :param fEmissivity: Radiator emissivity [-].
        """
        self.oMT = oMT
        self.sName = sName
        self.fArea = fArea
        self.fEmissivity = fEmissivity
        self.bActive = True
        self.fHeatFlow = 0.0

        # Manual solver setup
        self.support_solver('manual', True, self.update_manual_solver)

    def support_solver(self, solver_type, active, update_function):
        """
        Placeholder for registering solvers.
        """
        self.solver_type = solver_type
        self.solver_active = active
        self.update_function = update_function

    def get_flows(self):
        """
        Retrieves the flow objects associated with the radiator.
        This is a placeholder for MATLAB's getFlows() method.

        :return: Two flow objects (Flow1, Flow2).
        """
        return self.oMT.get_flows(self.sName)

    def update_manual_solver(self):
        """
        Updates the manual solver, calculating heat flow based on the Stefan-Boltzmann law.
        """
        try:
            Flow1, Flow2 = self.get_flows()

            if Flow1['fFlowRate'] > 0:
                in_flow = Flow1
            else:
                in_flow = Flow2
        except Exception:
            in_flow = self.oMT.get_flow(self.sName)

        # Stefan-Boltzmann law calculation for heat radiation
        self.fHeatFlow = (
            -self.oMT.Const['fStefanBoltzmann']
            * in_flow['fTemperature']**4
            * self.fArea
            * self.fEmissivity
        )

    def set_active(self, bActive):
        """
        Activates or deactivates the radiator.

        :param bActive: Boolean indicating if the radiator is active.
        """
        self.bActive = bActive


# Supporting classes or mock for oMT
class MatterTable:
    """
    Mock class for the matter table or system containing constants and flows.
    """
    def __init__(self):
        self.Const = {
            'fStefanBoltzmann': 5.67e-8  # Stefan-Boltzmann constant [W/m^2K^4]
        }
        self.flows = {}

    def get_flows(self, sName):
        """
        Mock method to get flows by name.
        """
        # Replace with actual logic for retrieving flows.
        return self.flows.get(sName, [{'fFlowRate': 0, 'fTemperature': 300}, {'fFlowRate': 0, 'fTemperature': 300}])

    def get_flow(self, sName):
        """
        Mock method to get a single flow by name.
        """
        # Replace with actual logic for retrieving a single flow.
        return {'fFlowRate': 0, 'fTemperature': 300}
