class Example3(vsys):
    """
    Example simulation for a simple flow in V-HAB 2.0.
    Two tanks filled with gas at different pressures and a pipe in between.
    """

    def __init__(self, oParent, sName):
        """
        Constructor for the Example3 class.
        """
        # Call parent constructor with a 30-second interval for .exec() method
        super().__init__(oParent, sName, 30)

        # Make the system configurable
        eval(self.oRoot.oCfgParams.configCode(self))

        # Pipe parameters
        self.fPipeLength = 1.5
        self.fPipeDiameter = 0.05

    def createMatterStructure(self):
        """
        Creates the matter structure for the system.
        """
        super().createMatterStructure()

        # Creating a store, volume 1 m^3
        matter.store(self, 'Tank_1', 1)
        oGasPhase = self.toStores.Tank_1.createPhase(
            'gas', 'CabinAir', self.toStores.Tank_1.fVolume,
            {'N2': 16e4, 'O2': 4e4, 'CO2': 1000}, 293, 0.5
        )
        matter.procs.exmes.gas(oGasPhase, 'Port_1')
        matter.procs.exmes.gas(oGasPhase, 'Port_2')

        # Creating a second store, volume 1 m^3
        matter.store(self, 'Tank_2', 1)
        oGasPhase = self.toStores.Tank_2.createPhase(
            'gas', 'CabinAir', self.toStores.Tank_1.fVolume,
            {'N2': 8e4, 'O2': 2e4, 'CO2': 500}, 293, 0.5
        )
        matter.procs.exmes.gas(oGasPhase, 'Port_1')
        matter.procs.exmes.gas(oGasPhase, 'Port_2')

        # Creating flow stores
        for i in range(1, 4):
            store_name = f'Flow_{i}'
            matter.store(self, store_name, 1e-5)
            oGasPhase = self.toStores[store_name].createPhase(
                'gas', 'flow', 'FlowPhase', self.toStores[store_name].fVolume,
                {'N2': 8e4, 'O2': 2e4, 'CO2': 500}, 293, 0.5
            )
            matter.procs.exmes.gas(oGasPhase, 'Port_1')
            matter.procs.exmes.gas(oGasPhase, 'Port_2')

        # Adding pipes to connect the tanks, each 1.5 m long and 5 cm in diameter
        for i in range(1, 5):
            components.matter.pipe(self, f'Pipe{i}', self.fPipeLength, self.fPipeDiameter, 2e-3)

        # Adding a fan
        components.matter.fan_simple(self, 'Fan1', 0.5 * 10**5)

        # Creating the flowpath (branches) between components
        matter.branch(self, 'Tank_1.Port_1', ['Pipe1'], 'Flow_1.Port_1', 'Branch1')
        matter.branch(self, 'Flow_1.Port_2', ['Pipe2'], 'Tank_2.Port_1', 'Branch2')
        matter.branch(self, 'Tank_2.Port_2', ['Pipe3'], 'Flow_2.Port_1', 'Branch3')
        matter.branch(self, 'Flow_2.Port_2', ['Fan1'], 'Flow_3.Port_1', 'Branch4')
        matter.branch(self, 'Flow_3.Port_2', ['Pipe4'], 'Tank_1.Port_2', 'Branch5')

    def createSolverStructure(self):
        """
        Creates the solver structure for the system.
        """
        super().createSolverStructure()

        # Using iterative solver for branches
        solver.matter_multibranch.iterative.branch(self.aoBranches[:], 'complex')

        # Setting time step properties for Tank phases
        tTimeStepProperties = {'rMaxChange': 0.001}
        self.toStores.Tank_1.toPhases.CabinAir.setTimeStepProperties(tTimeStepProperties)
        self.toStores.Tank_2.toPhases.CabinAir.setTimeStepProperties(tTimeStepProperties)

        self.setThermalSolvers()

    def exec(self, *args):
        """
        Exec function for this system. Called at each simulation step.
        """
        super().exec(*args)

        if not base.oDebug.bOff:
            self.out(2, 1, 'exec', f'Exec vsys {self.sName}')
