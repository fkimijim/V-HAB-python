class Example:
    """
    Example simulation using automatically generated ExMe processors.
    Two tanks filled with gas at different pressures and a pipe in between.
    This is the same setup as the simple_flow tutorial, but the ExMe processors
    on both phases are created automatically, reducing the number of lines of code.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example class.
        """
        self.oParent = oParent
        self.sName = sName
        self.simulation_time = 30  # Duration for the simulation in seconds
        self.fPressureDifference = 10 ** 5  # Pressure difference in Pa
        self.toStores = {}
        self.toBranches = {}
        self.oRoot = None  # Root object placeholder for configuration (optional)

        # Call the configuration if available
        if self.oRoot and hasattr(self.oRoot, "oCfgParams") and hasattr(self.oRoot.oCfgParams, "configCode"):
            eval(self.oRoot.oCfgParams.configCode(self))

    def create_matter_structure(self):
        """
        Create the matter structure for the simulation.
        """
        # Creating a store, volume 1 m^3
        self.toStores["Tank_1"] = {"volume": 1, "phase": self.create_phase("air", 1, 293.15)}

        # Creating a second store, volume 1 m^3
        self.toStores["Tank_2"] = {
            "volume": 1,
            "phase": self.create_phase("air", 1, 323.15, pressure=self.fPressureDifference + 10 ** 5),
        }

        # Adding a pipe to connect the tanks
        self.toStores["Pipe"] = {"length": 1.5, "diameter": 0.005}

        # Creating the flow path (branch) between the components
        self.toBranches["Branch"] = self.create_branch(
            self.toStores["Tank_1"]["phase"], self.toStores["Tank_2"]["phase"], ["Pipe"]
        )

    def create_phase(self, substance, volume, temperature, pressure=10 ** 5):
        """
        Create a phase with specified properties.
        """
        return {
            "substance": substance,
            "volume": volume,
            "temperature": temperature,
            "pressure": pressure,
        }

    def create_branch(self, left_phase, right_phase, components):
        """
        Create a branch connecting two phases.
        """
        return {
            "left_phase": left_phase,
            "right_phase": right_phase,
            "components": components,
        }

    def create_thermal_structure(self):
        """
        Create the thermal structure for the simulation.
        """
        # This is where thermal connections or configurations would be set up
        pass

    def create_solver_structure(self):
        """
        Create the solver structure for the simulation.
        """
        # Assign the branch to a solver
        self.toBranches["Branch"]["solver"] = "iterative"

        # Set thermal solvers if needed
        self.set_thermal_solvers()

    def set_thermal_solvers(self):
        """
        Set thermal solvers for the system.
        """
        # Placeholder for thermal solver setup
        pass

    def exec(self):
        """
        Execute the system's operations.
        """
        # Placeholder for the system's execution logic
        print(f"Executing system: {self.sName}")

        # Debug output (if applicable)
        if hasattr(self, "debug") and not self.debug.get("bOff", True):
            print(f"Debug: Exec system {self.sName}")


# Example usage
if __name__ == "__main__":
    example_sim = Example(oParent=None, sName="ExampleSimulation")
    example_sim.create_matter_structure()
    example_sim.create_thermal_structure()
    example_sim.create_solver_structure()
    example_sim.exec()
