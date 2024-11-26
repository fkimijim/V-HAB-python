class Example(vsys):
    """
    Example simulation for a simple flow in V-HAB 2.0.
    Two tanks filled with gas at different temperatures and pressures
    with a pipe in between.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example class.

        :param oParent: Parent object
        :param sName: Name of the system
        """
        # Call the parent constructor
        # Third parameter (30) defines the interval for .exec() in seconds
        super().__init__(oParent, sName, 30)

    def create_matter_structure(self):
        """
        Creates all simulation objects in the matter domain.
        """
        # Call the parent class's create_matter_structure() method
        super().create_matter_structure()

        # Creating a store, volume 1 m^3
        matter.store(self, 'Tank_1', 1)

        # Adding a phase to the store 'Tank_1', 1 m^3 air at 20 deg C
        oGasPhase = self.toStores.Tank_1.create_phase('air', 1, 293.15)

        # Creating a second store, volume 1 m^3
        matter.store(self, 'Tank_2', 1)

        # Adding a phase to the store 'Tank_2', 1 m^3 air at 50 deg C,
        # relative humidity of 50% and at a pressure of 2e5 Pa
        oAirPhase = self.toStores.Tank_2.create_phase('air', 1, 323.15, 0.5, 2e5)

        # Adding a pipe to connect the tanks, 1.5 m long, 5 mm in diameter
        # Pipe is derived from the flow-to-flow (f2f) processor class
        components.matter.pipe(self, 'Pipe', 1.5, 0.005)

        # Creating the flowpath (branch) between the components
        matter.branch(self, oGasPhase, ['Pipe'], oAirPhase, 'Branch')

    def create_thermal_structure(self):
        """
        Creates all simulation objects in the thermal domain.
        """
        # Call the parent class's create_thermal_structure() method
        super().create_thermal_structure()

        # No additional objects are needed for this simple model.
        # All thermal domain objects related to advective heat transfer
        # will be automatically created by setThermalSolvers().

    def create_solver_structure(self):
        """
        Creates all of the solver objects required for a simulation.
        """
        # Call the parent class's create_solver_structure() method
        super().create_solver_structure()

        # Creating an interval solver object for the branch flow rate
        solver.matter.interval.branch(self.toBranches.Branch)

        # Set up thermal solvers to calculate temperature changes
        self.set_thermal_solvers()

    def exec(self, _):
        """
        Execute function for this system.

        Can be used to change the system state, e.g., close valves
        or switch on/off components.
        """
        # Call the parent class's exec() method
        super().exec()
