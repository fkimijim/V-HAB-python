class Example:
    """
    Example simulation for a simple flow in V-HAB 2.0.
    Two tanks filled with gas at different temperatures and pressures
    with a pipe in between.
    """

    def __init__(self, parent, name):
        """
        Constructor for the Example system.
        """
        self.parent = parent
        self.name = name
        self.bSetNewBoundary = False
        self.timer_interval = 30  # Interval in seconds for .exec()
        self.toStores = {}
        self.toBranches = {}
        self.oTimer = Timer()  # Mock timer object
        self.create_matter_structure()
        self.create_thermal_structure()
        self.create_solver_structure()

    def create_matter_structure(self):
        """
        Creates all simulation objects in the matter domain.
        """
        # Creating Tank_1 with an infinite volume
        self.toStores["Tank_1"] = Store("Tank_1", float("inf"))
        oGasPhase = self.toStores["Tank_1"].create_phase("air", "boundary", 1, 293.15)

        # Creating Tank_2 with an infinite volume
        self.toStores["Tank_2"] = Store("Tank_2", float("inf"))
        oAirPhase = self.toStores["Tank_2"].create_phase("air", "boundary", 1, 323.15, 2e5)

        # Adding a pipe to connect the tanks
        self.toBranches["Branch"] = Branch(oGasPhase, ["Pipe"], oAirPhase, "Branch")

        # Creating InletTank with a volume of 100 m^3
        self.toStores["InletTank"] = Store("InletTank", 100)
        oInletPhase = self.toStores["InletTank"].create_phase("water", "boundary", 100, 288.15)

        # Creating OutletTank with a volume of 100 m^3
        self.toStores["OutletTank"] = Store("OutletTank", 100)
        oOutletPhase = self.toStores["OutletTank"].create_phase("water", "boundary", 100, 293.15)

        # Adding another pipe and branch
        self.toBranches["WaterBranch"] = Branch(oInletPhase, ["Pipe2"], oOutletPhase, "WaterBranch")

    def create_thermal_structure(self):
        """
        Creates all simulation objects in the thermal domain.
        """
        # In this example, no additional thermal domain objects are created.
        pass

    def create_solver_structure(self):
        """
        Creates all solver objects required for the simulation.
        """
        # Creating an interval solver for the main branch
        IntervalSolver(self.toBranches["Branch"])

        # Creating a manual solver for the water branch and setting its flow rate
        manual_solver = ManualSolver(self.toBranches["WaterBranch"])
        manual_solver.set_flow_rate(0.002)

        # Setting thermal solvers
        self.set_thermal_solvers()

    def set_thermal_solvers(self):
        """
        Configures the thermal solvers for the simulation.
        """
        print("Thermal solvers configured.")

    def exec(self):
        """
        Execute function for this system.
        Can be used to change the system state, e.g., close valves or switch on/off components.
        """
        if self.oTimer.time > 600 and not self.bSetNewBoundary:
            tProperties = {
                "fPressure": 2e5,
                "afMass": [1 if i == "N2" else 0 for i in range(self.parent.get_substances_count())],
            }
            self.toStores["Tank_1"].phases[0].set_boundary_properties(tProperties)

            tProperties["fPressure"] = 1e5
            self.toStores["Tank_2"].phases[0].set_boundary_properties(tProperties)

            self.bSetNewBoundary = True


# Supporting Classes (Mock implementations for Store, Phase, Branch, Timer, etc.)
class Store:
    def __init__(self, name, volume):
        self.name = name
        self.volume = volume
        self.phases = []

    def create_phase(self, substance, boundary, volume, temperature, pressure=None):
        phase = Phase(substance, boundary, volume, temperature, pressure)
        self.phases.append(phase)
        return phase


class Phase:
    def __init__(self, substance, boundary, volume, temperature, pressure=None):
        self.substance = substance
        self.boundary = boundary
        self.volume = volume
        self.temperature = temperature
        self.pressure = pressure

    def set_boundary_properties(self, properties):
        self.pressure = properties["fPressure"]
        self.mass = properties["afMass"]


class Branch:
    def __init__(self, phase_start, pipes, phase_end, name):
        self.phase_start = phase_start
        self.pipes = pipes
        self.phase_end = phase_end
        self.name = name


class IntervalSolver:
    def __init__(self, branch):
        print(f"Interval solver initialized for branch {branch.name}")


class ManualSolver:
    def __init__(self, branch):
        self.branch = branch

    def set_flow_rate(self, rate):
        print(f"Flow rate set to {rate} for branch {self.branch.name}")


class Timer:
    def __init__(self):
        self.time = 0  # Simulated time
