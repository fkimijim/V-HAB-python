class Example(vsys):
    """
    Example simulation for a fan-driven looped gas flow in V-HAB 2.2.
    One tank filled with gas, a fan, and two pipes.
    """

    def __init__(self, oParent, sName):
        """
        Initializes the Example class.
        Calls the parent constructor with a specified execution interval.
        """
        super().__init__(oParent, sName, 100)

    def createMatterStructure(self):
        """
        Creates the matter structure for the simulation.
        """
        super().createMatterStructure()

        # Creating a store, volume 1 m^3
        matter.store(self, 'Tank_1', 1)

        # Adding a phase to the store 'Tank_1', 1 m^3 air
        oGasPhase = self.toStores.Tank_1.createPhase('air', 1)

        # Adding extract/merge processors to the phase
        matter.procs.exmes.gas(oGasPhase, 'Port_1')
        matter.procs.exmes.gas(oGasPhase, 'Port_2')

        # Adding a fan to move the gas
        components.matter.fan(self, 'Fan', 55000)

        # Adding pipes to connect components
        components.matter.pipe(self, 'Pipe_1', 1, 0.02)
        components.matter.pipe(self, 'Pipe_2', 1, 0.02)

        # Creating the flowpath (=branch) between the components
        # Format: 'store.exme', {'f2f-processor, 'f2fprocessor'}, 'store.exme'
        matter.branch(self, 'Tank_1.Port_1', ['Pipe_1', 'Fan', 'Pipe_2'], 'Tank_1.Port_2')

    def createSolverStructure(self):
        """
        Creates the solver structure for the simulation.
        """
        super().createSolverStructure()

        # Adding the branch to a specific solver
        solver.matter.interval.branch(self.toBranches.Tank_1__Port_1___Tank_1__Port_2)

        # Switch on the fan
        self.toProcsF2F.Fan.switchOn()

        # Set thermal solvers
        self.setThermalSolvers()

    def exec(self, _):
        """
        Execution function for this system.
        Adjusts the fan's speed based on simulation time.
        """
        super().exec()

        # Adjust the fan speed based on the simulation time
        oFan = self.toProcsF2F.Fan
        if 600 < self.oTimer.fTime < 1200:
            oFan.fSpeedSetpoint = 40000
        elif 1200 < self.oTimer.fTime < 1800:
            oFan.fSpeedSetpoint = 75000
        else:
            oFan.fSpeedSetpoint = 55000
