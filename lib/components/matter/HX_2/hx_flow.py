class HXFlow:
    """
    HXFlow: A flow-to-flow processor to set the values for the outflows of a heat exchanger.
    """

    def __init__(self, oHXParent, oContainer, sName):
        """
        Initialize the HXFlow processor.
        
        Args:
            oHXParent: Reference to the parent heat exchanger object.
            oContainer: The container (store) where this processor resides.
            sName: Name of the processor.
        """
        self.oHXParent = oHXParent
        self.oContainer = oContainer
        self.sName = sName

        # Properties
        self.fFlowRate = 0
        self.fHeatFlow = 0
        self.fDeltaPressure = 0

        # Register solver support
        self.supported_solvers = {
            'callback': self.solver_deltas,
            'manual': self.update_manual_solver
        }

    def support_solver(self, solver_type, solver_method):
        """
        Register a solver for the HXFlow processor.

        Args:
            solver_type: Type of solver (e.g., 'callback', 'manual').
            solver_method: Method to handle the solver logic.
        """
        self.supported_solvers[solver_type] = solver_method

    def update(self):
        """
        Mark the thermal branch as outdated, prompting a recalculation.
        """
        self.oContainer.oThermalBranch.set_outdated()

    def update_thermal(self):
        """
        Trigger an update on the parent heat exchanger.
        """
        self.oHXParent.update()

    def solver_deltas(self, fFlowRate):
        """
        Handle solver updates for flow rate and delta pressure.

        Args:
            fFlowRate: Flow rate from the solver.

        Returns:
            fDeltaPressure: Calculated delta pressure.
        """
        # Setting the flow rate given by the solver
        self.fFlowRate = fFlowRate

        # Update the parent HX system
        self.oContainer.oThermalBranch.set_outdated()

        # Return the calculated delta pressure if flow rate is non-zero
        if fFlowRate != 0:
            return self.fDeltaPressure
        return 0

    def set_out_flow(self, fHeatFlow, fDeltaPressure):
        """
        Set the heat flow and delta pressure of the heat exchanger.

        Args:
            fHeatFlow: Heat flow to be set.
            fDeltaPressure: Delta pressure to be set.
        """
        self.fHeatFlow = fHeatFlow
        self.fDeltaPressure = fDeltaPressure

    def get_in_flow(self):
        """
        Retrieve the inflow object for this processor.

        Returns:
            oInFlow: The inflow object.
        """
        oInFlow, _ = self.get_flows()
        return oInFlow

    def get_flows(self):
        """
        Placeholder for retrieving flow information.

        Returns:
            Tuple containing inflow and outflow.
        """
        # Placeholder implementation; replace with actual flow retrieval logic
        return self.oContainer.oInFlow, self.oContainer.oOutFlow

    def update_manual_solver(self):
        """
        Update the processor manually, synchronizing flow rates.
        """
        self.fFlowRate = self.oContainer.fFlowRate

        # Update the parent HX system
        self.oContainer.oThermalBranch.set_outdated()
