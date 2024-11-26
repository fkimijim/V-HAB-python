class Example:
    """
    Example simulation for a simple flow solved by the equalizer solver.
    Two tanks filled with gas at different temperatures and pressures with a pipe in between.
    """
    def __init__(self, oParent, sName):
        """
        Initializes the Example system.
        """
        self.oParent = oParent
        self.sName = sName
        self.simulation_time = 30
        self.toStores = {}
        self.toBranches = {}

    def createMatterStructure(self):
        """
        Creates the matter structure of the simulation.
        """
        self.toStores['Tank_1'] = self.createStore('Tank_1', 1)
        oGasPhase = self.toStores['Tank_1'].createPhase('air', 1, 293.15)

        self.toStores['Tank_2'] = self.createStore('Tank_2', 1)
        oAirPhase = self.toStores['Tank_2'].createPhase('air', 'boundary', 1, 323.15, 0.5, 2e5)

        self.toBranches['Pipe'] = self.createPipe('Pipe', 1.5, 0.005)
        self.toBranches['Branch'] = self.createBranch(oGasPhase, ['Pipe'], oAirPhase)

    def createSolverStructure(self):
        """
        Creates the solver structure for the simulation.
        """
        self.toBranches['Branch'].assignEqualizerSolver(0.1, 2e5)
        self.setThermalSolvers()

    def exec(self):
        """
        Executes the system's operations.
        """
        pass  # Add execution logic as needed

    def createStore(self, name, volume):
        """
        Creates a store for the simulation.
        """
        return Store(name, volume)

    def createPipe(self, name, length, diameter):
        """
        Creates a pipe for the simulation.
        """
        return Pipe(name, length, diameter)

    def createBranch(self, phase_start, components, phase_end):
        """
        Creates a branch connecting two phases with components in between.
        """
        return Branch(phase_start, components, phase_end)

    def setThermalSolvers(self):
        """
        Sets the thermal solvers for the simulation.
        """
        print("Thermal solvers set.")


class Store:
    """
    Represents a storage unit in the simulation.
    """
    def __init__(self, name, volume):
        self.name = name
        self.volume = volume
        self.phases = {}

    def createPhase(self, substance, *args):
        """
        Creates a phase within the store.
        """
        phase = Phase(substance, *args)
        self.phases[substance] = phase
        return phase


class Pipe:
    """
    Represents a pipe in the simulation.
    """
    def __init__(self, name, length, diameter):
        self.name = name
        self.length = length
        self.diameter = diameter


class Branch:
    """
    Represents a branch connecting two phases in the simulation.
    """
    def __init__(self, phase_start, components, phase_end):
        self.phase_start = phase_start
        self.components = components
        self.phase_end = phase_end

    def assignEqualizerSolver(self, parameter1, parameter2):
        """
        Assigns an equalizer solver to this branch.
        """
        print(f"Equalizer solver assigned with parameters {parameter1}, {parameter2}.")


class Phase:
    """
    Represents a phase in the simulation.
    """
    def __init__(self, substance, *args):
        self.substance = substance
        self.parameters = args
