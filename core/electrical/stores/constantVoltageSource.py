from .. import store

store = store()

class constantVoltageSource(store):
    """
    Simple model of a constant voltage source.
    This model simplifies the creation of circuit diagrams containing
    voltage sources like power outlets or batteries.
    """

    def __init__(self, oCircuit, sName, sType, fVoltage):
        """
        Constructor for the constantVoltageSource class.

        Parameters:
        - oCircuit: Reference to the parent circuit.
        - sName: Name of the voltage source.
        - sType: Type of the voltage source ('AC' or 'DC').
        - fVoltage: Voltage value of the source.
        """
        # Call the parent constructor
        super().__init__(oCircuit, sName)

        # Set type and voltage properties
        self.sType = sType  # Type of electrical component ('AC' or 'DC')
        self.fVoltage = fVoltage  # Constant voltage of the source

        # Set the voltage on the terminals
        self.oPositiveTerminal.setVoltage(fVoltage)
        self.oNegativeTerminal.setVoltage(0)

    def calculateTimeStep(self):
        """
        Sets the default, fixed time step.
        """
        if self.hSetTimeStep:
            self.hSetTimeStep(self.fFixedTimeStep)

        # Set the time step property for information
        self.fTimeStep = self.fFixedTimeStep
